# Moshi Setup Guide — Windows

> Complete setup, configuration, and troubleshooting guide for running the Moshi voice AI server on Windows with Python 3.13 and NVIDIA GPU.

---

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| GPU | NVIDIA with 16GB+ VRAM | RTX 3090 Ti (24GB) |
| CUDA | 12.x | 12.4 |
| Python | 3.10 | 3.13.7 |
| RAM | 16GB | 32GB |
| Storage | 20GB free | 50GB free |
| OS | Windows 10 | Windows 11 |

---

## Installation

### Step 1: Python

Python 3.13.7 is installed at `C:\Python313\python.exe`. It is **NOT in the system PATH** — all commands must use the full path.

```powershell
# Verify
C:\Python313\python.exe --version
# Expected: Python 3.13.7
```

### Step 2: PyTorch with CUDA

```powershell
C:\Python313\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

This is a ~2.5GB download. Verify:

```powershell
C:\Python313\python.exe -c "import torch; print(f'PyTorch {torch.__version__} CUDA: {torch.cuda.is_available()}')"
# Expected: PyTorch 2.6.0+cu124 CUDA: True
```

### Step 3: Moshi

```powershell
C:\Python313\Scripts\pip.exe install moshi
```

This installs the Moshi package including `sphn` (opus codec) and model loaders. Verify:

```powershell
C:\Python313\python.exe -c "import moshi; print('Moshi OK')"
```

### Step 4: aiohttp (for Agent API)

```powershell
C:\Python313\Scripts\pip.exe install aiohttp
```

---

## One-Click Launch

The simplest way to start the Moshi server:

```
Double-click: D:\conscious\setup_and_launch.bat
```

This script automatically:

1. **Kills stale processes** on port 8998
2. **Checks Python** at `C:\Python313\python.exe`
3. **Checks/installs PyTorch** with CUDA 12.4
4. **Checks/installs Moshi**
5. **Checks/installs sounddevice**
6. **Checks GPU VRAM** (warns if <14GB free)
7. **Sets environment variables** (`NO_TORCH_COMPILE=1`, `TORCHDYNAMO_DISABLE=1`)
8. **Launches the server** with `python -u -m moshi.server`

Wait for: `Access the Web UI directly at http://localhost:8998`

---

## Environment Variables

### MUST Set

| Variable | Value | Reason |
|----------|-------|--------|
| `NO_TORCH_COMPILE` | `1` | `torch.compile` uses triton which is incompatible with Python 3.13 on Windows. Without this, the server crashes with `AttrsDescriptor` import error. Source: `moshi/utils/compile.py` line 41. |
| `TORCHDYNAMO_DISABLE` | `1` | Safety net to prevent any torch dynamo compilation attempts. |
| `PYTHONUNBUFFERED` | `1` | Ensures server output is visible immediately in the terminal. |

### MUST NOT Set

| Variable | Why NOT |
|----------|---------|
| `NO_CUDA_GRAPH` | CUDA Graphs do NOT depend on triton. They work perfectly on Python 3.13/Windows. They are **critical** for real-time audio performance. Disabling them causes all audio packets to be dropped (latency >10s, 100% packet loss). |

### How They Work

```python
# From moshi/utils/compile.py line 41:
def torch_compile_lazy(fun):
    if os.environ.get("NO_TORCH_COMPILE"):
        return fun  # skip compilation entirely
    # ... torch.compile(fun) ...

# From moshi/utils/compile.py line 172:
# NO_CUDA_GRAPH controls CUDAGraphed wrapping
```

---

## Model Details

### Location

Models are cached by Hugging Face at:

```
C:\Users\Admin\.cache\huggingface\hub\models--kyutai--moshi-artifacts\
  snapshots\5040b2bc0ede3531913ce11bf591e7c822164a54\
```

### Files

| File | Size | Purpose |
|------|------|---------|
| `tokenizer_spm_32k_3.model` | ~1MB | SentencePiece text tokenizer |
| `moshiko_pt_bf16` | ~15GB | Main Moshi LM checkpoint (bfloat16) |
| `tokenizer_mimi_pt` | ~300MB | Mimi audio codec checkpoint |
| `dist.tgz` | ~1MB | Frontend web UI (compressed) |
| `dist/` | ~1MB | Extracted frontend (11 files) |

### First Run

On first launch, the model downloads from Hugging Face (~15GB). Subsequent launches load from cache.

---

## Frontend Assets

The Moshi web UI at `http://localhost:8998` is a React app served from `dist/`.

### Structure

```
dist/
├── index.html
├── assets/
│   ├── index-ClFQVzk0.js        (907KB — main React app)
│   ├── index-DfGMjjGn.css       (styles)
│   ├── decoderWorker.min-DI6rkCrP.js
│   ├── encoderWorker.min-Cpxhjaao.js
│   ├── audio-processor-BUNQrM5u.js
│   └── ... (11 files total)
```

### Known Issue: Empty `dist/assets/`

If the Connect button appears but nothing happens (no errors visible), check if `dist/assets/` is empty:

```powershell
$distPath = "C:\Users\Admin\.cache\huggingface\hub\models--kyutai--moshi-artifacts\snapshots\5040b2bc0ede3531913ce11bf591e7c822164a54\dist"
Get-ChildItem "$distPath\assets" | Measure-Object
```

If count is 0, delete `dist/` and let the server re-extract from `dist.tgz`:

