"""Audio Stream — Real-time microphone input and speaker output.

Bridges system audio hardware with the Moshi engine using sounddevice.
Handles buffering, resampling, and frame alignment to Moshi's 80ms / 1920-sample
frame size at 24kHz.

Architecture:
    Mic -> callback -> input_queue -> [MoshiEngine] -> output_queue -> callback -> Speaker
"""

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import torch

logger = logging.getLogger(__name__)

SAMPLE_RATE = 24000
CHANNELS = 1
FRAME_SIZE = 1920  # 80ms at 24kHz
DTYPE = "float32"


@dataclass
class AudioStreamConfig:
    """Configuration for audio streaming."""

    sample_rate: int = SAMPLE_RATE
    channels: int = CHANNELS
    frame_size: int = FRAME_SIZE
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    max_queue_size: int = 50  # Max buffered frames before dropping


class AudioStream:
    """Full-duplex audio streaming for real-time voice conversation.

    Captures microphone input in frame-aligned chunks and plays back
    generated audio through speakers, both at 24kHz / 80ms frames.

    Usage:
        stream = AudioStream()
        stream.start()

        while running:
            frame = stream.get_input_frame()  # blocks until frame ready
            if frame is not None:
                output = engine.process_frame(frame)
                if output is not None:
                    stream.put_output_frame(output)

        stream.stop()
    """

    def __init__(self, config: Optional[AudioStreamConfig] = None):
        self.config = config or AudioStreamConfig()

        self._input_queue: queue.Queue[torch.Tensor] = queue.Queue(
            maxsize=self.config.max_queue_size
        )
        self._output_queue: queue.Queue[np.ndarray] = queue.Queue(
            maxsize=self.config.max_queue_size
        )

        self._input_stream: Optional[sd.InputStream] = None
        self._output_stream: Optional[sd.OutputStream] = None
        self._running = False

        # Buffer for accumulating partial input frames
        self._input_buffer = np.zeros(0, dtype=np.float32)
        self._buffer_lock = threading.Lock()

        # Stats
        self._frames_captured = 0
        self._frames_played = 0
        self._frames_dropped = 0

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        """Start audio capture and playback streams."""
        if self._running:
            logger.warning("Audio stream already running")
            return

        logger.info(
            f"Starting audio streams: {self.config.sample_rate}Hz, "
            f"{self.config.frame_size} samples/frame "
            f"({self.config.frame_size / self.config.sample_rate * 1000:.0f}ms)"
        )

        self._input_stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            blocksize=self.config.frame_size,
            dtype=DTYPE,
            device=self.config.input_device,
            callback=self._input_callback,
        )

        self._output_stream = sd.OutputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            blocksize=self.config.frame_size,
            dtype=DTYPE,
            device=self.config.output_device,
            callback=self._output_callback,
        )

        self._running = True
        self._input_stream.start()
        self._output_stream.start()
        logger.info("Audio streams started")

    def stop(self) -> None:
        """Stop audio streams and clean up."""
        if not self._running:
            return

        self._running = False

        if self._input_stream is not None:
            self._input_stream.stop()
            self._input_stream.close()
            self._input_stream = None

        if self._output_stream is not None:
            self._output_stream.stop()
            self._output_stream.close()
            self._output_stream = None

        # Drain queues
        while not self._input_queue.empty():
            try:
                self._input_queue.get_nowait()
            except queue.Empty:
                break

        while not self._output_queue.empty():
            try:
                self._output_queue.get_nowait()
            except queue.Empty:
                break

        logger.info(
            f"Audio streams stopped. "
            f"Captured: {self._frames_captured}, "
            f"Played: {self._frames_played}, "
            f"Dropped: {self._frames_dropped}"
        )

    def get_input_frame(self, timeout: float = 0.2) -> Optional[torch.Tensor]:
        """Get the next input audio frame as a torch tensor.

        Returns:
            Tensor of shape [1, 1, frame_size] (float32) or None on timeout.
        """
        try:
            return self._input_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def put_output_frame(self, audio: torch.Tensor) -> None:
        """Queue an audio frame for playback.

        Args:
            audio: Tensor of shape [B, C, T] — will be converted to numpy.
        """
        # Convert torch tensor to numpy for sounddevice
        np_audio = audio.squeeze().cpu().numpy()

        # Ensure correct length (pad or trim to frame_size)
        if len(np_audio) < self.config.frame_size:
            np_audio = np.pad(np_audio, (0, self.config.frame_size - len(np_audio)))
        elif len(np_audio) > self.config.frame_size:
            np_audio = np_audio[: self.config.frame_size]

        try:
            self._output_queue.put_nowait(np_audio)
        except queue.Full:
            self._frames_dropped += 1
            # Drop oldest frame to prevent growing lag
            try:
                self._output_queue.get_nowait()
            except queue.Empty:
                pass
            self._output_queue.put_nowait(np_audio)

    def get_stats(self) -> dict:
        """Return audio stream statistics."""
        return {
            "frames_captured": self._frames_captured,
            "frames_played": self._frames_played,
            "frames_dropped": self._frames_dropped,
            "input_queue_size": self._input_queue.qsize(),
            "output_queue_size": self._output_queue.qsize(),
        }

    def _input_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Sounddevice input callback — accumulates audio into frame-aligned chunks."""
        if status:
            logger.warning(f"Input status: {status}")

        if not self._running:
            return

        # indata is [frames, channels], we need [frame_size] flat
        audio = indata[:, 0].copy()

        with self._buffer_lock:
            self._input_buffer = np.concatenate([self._input_buffer, audio])

            # Extract complete frames from buffer
            while len(self._input_buffer) >= self.config.frame_size:
                frame_np = self._input_buffer[: self.config.frame_size]
                self._input_buffer = self._input_buffer[self.config.frame_size :]

                # Convert to torch tensor [1, 1, frame_size]
                frame_tensor = torch.from_numpy(frame_np).unsqueeze(0).unsqueeze(0)

                try:
                    self._input_queue.put_nowait(frame_tensor)
                    self._frames_captured += 1
                except queue.Full:
                    self._frames_dropped += 1
                    # Drop oldest to keep latency low
                    try:
                        self._input_queue.get_nowait()
                    except queue.Empty:
                        pass
                    self._input_queue.put_nowait(frame_tensor)

    def _output_callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        """Sounddevice output callback — feeds queued audio to speakers."""
        if status:
            logger.warning(f"Output status: {status}")

        try:
            audio = self._output_queue.get_nowait()
            outdata[:, 0] = audio[: len(outdata)]
            self._frames_played += 1
        except queue.Empty:
            # No audio to play — output silence
            outdata.fill(0)
