# Super-Goose Integration Guide

> Complete guide for integrating Conscious voice capabilities into Super-Goose via the Moshi Agent API. Written for Claude/Windsurf AI assistants.

---

## Quick Start (For Claude/Windsurf)

### 1. Start Everything with One Call

```python
import sys
sys.path.insert(0, r"D:\conscious\src")

from conscious.voice import MoshiAgentAPI

api = MoshiAgentAPI(api_port=8999)
await api.start_all()  # launches Moshi server + loads model + connects agent
```

This single call:
- Kills any stale process on port 8998
- Checks GPU VRAM (warns if <14GB free)
- Launches `python -m moshi.server` with correct env vars
- Waits up to 5 minutes for the 15GB model to load
- Connects the autonomous WebSocket client
- Starts latency monitoring and auto-reconnect

### 2. Send Audio

```python
import numpy as np

# From any source — mic, file, TTS, or generated
pcm = np.zeros(24000, dtype=np.float32)  # 1 second of silence
await api.agent.send_audio(pcm)
```

### 3. Receive Audio and Text

```python
async def on_audio(pcm: np.ndarray):
    """Called when Moshi speaks — pcm is float32 mono 24kHz."""
    # Play via speakers, pipe to another system, save to file, etc.
    print(f"Received {len(pcm)} audio samples")

async def on_text(text: str):
    """Called for each text token Moshi produces."""
    print(f"Moshi says: {text}", end="", flush=True)

api.agent.on_audio_received = on_audio
api.agent.on_text_received = on_text
```

### 4. Check Status

```python
status = api.get_status()
# {
#   "server": {"status": "ready", "url": "http://localhost:8998", ...},
#   "agent": {"state": "streaming", "is_connected": true, "stats": {...}},
#   "recent_text": ["Hello", " how", " are", " you"]
# }
```

### 5. Stop Everything

```python
await api.stop_all()
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPER-GOOSE                             │
│                                                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────┐ │
│  │ Coding  │  │ Research │  │ Chat UI   │  │ Other      │ │
│  │ Agent   │  │ Agent    │  │           │  │ Agents     │ │
│  └────┬────┘  └────┬─────┘  └─────┬─────┘  └─────┬──────┘ │
│       │            │              │               │         │
│       └────────────┴──────┬───────┴───────────────┘         │
│                           │                                  │
│              ┌────────────▼────────────┐                    │
│              │   Integration Layer     │                    │
│              │                         │                    │
│              │  Option A: Python API   │                    │
│              │  Option B: HTTP REST    │                    │
│              │  Option C: WebSocket    │                    │
│              └────────────┬────────────┘                    │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
               ┌────────────▼────────────┐
               │    MoshiAgentAPI        │
               │    Port 8999            │
               │                         │
               │  GET  /api/voice/status │
               │  POST /api/voice/start  │
               │  POST /api/voice/audio  │
               │  WS   /api/voice/stream │
               └────────────┬────────────┘
                            │
               ┌────────────▼────────────┐
               │    Moshi Server         │
               │    Port 8998            │
               │    (PyTorch + CUDA)     │
               │    RTX 3090 Ti 24GB     │
               └─────────────────────────┘
```

---

## Three Integration Options

### Option A: Direct Python Import (Recommended)

Best for Super-Goose modules running in the same Python process.

```python
import sys
sys.path.insert(0, r"D:\conscious\src")

from conscious.voice import MoshiAgentAPI, MoshiAgent, MoshiServerManager

# Full stack
api = MoshiAgentAPI()
await api.start_all()

# Or individual components
manager = MoshiServerManager()
await manager.start()
await manager.wait_ready()

agent = MoshiAgent()
await agent.connect()
await agent.send_audio(pcm_data)
```

**Pros:** Lowest latency, full control, async callbacks
**Cons:** Must share Python process

### Option B: HTTP REST API

Best for language-agnostic integration or separate processes.

```bash
# Start the API server
C:\Python313\python.exe -m conscious.voice.agent_api --auto-start --api-port 8999
```

Then from any language:

```bash
# Check status
curl http://localhost:8999/api/voice/status

# Start everything
curl -X POST http://localhost:8999/api/voice/start

# Send audio (base64 PCM float32 mono 24kHz)
curl -X POST http://localhost:8999/api/voice/audio \
  -H "Content-Type: application/json" \
  -d '{"audio": "<base64_encoded_pcm>"}'

# Force reconnect (reset KV cache, fix latency)
curl -X POST http://localhost:8999/api/voice/reconnect

# Stop
curl -X POST http://localhost:8999/api/voice/stop
```

**Pros:** Language-agnostic, process isolation, simple HTTP
**Cons:** Higher latency for audio, base64 overhead

