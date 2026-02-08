"""Conscious Server — Main entry point for the voice companion.

Ties together the Moshi voice engine, audio streaming, config loading,
and (future) personality/memory/emotion systems into a real-time
voice conversation loop.

Usage:
    python -m conscious.server
    # or via entry point:
    conscious
"""

import logging
import signal
import sys
import time
from typing import Optional

import torch

from conscious.config import load_config, get_config_value
from conscious.voice.audio_stream import AudioStream, AudioStreamConfig
from conscious.voice.moshi_engine import MoshiEngine, MoshiConfig

logger = logging.getLogger("conscious")


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


class ConsciousServer:
    """Main server coordinating voice pipeline and future subsystems.

    Pipeline:
        Mic -> AudioStream -> MoshiEngine.process_frame -> AudioStream -> Speaker
                                    |
                                    v
                            (future: personality, memory, emotion hooks)
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or load_config()
        self._running = False

        # Build component configs from unified config
        moshi_cfg = MoshiConfig(
            device=get_config_value(self._config, "moshi.device", "cuda"),
            temp=0.8,
            temp_text=0.7,
        )
        audio_cfg = AudioStreamConfig()

        self._engine = MoshiEngine(moshi_cfg)
        self._audio = AudioStream(audio_cfg)

    def start(self) -> None:
        """Initialize models and start the conversation loop."""
        logger.info("=" * 60)
        logger.info("CONSCIOUS — Starting Voice Companion")
        logger.info("=" * 60)

        # Load models
        logger.info("Loading models...")
        self._engine.load_models()

        # Start audio streams
        logger.info("Starting audio streams...")
        self._audio.start()

        # Display greeting
        personality = get_config_value(self._config, "personality.active", "conscious")
        greeting = get_config_value(self._config, "greeting.first_time", "")
        logger.info(f"Active personality: {personality}")
        if greeting:
            # In future: speak the greeting via TTS
            print(f"\n{greeting.strip()}\n")

        # Enter main loop
        self._running = True
        self._conversation_loop()

    def stop(self) -> None:
        """Gracefully shut down all systems."""
        logger.info("Shutting down...")
        self._running = False
        self._audio.stop()

        # Display farewell
        farewell = get_config_value(self._config, "farewell.conscious", [])
        if farewell and isinstance(farewell, list):
            import random
            print(f"\n{random.choice(farewell)}\n")

        # Log final stats
        engine_stats = self._engine.get_performance_stats()
        audio_stats = self._audio.get_stats()
        logger.info(f"Engine stats: {engine_stats}")
        logger.info(f"Audio stats: {audio_stats}")
        logger.info("Conscious has stopped.")

    def _conversation_loop(self) -> None:
        """Main real-time conversation loop.

        Reads mic frames, processes through Moshi, plays output.
        Runs until interrupted or stop() is called.
        """
        logger.info("Entering conversation loop (Ctrl+C to exit)")

        with self._engine.streaming():
            while self._running:
                # Get next mic frame (blocks up to 200ms)
                frame = self._audio.get_input_frame(timeout=0.2)
                if frame is None:
                    continue

                # Process through Moshi: encode -> LM -> decode
                try:
                    output = self._engine.process_frame(frame)
                except Exception as e:
                    logger.error(f"Engine error: {e}")
                    continue

                # Queue output for playback
                if output is not None:
                    self._audio.put_output_frame(output)

        logger.info("Conversation loop ended")


def main() -> None:
    """Entry point for the conscious command."""
    setup_logging("INFO")

    try:
        config = load_config()
    except FileNotFoundError as e:
        logger.error(str(e))
        logger.error("Run 'python scripts/download_models.py' first.")
        sys.exit(1)

    server = ConsciousServer(config)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        server.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
