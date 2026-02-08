"""Moshi Agent API — HTTP/WebSocket API layer for Super-Goose integration.

Provides a REST + WebSocket API that Super-Goose (or any external system)
can use to interact with the Moshi voice AI autonomously. This is the
top-level orchestrator that ties together MoshiServerManager and MoshiAgent.

Endpoints:
    GET  /api/voice/status     — Agent and server status
    GET  /api/voice/stats      — Runtime statistics
    POST /api/voice/connect    — Connect agent to Moshi server
    POST /api/voice/disconnect — Disconnect agent
    POST /api/voice/reconnect  — Force reconnect (reset KV cache)
    POST /api/voice/audio      — Send PCM audio (base64 encoded)
    WS   /api/voice/stream     — Bidirectional audio streaming
    POST /api/voice/start      — Start server + connect agent
    POST /api/voice/stop       — Stop everything

Architecture:
    Super-Goose -> AgentAPI -> MoshiAgent -> [WebSocket] -> MoshiServer
                            -> MoshiServerManager -> [subprocess] -> moshi.server
"""

import asyncio
import base64
import json
import logging
import time
from dataclasses import asdict
from typing import Optional

import numpy as np

try:
    from aiohttp import web
except ImportError:
    web = None

from .moshi_agent import MoshiAgent, AgentConfig, AgentState
from .server_manager import MoshiServerManager, ServerManagerConfig, ServerStatus

logger = logging.getLogger(__name__)

SAMPLE_RATE = 24000


