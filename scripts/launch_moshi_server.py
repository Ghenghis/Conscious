"""Launch Moshi's built-in web server with torch.compile disabled.

On Windows + Python 3.13, triton is incompatible (AttrsDescriptor import error),
which causes torch.compile to crash. CUDA Graphs work fine without triton
and are REQUIRED for real-time audio performance.

Moshi's own codebase (moshi/utils/compile.py) checks these env vars:
  - NO_TORCH_COMPILE  -> skips torch.compile in torch_compile_lazy()
  - NO_CUDA_GRAPH     -> skips CUDAGraphed wrapping (DO NOT SET - needed for perf)

NO_TORCH_COMPILE MUST be set before any moshi/torch imports.

IMPORTANT: moshi/server.py has module-level code (lines 286-287) that calls main()
on import, so we CANNOT use `from moshi.server import main`. We must launch via
subprocess so env vars are inherited and the module runs exactly once as __main__.

Usage:
    python scripts/launch_moshi_server.py [--host HOST] [--port PORT]
    Then open http://localhost:8998 in Chrome and click Connect.
"""
import os
import subprocess
import sys


def launch():
    env = os.environ.copy()
    # Official Moshi env var from moshi/utils/compile.py line 41
    env["NO_TORCH_COMPILE"] = "1"
    # Generic torch dynamo disable as safety net
    env["TORCHDYNAMO_DISABLE"] = "1"
    # NOTE: CUDA Graphs left ENABLED — they work on Py3.13 and are needed for real-time audio

    cmd = [sys.executable, "-m", "moshi.server"] + sys.argv[1:]
    print(f"[launcher] Starting Moshi server: {' '.join(cmd)}")
    print(f"[launcher] Env: NO_TORCH_COMPILE=1, TORCHDYNAMO_DISABLE=1, CUDA Graphs ENABLED")

    proc = subprocess.run(cmd, env=env)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    launch()
