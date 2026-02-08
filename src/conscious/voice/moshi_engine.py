"""Moshi Voice Engine — Core wrapper for Kyutai Moshi speech-to-speech model.

Handles model loading, streaming encode/decode via Mimi codec,
and LM generation via Moshi. Designed for full-duplex conversation.

Architecture:
    Mic -> AudioStream -> Mimi.encode -> LMGen.step -> Mimi.decode -> Speaker
"""

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Official Moshi env vars (moshi/utils/compile.py) + generic torch dynamo disable
# Required on Windows + Python 3.13 where triton is incompatible
os.environ.setdefault("NO_TORCH_COMPILE", "1")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
# NOTE: NO_CUDA_GRAPH intentionally NOT set — CUDA Graphs work on Py3.13 and are needed for real-time audio

import torch

from huggingface_hub import hf_hub_download
from moshi.models import loaders, LMGen

logger = logging.getLogger(__name__)


@dataclass
class MoshiConfig:
    """Configuration for the Moshi voice engine."""

    device: str = "cuda"
    use_quantization: bool = False
    precision: str = "fp16"
    temp: float = 0.8
    temp_text: float = 0.7
    frame_size: int = 1920  # 80ms at 24kHz
    sample_rate: int = 24000
    num_codebooks: int = 8


class MoshiEngine:
    """Wraps Kyutai Moshi for streaming voice-to-voice generation.

    Usage:
        engine = MoshiEngine(config)
        engine.load_models()

        with engine.streaming():
            while running:
                audio_in = get_mic_frame()  # [1, 1, 1920]
                audio_out = engine.process_frame(audio_in)
                play_speaker(audio_out)
    """

    def __init__(self, config: Optional[MoshiConfig] = None):
        self.config = config or MoshiConfig()
        self._mimi = None
        self._moshi_lm = None
        self._lm_gen = None
        self._loaded = False
        self._streaming = False

        # Performance tracking
        self._frame_count = 0
        self._total_encode_ms = 0.0
        self._total_step_ms = 0.0
        self._total_decode_ms = 0.0

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def is_streaming(self) -> bool:
        return self._streaming

    def load_models(self) -> None:
        """Download (if needed) and load Mimi codec + Moshi LM."""
        device = self.config.device
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            device = "cpu"
            self.config.device = device

        logger.info("Loading Mimi codec...")
        start = time.time()
        mimi_weight = hf_hub_download(loaders.DEFAULT_REPO, loaders.MIMI_NAME)
        self._mimi = loaders.get_mimi(mimi_weight, device=device)
        self._mimi.set_num_codebooks(self.config.num_codebooks)
        logger.info(f"Mimi loaded in {time.time() - start:.1f}s (device={device})")

        logger.info("Loading Moshi LM...")
        start = time.time()
        moshi_weight = hf_hub_download(loaders.DEFAULT_REPO, loaders.MOSHI_NAME)
        self._moshi_lm = loaders.get_moshi_lm(moshi_weight, device=device)
        self._lm_gen = LMGen(
            self._moshi_lm,
            temp=self.config.temp,
            temp_text=self.config.temp_text,
        )
        logger.info(f"Moshi LM loaded in {time.time() - start:.1f}s")

        self._loaded = True
        logger.info("All models loaded successfully")

    def streaming(self):
        """Context manager for streaming mode.

        Must be entered before calling process_frame().
        Sets up streaming state for both Mimi and Moshi LM.
        """
        return _StreamingContext(self)

    def process_frame(self, audio_in: torch.Tensor) -> Optional[torch.Tensor]:
        """Process one audio frame through the full pipeline.

        Args:
            audio_in: Input audio tensor [B=1, C=1, T=frame_size] at 24kHz.
                      Must be exactly frame_size (1920) samples.

        Returns:
            Output audio tensor [B=1, C=1, T] or None if LM hasn't started
            producing output yet (initial warmup frames).
        """
        if not self._streaming:
            raise RuntimeError("Must be in streaming mode. Use `with engine.streaming():`")

        device = self.config.device

        # Ensure input is on the right device
        if audio_in.device.type != device:
            audio_in = audio_in.to(device)

        # Encode: audio -> codes
        t0 = time.perf_counter()
        with torch.no_grad():
            codes = self._mimi.encode(audio_in)  # [B, K=8, T=1]
        t1 = time.perf_counter()

        # LM step: input codes -> output tokens
        with torch.no_grad():
            tokens_out = self._lm_gen.step(codes)  # [B, 1+8, 1] or None
        t2 = time.perf_counter()

        # Decode: output tokens -> audio
        audio_out = None
        if tokens_out is not None:
            with torch.no_grad():
                # tokens_out[:, 0] = text token
                # tokens_out[:, 1:] = audio tokens (8 codebooks)
                audio_out = self._mimi.decode(tokens_out[:, 1:])  # [B, C=1, T]
        t3 = time.perf_counter()

        # Track performance
        self._frame_count += 1
        self._total_encode_ms += (t1 - t0) * 1000
        self._total_step_ms += (t2 - t1) * 1000
        self._total_decode_ms += (t3 - t2) * 1000

        if self._frame_count % 100 == 0:
            self._log_performance()

        return audio_out

    def get_text_token(self, tokens_out: torch.Tensor) -> int:
        """Extract text token from LM output for personality/context use.

        Args:
            tokens_out: LM output tensor [B, 1+8, 1]

        Returns:
            Text token ID (int)
        """
        return tokens_out[0, 0, 0].item()

    def get_performance_stats(self) -> dict:
        """Return current performance statistics."""
        if self._frame_count == 0:
            return {"frame_count": 0}

        frame_ms = self.config.frame_size / self.config.sample_rate * 1000  # 80ms
        avg_encode = self._total_encode_ms / self._frame_count
        avg_step = self._total_step_ms / self._frame_count
        avg_decode = self._total_decode_ms / self._frame_count
        avg_total = avg_encode + avg_step + avg_decode

        return {
            "frame_count": self._frame_count,
            "frame_budget_ms": frame_ms,
            "avg_encode_ms": round(avg_encode, 2),
            "avg_lm_step_ms": round(avg_step, 2),
            "avg_decode_ms": round(avg_decode, 2),
            "avg_total_ms": round(avg_total, 2),
            "realtime_factor": round(avg_total / frame_ms, 3),
            "within_budget": avg_total < frame_ms,
        }

    def _log_performance(self) -> None:
        """Log performance stats periodically."""
        stats = self.get_performance_stats()
        status = "OK" if stats["within_budget"] else "SLOW"
        logger.info(
            f"[{status}] Frame {stats['frame_count']}: "
            f"encode={stats['avg_encode_ms']:.1f}ms "
            f"lm={stats['avg_lm_step_ms']:.1f}ms "
            f"decode={stats['avg_decode_ms']:.1f}ms "
            f"total={stats['avg_total_ms']:.1f}ms "
            f"(budget={stats['frame_budget_ms']:.0f}ms, "
            f"rtf={stats['realtime_factor']:.2f}x)"
        )

    def reset_stats(self) -> None:
        """Reset performance counters."""
        self._frame_count = 0
        self._total_encode_ms = 0.0
        self._total_step_ms = 0.0
        self._total_decode_ms = 0.0


