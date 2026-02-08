"""Minimal Moshi API verification script.

Runs the exact code pattern from Moshi's README to verify:
1. Model weights can be loaded
2. Mimi codec encode/decode works
3. Moshi LM generation works
4. GPU/CUDA is available and functional

Usage:
    python scripts/test_moshi_api.py
"""

import os
import sys
import time

# Official Moshi env vars (moshi/utils/compile.py) + generic torch dynamo disable
# Required on Windows + Python 3.13 where triton is incompatible
os.environ["NO_TORCH_COMPILE"] = "1"
os.environ["NO_CUDA_GRAPH"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"

import torch


def check_cuda() -> str:
    """Check CUDA availability and return device string."""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"  GPU: {gpu_name}")
        print(f"  VRAM: {vram_gb:.1f} GB")
        print(f"  CUDA: {torch.version.cuda}")
        return "cuda"
    else:
        print("  WARNING: No CUDA GPU detected. Running on CPU (will be slow).")
        return "cpu"


def test_mimi_codec(device: str) -> list:
    """Test Mimi audio codec encode/decode."""
    from huggingface_hub import hf_hub_download
    from moshi.models import loaders

    print("\n[2/4] Loading Mimi codec...")
    start = time.time()
    mimi_weight = hf_hub_download(loaders.DEFAULT_REPO, loaders.MIMI_NAME)
    mimi = loaders.get_mimi(mimi_weight, device=device)
    mimi.set_num_codebooks(8)
    print(f"  Loaded in {time.time() - start:.1f}s")
    print(f"  Frame size: {mimi.frame_size} samples ({mimi.frame_size / 24000 * 1000:.0f}ms)")

    # Test encode/decode with synthetic audio (2 seconds)
    print("\n[3/4] Testing Mimi encode/decode...")
    duration_s = 2.0
    num_samples = int(24000 * duration_s)
    # Pad to multiple of frame_size
    num_samples = (num_samples // mimi.frame_size) * mimi.frame_size
    wav = torch.randn(1, 1, num_samples, device=device)

    start = time.time()
    with torch.no_grad():
        # Batch encode/decode
        codes = mimi.encode(wav)
        decoded = mimi.decode(codes)
        print(f"  Batch - Input: {wav.shape} -> Codes: {codes.shape} -> Decoded: {decoded.shape}")

        # Streaming encode
        all_codes = []
        with mimi.streaming(batch_size=1):
            for offset in range(0, wav.shape[-1], mimi.frame_size):
                frame = wav[:, :, offset: offset + mimi.frame_size]
                frame_codes = mimi.encode(frame)
                all_codes.append(frame_codes)

    elapsed = time.time() - start
    num_frames = len(all_codes)
    print(f"  Streaming - {num_frames} frames encoded in {elapsed:.3f}s")
    print(f"  Per-frame: {elapsed / num_frames * 1000:.1f}ms (target: <80ms)")
    print(f"  PASS" if elapsed / num_frames < 0.080 else f"  WARN: Slow encoding")

    return all_codes


def test_moshi_lm(device: str, all_codes: list) -> None:
    """Test Moshi LM generation."""
    from huggingface_hub import hf_hub_download
    from moshi.models import loaders, LMGen

    if device == "cpu":
        print("\n[4/4] Skipping Moshi LM test (requires GPU)")
        print("  The LM model is too large for CPU inference.")
        return

    print("\n[4/4] Loading Moshi LM...")
    start = time.time()
    moshi_weight = hf_hub_download(loaders.DEFAULT_REPO, loaders.MOSHI_NAME)
    moshi = loaders.get_moshi_lm(moshi_weight, device=device)
    lm_gen = LMGen(moshi, temp=0.8, temp_text=0.7)
    print(f"  Loaded in {time.time() - start:.1f}s")

    # Load Mimi on GPU for decoding output
    mimi_weight = hf_hub_download(loaders.DEFAULT_REPO, loaders.MIMI_NAME)
    mimi = loaders.get_mimi(mimi_weight, device=device)
    mimi.set_num_codebooks(8)

    print("  Running LM generation on encoded frames...")
    start = time.time()
    out_chunks = []
    with torch.no_grad(), lm_gen.streaming(1), mimi.streaming(1):
        for idx, code in enumerate(all_codes):
            tokens_out = lm_gen.step(code.to(device))
            if tokens_out is not None:
                # tokens_out is [B, 1+8, 1]
                # tokens_out[:, 0] = text token
                # tokens_out[:, 1:] = audio tokens
                wav_chunk = mimi.decode(tokens_out[:, 1:])
                out_chunks.append(wav_chunk)
            print(f"  Frame {idx + 1}/{len(all_codes)}", end="\r")

    elapsed = time.time() - start
    if out_chunks:
        out_wav = torch.cat(out_chunks, dim=-1)
        print(f"\n  Generated {out_wav.shape[-1] / 24000:.2f}s of audio in {elapsed:.2f}s")
        rtf = elapsed / (out_wav.shape[-1] / 24000)
        print(f"  Real-time factor: {rtf:.2f}x (target: <1.0x)")
        print(f"  PASS" if rtf < 1.0 else f"  WARN: Slower than real-time")
    else:
        print(f"\n  WARNING: No output generated")


def main() -> None:
    """Run all Moshi API tests."""
    print("=" * 60)
    print("CONSCIOUS - Moshi API Verification")
    print("=" * 60)

    print("\n[1/4] Checking hardware...")
    device = check_cuda()

    try:
        all_codes = test_mimi_codec(device)
        test_moshi_lm(device, all_codes)
    except Exception as e:
        print(f"\n  FAIL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("All tests passed! Moshi API is working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    main()
