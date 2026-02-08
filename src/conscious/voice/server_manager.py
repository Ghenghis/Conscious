"""Moshi Server Manager — Autonomous lifecycle management for the Moshi server process.

Handles starting, stopping, restarting, health checking, and crash recovery
for the Moshi voice AI server. Designed for fully autonomous operation
within the Super-Goose agentic framework.

Features:
    - Auto-kill stale processes on target port before starting
    - Health monitoring via HTTP polling
    - Automatic restart on crash with exponential backoff
    - GPU VRAM pre-flight check
    - Structured logging for all lifecycle events
"""

import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)

PYTHON_EXE = r"C:\Python313\python.exe"


class ServerStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    LOADING_MODEL = "loading_model"
    READY = "ready"
    ERROR = "error"
    RESTARTING = "restarting"


@dataclass
class ServerManagerConfig:
    """Configuration for the Moshi server manager."""
    host: str = "localhost"
    port: int = 8998
    python_exe: str = PYTHON_EXE
    health_check_interval: float = 5.0
    health_check_timeout: float = 3.0
    max_restart_attempts: int = 5
    restart_backoff_base: float = 2.0
    restart_backoff_max: float = 60.0
    min_vram_mb: int = 14000
    env_vars: dict = field(default_factory=lambda: {
        "NO_TORCH_COMPILE": "1",
        "TORCHDYNAMO_DISABLE": "1",
        "PYTHONUNBUFFERED": "1",
    })


