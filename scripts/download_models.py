"""Download Moshi and Mimi model weights from Hugging Face.

Usage:
    python scripts/download_models.py

Downloads to ~/.conscious/models/ by default.
"""

import os
import sys
import time
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    print("ERROR: huggingface-hub not installed. Run: pip install huggingface-hub")
    sys.exit(1)

try:
    from moshi.models import loaders
except ImportError:
    print("ERROR: moshi not installed. Run: pip install moshi")
    sys.exit(1)


MODELS_DIR = Path(os.path.expanduser("~/.conscious/models"))


def download_models() -> None:
    """Download Mimi codec and Moshi LM weights."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("CONSCIOUS - Model Download")
    print("=" * 60)
    print(f"Repository: {loaders.DEFAULT_REPO}")
    print(f"Target dir: {MODELS_DIR}")
    print()

    # Download Mimi (audio codec)
    print(f"[1/2] Downloading Mimi codec: {loaders.MIMI_NAME}")
    start = time.time()
    mimi_path = hf_hub_download(
        loaders.DEFAULT_REPO,
        loaders.MIMI_NAME,
        local_dir=str(MODELS_DIR),
    )
    elapsed = time.time() - start
    print(f"  -> {mimi_path}")
    print(f"  -> Completed in {elapsed:.1f}s")
    print()

    # Download Moshi LM
    print(f"[2/2] Downloading Moshi LM: {loaders.MOSHI_NAME}")
    start = time.time()
    moshi_path = hf_hub_download(
        loaders.DEFAULT_REPO,
        loaders.MOSHI_NAME,
        local_dir=str(MODELS_DIR),
    )
    elapsed = time.time() - start
    print(f"  -> {moshi_path}")
    print(f"  -> Completed in {elapsed:.1f}s")
    print()

    print("=" * 60)
    print("All models downloaded successfully!")
    print(f"Mimi: {mimi_path}")
    print(f"Moshi: {moshi_path}")
    print("=" * 60)


if __name__ == "__main__":
    download_models()