class MoshiAgentAPI:
    """HTTP/WebSocket API for autonomous Moshi voice interaction.

    Usage:
        api = MoshiAgentAPI()
        await api.start_all()      # starts server, waits for model, connects agent
        ...
        await api.stop_all()

    Or run as standalone HTTP server:
        api = MoshiAgentAPI()
        api.run(host="0.0.0.0", port=8999)
    """

    def __init__(
        self,
        server_config: Optional[ServerManagerConfig] = None,
        agent_config: Optional[AgentConfig] = None,
        api_port: int = 8999,
    ):
        if web is None:
            raise ImportError("aiohttp is required: pip install aiohttp")

        self.api_port = api_port
        self.server_manager = MoshiServerManager(
            config=server_config,
            on_status_change=self._on_server_status_change,
        )
        self.agent = MoshiAgent(config=agent_config)
        self.agent.on_audio_received = self._on_audio_received
        self.agent.on_text_received = self._on_text_received
        self.agent.on_state_change = self._on_agent_state_change

        # WebSocket clients subscribed to audio/text streams
        self._stream_clients: list[web.WebSocketResponse] = []
        self._text_buffer: list[str] = []
        self._text_buffer_max = 200

    async def start_all(self, wait_ready: bool = True) -> bool:
        """Start the Moshi server and connect the agent.

        Args:
            wait_ready: If True, waits for the model to finish loading.

        Returns:
            True if everything is ready.
        """
        logger.info("Starting full Moshi agentic stack...")

        # Start server
        await self.server_manager.start()

        if wait_ready:
            logger.info("Waiting for Moshi server to load model (up to 5 min)...")
            ready = await self.server_manager.wait_ready(timeout=300)
            if not ready:
                logger.error("Server did not become ready")
                return False

        # Connect agent
        await asyncio.sleep(1)  # brief pause after server ready
        success = await self.agent.connect()
        if not success:
            logger.error("Agent failed to connect to server")
            return False

        logger.info("Full agentic stack is running")
        return True

    async def stop_all(self) -> None:
        """Stop the agent and server."""
        logger.info("Stopping full Moshi agentic stack...")
        await self.agent.disconnect()
        await self.server_manager.stop()
        logger.info("Agentic stack stopped")

    def get_status(self) -> dict:
        """Get combined status of server and agent."""
        return {
            "server": {
                "status": self.server_manager.status.value,
                "url": self.server_manager.url,
                "ws_url": self.server_manager.ws_url,
            },
            "agent": {
                "state": self.agent.state.value,
                "is_connected": self.agent.is_connected,
                "stats": {
                    "total_audio_sent": self.agent.stats.total_audio_sent,
                    "total_audio_received": self.agent.stats.total_audio_received,
                    "total_text_tokens": self.agent.stats.total_text_tokens,
                    "reconnect_count": self.agent.stats.reconnect_count,
                    "current_latency_ms": round(self.agent.stats.current_latency_ms, 1),
                    "avg_latency_ms": round(self.agent.stats.avg_latency_ms, 1),
                },
            },
            "recent_text": self._text_buffer[-20:],
        }

    # ── HTTP Route Handlers ──────────────────────────────────────

    async def handle_status(self, request: web.Request) -> web.Response:
        return web.json_response(self.get_status())

    async def handle_connect(self, request: web.Request) -> web.Response:
        success = await self.agent.connect()
        return web.json_response({"success": success, "state": self.agent.state.value})

    async def handle_disconnect(self, request: web.Request) -> web.Response:
        await self.agent.disconnect()
        return web.json_response({"success": True, "state": self.agent.state.value})

    async def handle_reconnect(self, request: web.Request) -> web.Response:
        """Force reconnect to reset KV cache and restore low latency."""
        await self.agent.disconnect()
        await asyncio.sleep(0.5)
        success = await self.agent.connect()
        return web.json_response({"success": success, "state": self.agent.state.value})

    async def handle_send_audio(self, request: web.Request) -> web.Response:
        """Receive base64-encoded PCM audio and send to Moshi."""
        try:
            data = await request.json()
            pcm_b64 = data.get("audio")
            if not pcm_b64:
                return web.json_response({"error": "Missing 'audio' field"}, status=400)

            pcm_bytes = base64.b64decode(pcm_b64)
            pcm = np.frombuffer(pcm_bytes, dtype=np.float32)
            await self.agent.send_audio(pcm)

            return web.json_response({
                "success": True,
                "samples_sent": len(pcm),
                "duration_ms": len(pcm) / SAMPLE_RATE * 1000,
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_start(self, request: web.Request) -> web.Response:
        """Start server + connect agent (full stack startup)."""
        success = await self.start_all()
        return web.json_response({"success": success, **self.get_status()})

    async def handle_stop(self, request: web.Request) -> web.Response:
        """Stop everything."""
        await self.stop_all()
        return web.json_response({"success": True})

    async def handle_stream(self, request: web.Request) -> web.WebSocketResponse:
        """WebSocket endpoint for bidirectional audio streaming.

        Client sends: binary frames of float32 PCM audio (24kHz mono)
        Server sends: JSON messages with type "audio" (base64 PCM) or "text"
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._stream_clients.append(ws)
        logger.info(f"Stream client connected ({len(self._stream_clients)} total)")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.BINARY:
                    pcm = np.frombuffer(msg.data, dtype=np.float32)
                    await self.agent.send_audio(pcm)
                elif msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        cmd = data.get("command")
                        if cmd == "reconnect":
                            await self.agent.disconnect()
                            await asyncio.sleep(0.5)
                            await self.agent.connect()
                        elif cmd == "status":
                            await ws.send_json(self.get_status())
                        elif cmd == "silence":
                            duration = data.get("duration_ms", 80)
                            await self.agent.send_silence(duration)
                    except json.JSONDecodeError:
                        pass
                elif msg.type in (web.WSMsgType.ERROR, web.WSMsgType.CLOSED):
                    break
        finally:
            self._stream_clients.remove(ws)
            logger.info(f"Stream client disconnected ({len(self._stream_clients)} total)")

        return ws

    # ── Callbacks ────────────────────────────────────────────────

    async def _on_audio_received(self, pcm: np.ndarray) -> None:
        """Forward received audio to all stream clients (non-blocking)."""
        if not self._stream_clients:
            return

        audio_b64 = base64.b64encode(pcm.astype(np.float32).tobytes()).decode()
        msg = json.dumps({"type": "audio", "data": audio_b64, "samples": len(pcm)})
        asyncio.create_task(self._broadcast(msg))

    async def _on_text_received(self, text: str) -> None:
        """Forward received text to all stream clients and buffer."""
        self._text_buffer.append(text)
        if len(self._text_buffer) > self._text_buffer_max:
            self._text_buffer = self._text_buffer[-self._text_buffer_max:]

        if not self._stream_clients:
            return

        msg = json.dumps({"type": "text", "data": text})
        asyncio.create_task(self._broadcast(msg))

    async def _broadcast(self, msg: str) -> None:
        """Send a message to all connected stream clients without blocking the caller."""
        for ws in list(self._stream_clients):
            try:
                if not ws.closed:
                    await ws.send_str(msg)
            except Exception:
                pass

    def _on_server_status_change(self, status: ServerStatus) -> None:
        """Log server status changes."""
        logger.info(f"Server status changed: {status.value}")

    def _on_agent_state_change(self, state: AgentState) -> None:
        """Log agent state changes."""
        logger.info(f"Agent state changed: {state.value}")

    # ── App Builder & Runner ────────────────────────────────────

    def build_app(self) -> web.Application:
        """Build the aiohttp web application with all routes."""
        app = web.Application()
        app.router.add_get("/api/voice/status", self.handle_status)
        app.router.add_post("/api/voice/connect", self.handle_connect)
        app.router.add_post("/api/voice/disconnect", self.handle_disconnect)
        app.router.add_post("/api/voice/reconnect", self.handle_reconnect)
        app.router.add_post("/api/voice/audio", self.handle_send_audio)
        app.router.add_post("/api/voice/start", self.handle_start)
        app.router.add_post("/api/voice/stop", self.handle_stop)
        app.router.add_get("/api/voice/stream", self.handle_stream)
        return app

    def run(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Run the API server (blocking)."""
        port = port or self.api_port
        app = self.build_app()
        logger.info(f"Starting Moshi Agent API on http://{host}:{port}")
        web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Moshi Agent API Server")
    parser.add_argument("--api-port", type=int, default=8999, help="API server port")
    parser.add_argument("--moshi-port", type=int, default=8998, help="Moshi server port")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start Moshi server")
    args = parser.parse_args()

    server_cfg = ServerManagerConfig(port=args.moshi_port)
    agent_cfg = AgentConfig(server_ws_url=f"ws://localhost:{args.moshi_port}/api/chat")
    api = MoshiAgentAPI(server_config=server_cfg, agent_config=agent_cfg, api_port=args.api_port)

    if args.auto_start:
        async def _auto_start():
            await api.start_all()
        asyncio.run(_auto_start())

    api.run(port=args.api_port)