class _StreamingContext:
    """Context manager that sets up Mimi + LMGen streaming state."""

    def __init__(self, engine: MoshiEngine):
        self._engine = engine
        self._mimi_ctx = None
        self._lm_ctx = None

    def __enter__(self):
        if not self._engine.is_loaded:
            raise RuntimeError("Models not loaded. Call engine.load_models() first.")
        if self._engine._streaming:
            raise RuntimeError("Already in streaming mode.")

        self._mimi_ctx = self._engine._mimi.streaming(batch_size=1)
        self._lm_ctx = self._engine._lm_gen.streaming(batch_size=1)

        self._mimi_ctx.__enter__()
        self._lm_ctx.__enter__()

        self._engine._streaming = True
        self._engine.reset_stats()
        logger.info("Streaming mode started")
        return self._engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._engine._streaming = False

        # Exit in reverse order
        try:
            self._lm_ctx.__exit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            logger.error(f"Error exiting LM streaming: {e}")

        try:
            self._mimi_ctx.__exit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            logger.error(f"Error exiting Mimi streaming: {e}")

        stats = self._engine.get_performance_stats()
        logger.info(f"Streaming ended. Processed {stats['frame_count']} frames.")
        if stats["frame_count"] > 0:
            self._engine._log_performance()

        return False
