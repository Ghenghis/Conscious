"""Moshi Agent — Autonomous WebSocket client for the Moshi voice AI server.

Replaces the browser-based UI entirely. Connects to the Moshi server via
WebSocket, streams audio bidirectionally, monitors latency, and auto-reconnects
when performance degrades (resetting the server's KV cache).

Protocol (reverse-engineered from moshi/server.py):
    - Server sends 0x00 as handshake after WS connect
    - 0x01 + opus_bytes = audio data (bidirectional)
    - 0x02 + utf8_text = text token (server -> client)

Features:
    - Fully autonomous operation (no browser needed)
    - Latency monitoring with configurable threshold
    - Auto-reconnect to reset KV cache when latency degrades
    - Exponential backoff on connection failures
    - Audio I/O abstracted via callbacks (pluggable for Super-Goose)
    - Text token streaming for real-time transcription
"""

import asyncio
import logging
import struct
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Callable, Optional

import numpy as np

try:
    import sphn
except ImportError:
    sphn = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)

# Moshi WebSocket message types
MSG_HANDSHAKE = 0x00
MSG_AUDIO = 0x01
MSG_TEXT = 0x02

SAMPLE_RATE = 24000


class AgentState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    HANDSHAKE = "handshake"
    STREAMING = "streaming"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for the Moshi agent."""
    server_ws_url: str = "ws://localhost:8998/api/chat"
    sample_rate: int = SAMPLE_RATE
    latency_threshold_ms: float = 2500.0
    latency_check_window: int = 10
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_backoff_base: float = 1.5
    reconnect_backoff_max: float = 30.0
    audio_send_interval_ms: float = 80.0
    silence_frame_size: int = 1920


@dataclass
class AgentStats:
    """Runtime statistics for the agent."""
    total_audio_sent: int = 0
    total_audio_received: int = 0
    total_text_tokens: int = 0
    reconnect_count: int = 0
    current_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    session_start: float = 0.0
    last_audio_sent: float = 0.0
    last_audio_received: float = 0.0


class MoshiAgent:
    """Autonomous WebSocket client for the Moshi voice server.

    Usage:
        agent = MoshiAgent()

        # Set callbacks for received audio/text
        agent.on_audio_received = my_audio_handler    # async fn(pcm: np.ndarray)
        agent.on_text_received = my_text_handler      # async fn(text: str)

        await agent.connect()

        # Send audio frames (from mic, file, or Super-Goose pipeline)
        await agent.send_audio(pcm_data)  # np.ndarray float32 mono 24kHz

        # Or send silence to keep connection alive while listening
        await agent.send_silence()

        await agent.disconnect()

    Auto-reconnect:
        When latency exceeds the threshold, the agent automatically
        disconnects and reconnects, resetting the server's KV cache.
        This restores instant response times.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        if aiohttp is None:
            raise ImportError("aiohttp is required: pip install aiohttp")
        if sphn is None:
            raise ImportError("sphn is required: pip install moshi (includes sphn)")

        self.config = config or AgentConfig()
        self._state = AgentState.DISCONNECTED
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._opus_writer: Optional[sphn.OpusStreamWriter] = None
        self._opus_reader: Optional[sphn.OpusStreamReader] = None
        self._stats = AgentStats()
        self._latency_history: deque = deque(maxlen=self.config.latency_check_window)
        self._reconnect_count = 0
        self._stop_event = asyncio.Event()
        self._recv_task: Optional[asyncio.Task] = None
        self._latency_task: Optional[asyncio.Task] = None

        # Pluggable callbacks — set these for Super-Goose integration
        self.on_audio_received: Optional[Callable] = None
        self.on_text_received: Optional[Callable] = None
        self.on_state_change: Optional[Callable] = None

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def stats(self) -> AgentStats:
        return self._stats

    @property
    def is_connected(self) -> bool:
        return self._state == AgentState.STREAMING

    def _set_state(self, state: AgentState) -> None:
        old = self._state
        self._state = state
        if old != state:
            logger.info(f"Agent state: {old.value} -> {state.value}")
            if self.on_state_change:
                try:
                    self.on_state_change(state)
                except Exception as e:
                    logger.error(f"State change callback error: {e}")

    async def connect(self) -> bool:
        """Connect to the Moshi server WebSocket.

        Returns:
            True if connected and handshake completed successfully.
        """
        if self._state == AgentState.STREAMING:
            logger.warning("Already connected")
            return True

        self._set_state(AgentState.CONNECTING)
        self._stop_event.clear()

        try:
            self._session = aiohttp.ClientSession()
            self._ws = await self._session.ws_connect(
                self.config.server_ws_url,
                timeout=aiohttp.ClientTimeout(total=30)
            )

            # Wait for handshake byte (0x00) from server
            self._set_state(AgentState.HANDSHAKE)
            msg = await asyncio.wait_for(self._ws.receive(), timeout=10.0)
            if msg.type != aiohttp.WSMsgType.BINARY or msg.data != b"\x00":
                logger.error(f"Invalid handshake: {msg}")
                await self._cleanup()
                self._set_state(AgentState.ERROR)
                return False

            # Initialize opus codec
            self._opus_writer = sphn.OpusStreamWriter(self.config.sample_rate)
            self._opus_reader = sphn.OpusStreamReader(self.config.sample_rate)

            # Reset stats for new session
            self._stats.session_start = time.time()
            self._latency_history.clear()

            self._set_state(AgentState.STREAMING)

            # Start background receive loop
            self._recv_task = asyncio.create_task(self._receive_loop())

            # Start latency monitor
            if self.config.auto_reconnect:
                self._latency_task = asyncio.create_task(self._latency_monitor())

            self._reconnect_count = 0
            logger.info(f"Connected to {self.config.server_ws_url}")
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            await self._cleanup()
            self._set_state(AgentState.ERROR)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the server."""
        self._stop_event.set()

        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass

        if self._latency_task and not self._latency_task.done():
            self._latency_task.cancel()
            try:
                await self._latency_task
            except asyncio.CancelledError:
                pass

        await self._cleanup()
        self._set_state(AgentState.DISCONNECTED)
        logger.info("Disconnected from server")

    async def send_audio(self, pcm: np.ndarray) -> None:
        """Send PCM audio to the server.

        Args:
            pcm: Float32 mono audio at 24kHz. Any length.
        """
        if self._state != AgentState.STREAMING or self._ws is None:
            return

        try:
            opus_bytes = self._opus_writer.append_pcm(pcm.astype(np.float32))
            if len(opus_bytes) > 0:
                await self._ws.send_bytes(bytes([MSG_AUDIO]) + opus_bytes)
                self._stats.total_audio_sent += len(pcm)
                self._stats.last_audio_sent = time.time()
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            if self.config.auto_reconnect:
                await self._auto_reconnect()

    async def send_silence(self, duration_ms: float = 80.0) -> None:
        """Send a silence frame to keep the connection alive.

        Args:
            duration_ms: Duration of silence in milliseconds.
        """
        samples = int(self.config.sample_rate * duration_ms / 1000)
        silence = np.zeros(samples, dtype=np.float32)
        await self.send_audio(silence)

    async def run_autonomous(self, audio_source: Optional[AsyncIterator] = None) -> None:
        """Run the agent autonomously, sending audio from a source.

        If no audio_source is provided, sends silence frames to keep
        the connection alive (listen-only mode).

        Args:
            audio_source: Async iterator yielding np.ndarray PCM frames.
                         Each frame should be float32 mono 24kHz.
        """
        if not await self.connect():
            logger.error("Failed to connect. Cannot run autonomously.")
            return

        try:
            if audio_source:
                async for frame in audio_source:
                    if self._stop_event.is_set():
                        break
                    await self.send_audio(frame)
                    await asyncio.sleep(self.config.audio_send_interval_ms / 1000)
            else:
                # Listen-only: send silence periodically
                while not self._stop_event.is_set():
                    await self.send_silence()
                    await asyncio.sleep(self.config.audio_send_interval_ms / 1000)
        except asyncio.CancelledError:
            pass
        finally:
            await self.disconnect()

    async def _receive_loop(self) -> None:
        """Background task: receive audio and text from the server."""
        try:
            async for msg in self._ws:
                if self._stop_event.is_set():
                    break

                if msg.type == aiohttp.WSMsgType.BINARY:
                    if len(msg.data) == 0:
                        continue

                    kind = msg.data[0]
                    payload = msg.data[1:]

                    if kind == MSG_AUDIO:
                        self._stats.last_audio_received = time.time()
                        self._stats.total_audio_received += 1

                        # Track latency
                        if self._stats.last_audio_sent > 0:
                            latency = (self._stats.last_audio_received - self._stats.last_audio_sent) * 1000
                            self._latency_history.append(latency)
                            self._stats.current_latency_ms = latency
                            if self._latency_history:
                                self._stats.avg_latency_ms = sum(self._latency_history) / len(self._latency_history)

                        # Decode opus to PCM
                        pcm = self._opus_reader.append_bytes(payload)
                        if pcm.shape[-1] > 0 and self.on_audio_received:
                            try:
                                result = self.on_audio_received(pcm)
                                if asyncio.iscoroutine(result):
                                    await result
                            except Exception as e:
                                logger.error(f"Audio callback error: {e}")

                    elif kind == MSG_TEXT:
                        text = payload.decode("utf-8")
                        self._stats.total_text_tokens += 1
                        if self.on_text_received:
                            try:
                                result = self.on_text_received(text)
                                if asyncio.iscoroutine(result):
                                    await result
                            except Exception as e:
                                logger.error(f"Text callback error: {e}")

                elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                    logger.warning(f"WebSocket closed/error: {msg.type}")
                    break

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Receive loop error: {e}")

        # If we exited the loop unexpectedly, attempt reconnect
        if not self._stop_event.is_set() and self.config.auto_reconnect:
            await self._auto_reconnect()

    async def _latency_monitor(self) -> None:
        """Background task: monitor latency and trigger reconnect if degraded."""
        while not self._stop_event.is_set():
            await asyncio.sleep(5.0)

            if self._state != AgentState.STREAMING:
                continue

            if len(self._latency_history) < 3:
                continue

            avg = self._stats.avg_latency_ms
            if avg > self.config.latency_threshold_ms:
                logger.warning(
                    f"Latency degraded: {avg:.0f}ms avg "
                    f"(threshold: {self.config.latency_threshold_ms:.0f}ms). "
                    f"Auto-reconnecting to reset KV cache."
                )
                await self._auto_reconnect()

    async def _auto_reconnect(self) -> None:
        """Disconnect and reconnect with exponential backoff."""
        if self._stop_event.is_set():
            return

        self._set_state(AgentState.RECONNECTING)
        self._reconnect_count += 1
        self._stats.reconnect_count += 1

        if self._reconnect_count > self.config.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts ({self.config.max_reconnect_attempts}) reached")
            self._set_state(AgentState.ERROR)
            return

        backoff = min(
            self.config.reconnect_backoff_base ** (self._reconnect_count - 1),
            self.config.reconnect_backoff_max
        )
        logger.info(f"Reconnecting in {backoff:.1f}s (attempt {self._reconnect_count})")

        await self._cleanup()
        await asyncio.sleep(backoff)

        success = await self.connect()
        if not success:
            logger.error("Reconnection failed")

    async def _cleanup(self) -> None:
        """Close WebSocket and session."""
        try:
            if self._ws and not self._ws.closed:
                await self._ws.close()
        except Exception:
            pass
        self._ws = None

        try:
            if self._session and not self._session.closed:
                await self._session.close()
        except Exception:
            pass
        self._session = None

        self._opus_writer = None
        self._opus_reader = None