```powershell
Remove-Item -Recurse -Force $distPath
# Restart the server — it will re-extract automatically
```

---

## Troubleshooting

### Server Hangs on "warming up the model"

**Cause:** `torch.compile` attempting triton compilation (which hangs on Windows/Py3.13).

**Fix:** Ensure `NO_TORCH_COMPILE=1` is set in the environment before launching.

### Audio Drops All Packets / 10s+ Latency

**Cause:** `NO_CUDA_GRAPH=1` is set, disabling the critical GPU optimization.

**Fix:** Remove `NO_CUDA_GRAPH` from all environment variables. Do NOT set it.

### Connect Button Doesn't Work

**Cause 1:** Frontend assets missing — `dist/assets/` is empty.
**Fix:** Delete `dist/` directory and restart server (re-extracts from `dist.tgz`).

**Cause 2:** Chrome microphone permission blocked.
**Fix:** Check Chrome address bar → click lock icon → Microphone → Allow → Refresh.

### `NotAllowedError: Permission denied by system`

**Cause:** Windows OS-level microphone privacy setting is blocking all apps.

**Fix:**
1. Windows Settings → Privacy & Security → Microphone
2. Turn ON "Microphone access" (master toggle)
3. Turn ON "Let desktop apps access your microphone"
4. Refresh the page

### `OSError: [Errno 10048]` Port In Use

**Cause:** A previous Moshi server process is still running on port 8998.

**Fix:**
```powershell
Get-NetTCPConnection -LocalPort 8998 -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

The `setup_and_launch.bat` handles this automatically (Step 0).

### `ModuleNotFoundError: No module named 'torch'`

**Cause:** `pip install sounddevice==0.4.7 --force-reinstall` removed torch as a side effect.

**Fix:**
```powershell
C:\Python313\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Response Gets Slow After 5-10 Minutes

**Cause:** Expected behavior — the LM's KV cache grows with conversation length, causing O(n²) attention scaling.

**Fix:** Refresh the browser page (F5) or reconnect the WebSocket client. This starts a fresh session with empty KV cache. The agentic system does this automatically when `avg_latency > 2500ms`.

### GPU VRAM Exhausted

**Cause:** Other GPU-heavy apps (LM Studio, Stable Diffusion, games) consuming VRAM. Moshi needs ~15GB.

**Fix:** Close other GPU apps before starting Moshi. The `setup_and_launch.bat` checks free VRAM and warns.

### PortAudio / sounddevice `-9999` Errors

**Cause:** The bundled PortAudio DLL in `sounddevice` is incompatible with Python 3.13 on Windows.

**Fix:** This is why the agentic system was built — it uses WebSocket audio streaming instead of PortAudio. The `MoshiAgent` communicates directly via WebSocket, bypassing all system audio driver issues.

---

## Server CLI Arguments

```
python -m moshi.server [OPTIONS]

Options:
  --host TEXT         Bind address (default: localhost)
  --port INT          Port (default: 8998)
  --static TEXT       Path to static frontend, or "none" to disable
  --hf-repo TEXT      HuggingFace repo (default: kyutai/moshiko-pytorch-bf16)
  --device TEXT       Device (default: cuda)
  --half              Use float16 instead of bfloat16 (for older GPUs)
  --ssl TEXT          Path to directory with cert.pem and key.pem
  --cfg-coef FLOAT    CFG coefficient (default: 1.0)
```

---

## Network Diagram

```
┌──────────────────────────────────────────┐
│              Windows Machine              │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │         Moshi Server                │ │
│  │         Port 8998                   │ │
│  │                                     │ │
│  │  ┌─────────┐  ┌──────────────────┐ │ │
│  │  │  Mimi   │  │   Moshi LM (7B)  │ │ │
│  │  │ Codec   │  │   ~15GB VRAM     │ │ │
│  │  └────┬────┘  └────────┬─────────┘ │ │
│  │       │                │            │ │
│  │  ┌────▼────────────────▼─────────┐ │ │
│  │  │    aiohttp Web Server         │ │ │
│  │  │    GET /           (frontend) │ │ │
│  │  │    WS  /api/chat   (voice)   │ │ │
│  │  └──────────────────────────────┘ │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │         Agent API                   │ │
│  │         Port 8999                   │ │
│  │                                     │ │
│  │  ┌──────────────┐ ┌──────────────┐ │ │
│  │  │ MoshiServer  │ │  MoshiAgent  │ │ │
│  │  │ Manager      │ │  (WS Client) │ │ │
│  │  └──────────────┘ └──────────────┘ │ │
│  │                                     │ │
│  │  REST: /api/voice/*                │ │
│  │  WS:   /api/voice/stream           │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │         NVIDIA RTX 3090 Ti          │ │
│  │         24GB GDDR6X                 │ │
│  │         CUDA 12.4                   │ │
│  └─────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

---

## Moshi Limitations (Official)

From the Kyutai Moshi README:

- Windows is **not officially supported** ("we hope it will work but do not provide official support")
- Recommended: Python 3.10-3.12 (3.13 works with `NO_TORCH_COMPILE=1`)
- PyTorch version: tested with 2.2 and 2.4 (we use 2.6 successfully)
- No quantization support for PyTorch backend (quantized models available for Rust/MLX backends only)
- Requires 24GB GPU VRAM for full bf16 model
- Single concurrent session only (server uses `asyncio.Lock`)
