"""Test audio input/output hardware.

Verifies microphone and speaker functionality before running Conscious.

Usage:
    python scripts/test_audio.py
"""

import sys
import time

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    print("ERROR: sounddevice not installed. Run: pip install sounddevice")
    sys.exit(1)

try:
    from scipy.signal import resample_poly
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


TARGET_RATE = 24000  # Moshi expects 24kHz
CHANNELS = 1
RECORD_SECONDS = 3
FRAME_MS = 80  # Moshi frame size
FRAME_SAMPLES = int(TARGET_RATE * FRAME_MS / 1000)  # 1920 samples

# Will be set by find_working_input_device()
CAPTURE_RATE = None
CAPTURE_DEVICE = None


def find_working_input_device() -> tuple[int | None, int]:
    """Find a working input device, preferring WASAPI over MME.

    Returns:
        (device_index_or_None, sample_rate) — None means use default.
    """
    devices = sd.query_devices()

    # Collect all input devices, prioritize WASAPI (48kHz) over MME (44100Hz)
    candidates = []
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            sr = int(dev["default_samplerate"])
            # WASAPI devices typically show 48000Hz on Windows
            is_wasapi = sr == 48000
            candidates.append((i, dev["name"], sr, is_wasapi))

    # Sort: WASAPI first, then by device index
    candidates.sort(key=lambda x: (not x[3], x[0]))

    for idx, name, sr, is_wasapi in candidates:
        api_type = "WASAPI" if is_wasapi else "MME"
        try:
            # Try opening a very short stream to test
            test_stream = sd.InputStream(
                device=idx,
                samplerate=sr,
                channels=CHANNELS,
                blocksize=1024,
                dtype="float32",
            )
            test_stream.start()
            time.sleep(0.1)
            test_stream.stop()
            test_stream.close()
            print(f"  FOUND working device: [{idx}] {name} @ {sr}Hz ({api_type})")
            return idx, sr
        except Exception as e:
            print(f"  SKIP [{idx}] {name} @ {sr}Hz ({api_type}): {e}")
            continue

    # Last resort: try default device at its native rate
    try:
        default_dev = sd.query_devices(kind="input")
        sr = int(default_dev["default_samplerate"])
        return None, sr
    except Exception:
        return None, 44100


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio from orig_sr to target_sr."""
    if orig_sr == target_sr:
        return audio
    if HAS_SCIPY:
        from math import gcd
        g = gcd(orig_sr, target_sr)
        return resample_poly(audio.flatten(), target_sr // g, orig_sr // g).reshape(-1, 1).astype(np.float32)
    # Fallback: simple linear interpolation
    ratio = target_sr / orig_sr
    n_samples = int(len(audio) * ratio)
    indices = np.linspace(0, len(audio) - 1, n_samples)
    return np.interp(indices, np.arange(len(audio)), audio.flatten()).reshape(-1, 1).astype(np.float32)


def list_devices() -> None:
    """List available audio devices."""
    print("\n--- Audio Devices ---")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        direction = ""
        if dev["max_input_channels"] > 0:
            direction += "IN"
        if dev["max_output_channels"] > 0:
            direction += "/OUT" if direction else "OUT"
        print(f"  [{i}] {dev['name']} ({direction}) - {dev['default_samplerate']:.0f}Hz")

    default_in = sd.query_devices(kind="input")
    default_out = sd.query_devices(kind="output")
    print(f"\n  Default input:  {default_in['name']}")
    print(f"  Default output: {default_out['name']}")


def test_microphone() -> np.ndarray:
    """Record from microphone and return audio data (resampled to 24kHz)."""
    print(f"\n--- Microphone Test ({RECORD_SECONDS}s) ---")
    print(f"  Capture at {CAPTURE_RATE}Hz, resample to {TARGET_RATE}Hz")
    print(f"  Device: {CAPTURE_DEVICE}")
    print(f"  Speak now!", flush=True)

    audio = sd.rec(
        int(CAPTURE_RATE * RECORD_SECONDS),
        samplerate=CAPTURE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=CAPTURE_DEVICE,
    )
    sd.wait()

    # Resample to Moshi's 24kHz
    audio_24k = resample_audio(audio, CAPTURE_RATE, TARGET_RATE)
    print(f"  Captured {len(audio)} samples @ {CAPTURE_RATE}Hz -> {len(audio_24k)} samples @ {TARGET_RATE}Hz")

    peak = np.max(np.abs(audio_24k))
    rms = np.sqrt(np.mean(audio_24k**2))
    print(f"  Peak level: {peak:.4f}")
    print(f"  RMS level:  {rms:.4f}")

    if peak < 0.01:
        print("  WARNING: Very low audio level. Check microphone.")
    elif peak > 0.95:
        print("  WARNING: Audio clipping detected. Reduce input volume.")
    else:
        print("  PASS: Audio levels look good.")

    return audio_24k


def test_speaker(audio: np.ndarray) -> None:
    """Play back recorded audio through speakers."""
    print(f"\n--- Speaker Test (playback) ---")
    print(f"  Playing back {len(audio) / TARGET_RATE:.1f}s of recorded audio @ {TARGET_RATE}Hz...")

    sd.play(audio, samplerate=TARGET_RATE)
    sd.wait()
    print("  PASS: Playback complete.")


def test_streaming_latency() -> None:
    """Test streaming audio capture at Moshi's frame rate."""
    print(f"\n--- Streaming Latency Test ---")
    print(f"  Frame size: {FRAME_SAMPLES} samples ({FRAME_MS}ms)")
    print(f"  Testing {RECORD_SECONDS}s of streaming capture...")

    # Use capture rate for streaming, frame-align to equivalent of 80ms at capture rate
    capture_frame = int(CAPTURE_RATE * FRAME_MS / 1000)  # e.g., 3840 samples at 48kHz
    frames_collected = []
    frame_times = []

    def callback(indata, frames, time_info, status):
        if status:
            print(f"  WARNING: {status}")
        frames_collected.append(indata.copy())
        frame_times.append(time.perf_counter())

    with sd.InputStream(
        device=CAPTURE_DEVICE,
        samplerate=CAPTURE_RATE,
        channels=CHANNELS,
        blocksize=capture_frame,
        dtype="float32",
        callback=callback,
    ):
        time.sleep(RECORD_SECONDS)

    num_frames = len(frames_collected)
    expected_frames = int(RECORD_SECONDS * CAPTURE_RATE / capture_frame)

    if len(frame_times) >= 2:
        intervals = np.diff(frame_times) * 1000  # ms
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        max_interval = np.max(intervals)
        print(f"  Frames captured: {num_frames} (expected ~{expected_frames})")
        print(f"  Avg interval:    {avg_interval:.1f}ms (target: {FRAME_MS}ms)")
        print(f"  Std deviation:   {std_interval:.1f}ms")
        print(f"  Max interval:    {max_interval:.1f}ms")
        if max_interval < FRAME_MS * 2:
            print("  PASS: Streaming latency is good.")
        else:
            print("  WARNING: Some frames arrived late. May cause audio glitches.")
    else:
        print("  FAIL: Not enough frames captured.")


def main() -> None:
    """Run all audio tests."""
    print("=" * 60)
    print("CONSCIOUS - Audio Hardware Test")
    print("=" * 60)

    list_devices()

    # Auto-detect working input device
    global CAPTURE_DEVICE, CAPTURE_RATE
    print("\n--- Device Auto-Detection ---")
    CAPTURE_DEVICE, CAPTURE_RATE = find_working_input_device()
    print(f"  Using: device={CAPTURE_DEVICE}, rate={CAPTURE_RATE}Hz")

    try:
        audio = test_microphone()
        test_speaker(audio)
        test_streaming_latency()
    except sd.PortAudioError as e:
        print(f"\n  FAIL: Audio device error: {e}")
        print("  Check that your microphone and speakers are connected.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  FAIL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All audio tests passed!")
    print(f"Your hardware is ready for Conscious.")
    print(f"  Capture: {CAPTURE_RATE}Hz -> Resample -> {TARGET_RATE}Hz / {FRAME_MS}ms frames")
    print("=" * 60)


if __name__ == "__main__":
    main()