### Option C: WebSocket Streaming

Best for real-time bidirectional audio streaming.

```javascript
// JavaScript example
const ws = new WebSocket("ws://localhost:8999/api/voice/stream");

// Send audio (binary float32 PCM)
ws.send(pcmFloat32ArrayBuffer);

// Receive responses
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === "audio") {
        const pcm = base64ToFloat32Array(msg.data);
        playAudio(pcm);
    } else if (msg.type === "text") {
        appendText(msg.data);
    }
};

// Send commands
ws.send(JSON.stringify({ command: "reconnect" }));
ws.send(JSON.stringify({ command: "status" }));
ws.send(JSON.stringify({ command: "silence", duration_ms: 80 }));
```

**Pros:** Real-time, bidirectional, efficient for streaming
**Cons:** More complex client code

---

## API Reference

### REST Endpoints

#### `GET /api/voice/status`

Returns combined server and agent status.

**Response:**
```json
{
    "server": {
        "status": "ready",
        "url": "http://localhost:8998",
        "ws_url": "ws://localhost:8998/api/chat"
    },
    "agent": {
        "state": "streaming",
        "is_connected": true,
        "stats": {
            "total_audio_sent": 48000,
            "total_audio_received": 156,
            "total_text_tokens": 42,
            "reconnect_count": 0,
            "current_latency_ms": 187.3,
            "avg_latency_ms": 195.1
        }
    },
    "recent_text": ["Hello", " how", " are", " you"]
}
```

#### `POST /api/voice/start`

Starts the full agentic stack: server + model load + agent connection.

**Response:**
```json
{
    "success": true,
    "server": { "status": "ready", ... },
    "agent": { "state": "streaming", ... }
}
```

**Notes:**
- Takes 2-3 minutes (model loading)
- Automatically kills stale port 8998 processes
- Checks GPU VRAM before launching

#### `POST /api/voice/stop`

Stops agent and server.

**Response:**
```json
{ "success": true }
```

#### `POST /api/voice/connect`

Connects agent to an already-running Moshi server.

**Response:**
```json
{ "success": true, "state": "streaming" }
```

#### `POST /api/voice/disconnect`

Disconnects agent from server (server keeps running).

**Response:**
```json
{ "success": true, "state": "disconnected" }
```

#### `POST /api/voice/reconnect`

Force disconnects and reconnects. Resets server KV cache, restoring low latency.

**Response:**
```json
{ "success": true, "state": "streaming" }
```

#### `POST /api/voice/audio`

Send audio to Moshi for processing.

**Request:**
```json
{
    "audio": "<base64_encoded_float32_pcm>"
}
```

Audio must be:
- **Format:** float32 PCM
- **Sample rate:** 24000 Hz
- **Channels:** 1 (mono)
- **Encoding:** base64 of raw bytes

**Response:**
```json
{
    "success": true,
    "samples_sent": 24000,
    "duration_ms": 1000.0
}
```

#### `WS /api/voice/stream`

Bidirectional WebSocket for real-time audio streaming.

**Client → Server:**
- Binary frames: raw float32 PCM audio (24kHz mono)
- Text frames: JSON commands

**Server → Client:**
- Text frames: JSON messages

**Commands (text frames):**
```json
{ "command": "reconnect" }
{ "command": "status" }
{ "command": "silence", "duration_ms": 80 }
```

**Response messages:**
```json
{ "type": "audio", "data": "<base64_pcm>", "samples": 1920 }
{ "type": "text", "data": "Hello" }
```

---

## Audio Format Specification

All audio in the system uses this format:

| Property | Value |
|----------|-------|
| Sample Rate | 24000 Hz |
| Channels | 1 (mono) |
| Bit Depth | 32-bit float |
| PCM Range | -1.0 to 1.0 |
| Frame Size | 1920 samples (80ms) |
| Wire Format (WS to Moshi) | Opus encoded via `sphn` |
| Wire Format (API) | Base64 of raw float32 bytes |

### Python Audio Helpers

```python
import numpy as np
import base64

# Generate 1 second of silence
silence = np.zeros(24000, dtype=np.float32)

# Load from WAV file (must be 24kHz mono)
import wave
with wave.open("input.wav", "rb") as wf:
    pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    pcm = pcm.astype(np.float32) / 32768.0  # normalize to [-1, 1]

# Encode for HTTP API
audio_b64 = base64.b64encode(pcm.tobytes()).decode()

# Decode from HTTP API response
pcm_bytes = base64.b64decode(audio_b64)
pcm = np.frombuffer(pcm_bytes, dtype=np.float32)
```

---

## Configuration Reference

### ServerManagerConfig