class MoshiServerManager:
    """Manages the Moshi server process lifecycle autonomously.

    Usage:
        manager = MoshiServerManager()
        await manager.start()       # starts server + health monitor
        await manager.wait_ready()  # blocks until model loaded
        ...
        await manager.stop()

    The manager automatically restarts the server on crash with
    exponential backoff and logs all lifecycle events.
    """

    def __init__(self, config: Optional[ServerManagerConfig] = None,
                 on_status_change: Optional[Callable[[ServerStatus], None]] = None):
        self.config = config or ServerManagerConfig()
        self._process: Optional[subprocess.Popen] = None
        self._status = ServerStatus.STOPPED
        self._health_task: Optional[asyncio.Task] = None
        self._restart_count = 0
        self._on_status_change = on_status_change
        self._ready_event = asyncio.Event()
        self._stop_requested = False

    @property
    def status(self) -> ServerStatus:
        return self._status

    @property
    def is_ready(self) -> bool:
        return self._status == ServerStatus.READY

    @property
    def url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    @property
    def ws_url(self) -> str:
        return f"ws://{self.config.host}:{self.config.port}/api/chat"

    def _set_status(self, status: ServerStatus) -> None:
        old = self._status
        self._status = status
        if old != status:
            logger.info(f"Server status: {old.value} -> {status.value}")
            if self._on_status_change:
                try:
                    self._on_status_change(status)
                except Exception as e:
                    logger.error(f"Status change callback error: {e}")
            if status == ServerStatus.READY:
                self._ready_event.set()
            else:
                self._ready_event.clear()

    async def start(self) -> None:
        """Start the Moshi server and begin health monitoring."""
        if self._status in (ServerStatus.STARTING, ServerStatus.LOADING_MODEL, ServerStatus.READY):
            logger.warning(f"Server already in state {self._status.value}")
            return

        self._stop_requested = False
        self._restart_count = 0

        await self._kill_stale_port()
        await self._check_gpu_vram()
        await self._launch_process()

        self._health_task = asyncio.create_task(self._health_loop())
        logger.info("Server manager started with health monitoring")

    async def stop(self) -> None:
        """Stop the server and health monitoring."""
        self._stop_requested = True

        if self._health_task and not self._health_task.done():
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        await self._kill_process()
        self._set_status(ServerStatus.STOPPED)
        logger.info("Server manager stopped")

    async def restart(self) -> None:
        """Restart the server (kills existing, launches new)."""
        self._set_status(ServerStatus.RESTARTING)
        await self._kill_process()
        await asyncio.sleep(1)
        await self._kill_stale_port()
        await self._launch_process()

    async def wait_ready(self, timeout: float = 300.0) -> bool:
        """Wait until the server is ready to accept connections.

        Args:
            timeout: Maximum seconds to wait (default 5 minutes for model loading).

        Returns:
            True if server is ready, False if timed out.
        """
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.error(f"Server did not become ready within {timeout}s")
            return False

    async def _launch_process(self) -> None:
        """Launch the Moshi server subprocess."""
        self._set_status(ServerStatus.STARTING)

        env = os.environ.copy()
        env.update(self.config.env_vars)

        cmd = [
            self.config.python_exe, "-u", "-m", "moshi.server",
            "--host", self.config.host,
            "--port", str(self.config.port),
        ]

        logger.info(f"Launching: {' '.join(cmd)}")
        try:
            self._process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._set_status(ServerStatus.LOADING_MODEL)

            # Start log reader task
            asyncio.create_task(self._read_process_output())

        except Exception as e:
            logger.error(f"Failed to launch server: {e}")
            self._set_status(ServerStatus.ERROR)
            raise

    async def _read_process_output(self) -> None:
        """Read and log server stdout/stderr in background."""
        if not self._process or not self._process.stdout:
            return

        loop = asyncio.get_event_loop()
        try:
            while self._process.poll() is None:
                line = await loop.run_in_executor(None, self._process.stdout.readline)
                if not line:
                    break
                line = line.strip()
                if line:
                    logger.info(f"[moshi-server] {line}")
                    if "Access the Web UI directly at" in line:
                        self._set_status(ServerStatus.READY)
                        self._restart_count = 0
        except Exception as e:
            logger.error(f"Error reading server output: {e}")

    async def _kill_process(self) -> None:
        """Kill the current server process."""
        if self._process is None:
            return

        try:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=3)
            logger.info(f"Server process (PID {self._process.pid}) terminated")
        except Exception as e:
            logger.warning(f"Error killing server process: {e}")
        finally:
            self._process = None

    async def _kill_stale_port(self) -> None:
        """Kill any process holding the target port."""
        try:
            result = await asyncio.create_subprocess_exec(
                "powershell", "-Command",
                f"Get-NetTCPConnection -LocalPort {self.config.port} -ErrorAction SilentlyContinue | "
                f"ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            await result.wait()
            logger.info(f"Port {self.config.port} cleared")
        except Exception as e:
            logger.warning(f"Could not clear port {self.config.port}: {e}")

    async def _check_gpu_vram(self) -> None:
        """Check available GPU VRAM before starting."""
        try:
            result = await asyncio.create_subprocess_exec(
                self.config.python_exe, "-c",
                "import torch; f=torch.cuda.mem_get_info(0)[0]//1024//1024; "
                f"print(f'{{f}}'); exit(0 if f>{self.config.min_vram_mb} else 1)",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            free_mb = int(stdout.decode().strip())
            if result.returncode != 0:
                logger.warning(
                    f"Low GPU VRAM: {free_mb}MB free, need {self.config.min_vram_mb}MB. "
                    "Close GPU-heavy apps (LM Studio, games, etc.)"
                )
            else:
                logger.info(f"GPU VRAM: {free_mb}MB free (need {self.config.min_vram_mb}MB) — OK")
        except Exception as e:
            logger.warning(f"Could not check GPU VRAM: {e}")

    async def _health_check(self) -> bool:
        """Perform a single health check via HTTP."""
        import urllib.request
        import urllib.error

        try:
            loop = asyncio.get_event_loop()
            req = urllib.request.Request(self.url)
            resp = await asyncio.wait_for(
                loop.run_in_executor(None, urllib.request.urlopen, req),
                timeout=self.config.health_check_timeout
            )
            return resp.status == 200
        except Exception:
            return False

    async def _health_loop(self) -> None:
        """Continuous health monitoring with auto-restart on failure."""
        consecutive_failures = 0
        max_consecutive = 3

        while not self._stop_requested:
            await asyncio.sleep(self.config.health_check_interval)

            if self._stop_requested:
                break

            # Check if process is still alive
            if self._process and self._process.poll() is not None:
                exit_code = self._process.returncode
                logger.error(f"Server process exited with code {exit_code}")
                self._set_status(ServerStatus.ERROR)
                await self._try_restart()
                consecutive_failures = 0
                continue

            # Only health-check once server should be ready
            if self._status == ServerStatus.READY:
                healthy = await self._health_check()
                if not healthy:
                    consecutive_failures += 1
                    logger.warning(f"Health check failed ({consecutive_failures}/{max_consecutive})")
                    if consecutive_failures >= max_consecutive:
                        logger.error("Too many consecutive health check failures — restarting")
                        await self._try_restart()
                        consecutive_failures = 0
                else:
                    consecutive_failures = 0

    async def _try_restart(self) -> None:
        """Attempt to restart with exponential backoff."""
        if self._stop_requested:
            return

        if self._restart_count >= self.config.max_restart_attempts:
            logger.error(
                f"Max restart attempts ({self.config.max_restart_attempts}) reached. "
                "Manual intervention required."
            )
            self._set_status(ServerStatus.ERROR)
            return

        backoff = min(
            self.config.restart_backoff_base ** self._restart_count,
            self.config.restart_backoff_max
        )
        self._restart_count += 1

        logger.info(
            f"Restarting server (attempt {self._restart_count}/"
            f"{self.config.max_restart_attempts}) after {backoff:.0f}s backoff"
        )
        await asyncio.sleep(backoff)
        await self.restart()