```python
@dataclass
class ServerManagerConfig:
    host: str = "localhost"           # Moshi server bind address
    port: int = 8998                  # Moshi server port
    python_exe: str = r"C:\Python313\python.exe"
    health_check_interval: float = 5.0     # seconds
    health_check_timeout: float = 3.0      # seconds
    max_restart_attempts: int = 5
    restart_backoff_base: float = 2.0      # exponential backoff
    restart_backoff_max: float = 60.0      # max backoff seconds
    min_vram_mb: int = 14000               # minimum free GPU VRAM
    env_vars: dict = {
        "NO_TORCH_COMPILE": "1",
        "TORCHDYNAMO_DISABLE": "1",
        "PYTHONUNBUFFERED": "1",
    }
```

### AgentConfig

```python
@dataclass
class AgentConfig:
    server_ws_url: str = "ws://localhost:8998/api/chat"
    sample_rate: int = 24000
    latency_threshold_ms: float = 2500.0   # auto-reconnect threshold
    latency_check_window: int = 10         # rolling average window
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_backoff_base: float = 1.5
    reconnect_backoff_max: float = 30.0
    audio_send_interval_ms: float = 80.0   # frame interval
    silence_frame_size: int = 1920         # samples per silence frame
```

---

## Windsurf/Claude Implementation Notes

### For Claude AI Assistants Building on This

1. **Always use full Python path:** `C:\Python313\python.exe` — Python is NOT in PATH
2. **Never set `NO_CUDA_GRAPH`** — CUDA Graphs are required for real-time audio
3. **Always set `NO_TORCH_COMPILE=1`** — triton is broken on Python 3.13/Windows
4. **The Moshi server accepts only ONE client** — it uses `asyncio.Lock`
5. **`moshi/server.py` has bare `main()` call at module level** — cannot import it directly, must launch via subprocess or `python -m moshi.server`
6. **Model loading takes 2-3 minutes** — the 15GB model loads into GPU VRAM
7. **Conversations degrade over time** — KV cache grows, latency increases, reconnect to reset

### Common Patterns

```python
# Pattern: Autonomous voice loop with latency management
async def voice_loop():
    api = MoshiAgentAPI()
    await api.start_all()

    while True:
        # Get audio from some source
        audio = await get_audio_from_source()
        await api.agent.send_audio(audio)

        # Status check
        if api.agent.stats.avg_latency_ms > 2000:
            # Agent will auto-reconnect, but you can force it
            await api.agent.disconnect()
            await asyncio.sleep(1)
            await api.agent.connect()

        await asyncio.sleep(0.08)  # 80ms frame interval
```

```python
# Pattern: HTTP-based integration from separate process
import requests

# Start everything
requests.post("http://localhost:8999/api/voice/start")

# Check readiness
while True:
    status = requests.get("http://localhost:8999/api/voice/status").json()
    if status["agent"]["is_connected"]:
        break
    time.sleep(2)

# Send audio
audio_b64 = base64.b64encode(pcm.tobytes()).decode()
requests.post("http://localhost:8999/api/voice/audio", json={"audio": audio_b64})

# Force reconnect when latency is high
requests.post("http://localhost:8999/api/voice/reconnect")
```

---

## Error Handling

### Server Won't Start

```python
manager = MoshiServerManager()
await manager.start()
ready = await manager.wait_ready(timeout=300)
if not ready:
    print(f"Server status: {manager.status}")
    # Check: Is GPU VRAM free? Is port 8998 available?
    # Server manager logs all issues to Python logging
```

### Agent Can't Connect

```python
agent = MoshiAgent()
success = await agent.connect()
if not success:
    print(f"Agent state: {agent.state}")
    # Check: Is server running and ready?
    # Check: Is port 8998 accessible?
```

### Latency Too High

```python
# Option 1: Let auto-reconnect handle it (default behavior)
# Agent monitors latency and reconnects when avg > 2500ms

# Option 2: Manual reconnect via API
requests.post("http://localhost:8999/api/voice/reconnect")

# Option 3: Adjust threshold
config = AgentConfig(latency_threshold_ms=1500.0)  # more aggressive
agent = MoshiAgent(config)
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | 2.6.0+cu124 | PyTorch with CUDA 12.4 |
| `moshi` | latest | Kyutai Moshi voice AI (includes `sphn`) |
| `aiohttp` | latest | HTTP server + WebSocket client |
| `numpy` | latest | Audio data handling |
| `sounddevice` | 0.4.7+ | Legacy audio I/O (not used by agentic system) |

### Install Command

```bash
C:\Python313\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
C:\Python313\Scripts\pip.exe install moshi aiohttp numpy
```

---

## Ports Summary

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| 8998 | Moshi Server | HTTP + WS | Voice AI model server |
| 8999 | Agent API | HTTP + WS | Super-Goose integration API |
