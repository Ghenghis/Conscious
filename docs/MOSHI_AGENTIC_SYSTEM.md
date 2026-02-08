# Moshi Agentic Voice System

> Autonomous voice AI architecture for Conscious, designed for fully headless operation within the Super-Goose framework. No browser required.

---

## Overview

The Moshi Agentic Voice System replaces the browser-based Moshi web UI with a fully autonomous Python-based client. It manages the entire voice pipeline programmatically — server lifecycle, WebSocket communication, audio streaming, latency monitoring, and self-healing reconnection.

**Key Principle:** Everything that previously required human interaction (clicking Connect, refreshing the page, restarting the server) is now automated.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        SUPER-GOOSE                               │
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│   │  Text Input   │    │  Audio Input  │    │  Other Agents    │  │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────────┘  │
│          │                   │                    │              │
│          └───────────────────┼────────────────────┘              │
│                              │                                   │
│                    ┌─────────▼──────────┐                       │
│                    │  MoshiAgentAPI     │  ← HTTP :8999         │
│                    │  (Orchestrator)    │  ← WS :8999/stream    │
│                    └────┬─────────┬────┘                        │
│                         │         │                              │
│              ┌──────────▼──┐ ┌────▼──────────┐                  │
│              │ MoshiAgent  │ │ MoshiServer   │                  │
│              │ (WS Client) │ │ Manager       │                  │
│              └──────┬──────┘ └────┬──────────┘                  │
│                     │             │                              │
└─────────────────────┼─────────────┼──────────────────────────────┘
                      │             │
                      │   ┌─────────▼──────────┐
                      │   │ subprocess:        │
                      │   │ python -m          │
                      │   │ moshi.server       │
                      │   │ (PyTorch + CUDA)   │
                      │   └─────────┬──────────┘
                      │             │
                      └──► WS :8998/api/chat ◄─┘
                           (Opus audio + text)
```

---

## Components

### 1. MoshiServerManager (`server_manager.py`)

Manages the Moshi server process lifecycle autonomously.

```python
from conscious.voice import MoshiServerManager, ServerManagerConfig

config = ServerManagerConfig(
    host="localhost",
    port=8998,
    python_exe=r"C:\Python313\python.exe",
    health_check_interval=5.0,     # seconds between health checks
    max_restart_attempts=5,        # max auto-restarts before giving up
    restart_backoff_base=2.0,      # exponential backoff base
    min_vram_mb=14000,             # minimum free GPU VRAM
)

manager = MoshiServerManager(config)
await manager.start()              # kills stale port, checks VRAM, launches
await manager.wait_ready()         # blocks until model loaded (~2-3 min)
await manager.restart()            # kill + relaunch
await manager.stop()               # graceful shutdown
```

**Lifecycle States:**

```
STOPPED ──► STARTING ──► LOADING_MODEL ──► READY
   ▲                                         │
   │         RESTARTING ◄── ERROR ◄──────────┘
   │              │                  (crash/health fail)
   └──────────────┘
```

**Features:**
- Auto-kills stale processes on port 8998 before starting
- GPU VRAM pre-flight check (warns if <14GB free)
- Reads server stdout to detect model load completion
- HTTP health polling every 5 seconds
- Auto-restart on crash with exponential backoff
- Status change callbacks for integration

### 2. MoshiAgent (`moshi_agent.py`)

Autonomous WebSocket client that replaces the browser entirely.

```python
from conscious.voice import MoshiAgent, AgentConfig

config = AgentConfig(
    server_ws_url="ws://localhost:8998/api/chat",
    sample_rate=24000,
    latency_threshold_ms=2500.0,   # auto-reconnect when avg > 2.5s
    latency_check_window=10,       # rolling window for latency avg
    auto_reconnect=True,
    max_reconnect_attempts=10,
)

agent = MoshiAgent(config)
agent.on_audio_received = handle_audio   # async fn(pcm: np.ndarray)
agent.on_text_received = handle_text     # async fn(text: str)

await agent.connect()
await agent.send_audio(pcm_data)         # float32 mono 24kHz
await agent.send_silence(80)             # keep-alive silence frame
await agent.disconnect()
```

**States:**

```
DISCONNECTED ──► CONNECTING ──► HANDSHAKE ──► STREAMING
      ▲                                          │
      │          RECONNECTING ◄──────────────────┘
      │               │              (latency > threshold
      └───────────────┘               or connection lost)
```

**Features:**
- Full Moshi binary protocol (handshake, opus audio, text tokens)
- Opus encode/decode via `sphn` library
- Latency monitoring with rolling average
- Auto-reconnect resets server KV cache (restores instant responses)
- Exponential backoff on connection failures
- Pluggable callbacks for audio/text/state changes

### 3. MoshiAgentAPI (`agent_api.py`)

HTTP + WebSocket API that orchestrates both components for Super-Goose.

```python
from conscious.voice import MoshiAgentAPI

api = MoshiAgentAPI(api_port=8999)
await api.start_all()    # start server + wait for model + connect agent
# ... Super-Goose sends audio via HTTP or WebSocket ...
await api.stop_all()     # clean shutdown
```

**REST Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/voice/status` | Combined server + agent status |
| `POST` | `/api/voice/start` | Start server + connect agent |
| `POST` | `/api/voice/stop` | Stop everything |
| `POST` | `/api/voice/connect` | Connect agent to running server |
| `POST` | `/api/voice/disconnect` | Disconnect agent |
| `POST` | `/api/voice/reconnect` | Force reconnect (reset KV cache) |
| `POST` | `/api/voice/audio` | Send base64-encoded PCM audio |
| `WS` | `/api/voice/stream` | Bidirectional audio streaming |

---

## Moshi WebSocket Protocol

Reverse-engineered from `moshi/server.py`. This is the binary protocol between the agent and the Moshi server.

### Connection Flow

```
Agent                          Moshi Server
  │                                │
  │──── WS Connect ───────────────►│
  │     ws://localhost:8998        │
  │     /api/chat                  │
  │                                │
  │◄─── 0x00 (handshake) ────────│  Server sends single byte
  │                                │
  │──── 0x01 + opus ─────────────►│  Agent sends audio
  │◄─── 0x01 + opus ─────────────│  Server sends audio response
  │◄─── 0x02 + utf8 ─────────────│  Server sends text token
  │                                │
  │  ... continuous bidirectional   │
  │  ... streaming ...              │
  │                                │
  │──── WS Close ─────────────────►│  Resets KV cache
  │                                │
```

### Message Format

All messages are binary WebSocket frames. First byte = message type.

| Byte | Direction | Format | Description |
|------|-----------|--------|-------------|
| `0x00` | Server → Client | 1 byte only | Handshake signal |
| `0x01` | Bidirectional | `0x01` + opus bytes | Opus-encoded audio at 24kHz |
| `0x02` | Server → Client | `0x02` + UTF-8 text | Text token (word fragment) |

### Audio Format

- **Sample rate:** 24000 Hz
- **Channels:** 1 (mono)
- **Encoding:** Opus (via `sphn` library)
- **Frame size:** `sample_rate / frame_rate` samples per frame
- **PCM format:** float32

### Server Constraints

- **Single session only** — server uses `asyncio.Lock`, only one client at a time
- **First audio frame is skipped** — server resets mimi streaming after first frame
- **KV cache grows with conversation** — latency increases over time
- **Reconnecting resets KV cache** — close WebSocket + reconnect = fresh session

---

## Latency Management

The Moshi LM accumulates context tokens for every second of conversation. This causes O(n²) attention scaling and progressive latency degradation.

### Detection

```python
# Agent monitors rolling average latency
latency_threshold_ms = 2500.0    # trigger reconnect above this
latency_check_window = 10        # rolling window size
```

### Auto-Recovery

When average latency exceeds the threshold:

1. Agent closes WebSocket connection
2. Waits brief backoff period
3. Reconnects to server
4. Server creates new session with fresh KV cache
5. Latency drops back to baseline (~100-200ms)

### Typical Latency Profile

```
Latency (ms)
  3000 │                              ╱ ← auto-reconnect triggers
       │                            ╱
  2000 │                          ╱
       │                        ╱
  1000 │                     ╱
       │                  ╱
   200 │──────────────╱                    ──────────── ← fresh session
       │
     0 └──────────────────────────────────────────────────
       0        5        10       15       20       25  (minutes)
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Value | Why |
|----------|-------|-----|
| `NO_TORCH_COMPILE` | `1` | Disables `torch.compile` — triton incompatible with Python 3.13/Windows |
| `TORCHDYNAMO_DISABLE` | `1` | Safety net for torch dynamo |

### DO NOT SET

| Variable | Why NOT |
|----------|---------|
| `NO_CUDA_GRAPH` | CUDA Graphs work on Python 3.13 and are **required** for real-time audio performance |

### Python Path

Python 3.13 is installed at `C:\Python313\python.exe` and is **NOT in system PATH**. All scripts use full paths.

---

## File Structure

```
src/conscious/voice/
├── __init__.py           # Package exports (MoshiAgent, MoshiServerManager, MoshiAgentAPI)
├── moshi_agent.py        # Autonomous WebSocket client
├── server_manager.py     # Server lifecycle management
├── agent_api.py          # HTTP/WS API for Super-Goose
├── moshi_engine.py       # Direct model wrapper (in-process, legacy)
└── audio_stream.py       # System audio I/O via sounddevice (legacy)

scripts/
├── launch_moshi_server.py    # Subprocess launcher with env vars
├── test_moshi_api.py         # API test script

setup_and_launch.bat          # One-click server launch (foolproof)
setup_and_launch.ps1          # PowerShell equivalent
```

---

## Troubleshooting Reference

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Server hangs on model load | `torch.compile` crashes with triton on Py3.13 | Set `NO_TORCH_COMPILE=1` |
| Audio drops all packets | `NO_CUDA_GRAPH=1` disables perf optimization | Remove `NO_CUDA_GRAPH` env var |
| Connect button doesn't work | `dist/assets/` empty (corrupted extraction) | Delete `dist/`, re-extract from `dist.tgz` |
| `NotAllowedError: Permission denied by system` | Windows mic privacy blocking | Settings → Privacy → Microphone → ON |
| `OSError: [Errno 10048]` | Port 8998 in use by stale process | Server manager auto-kills stale port |
| `ModuleNotFoundError: No module named 'torch'` | pip removed torch during sounddevice install | Reinstall: `pip install torch --index-url .../cu124` |
| Latency increases over 5-10 min | KV cache grows with conversation length | Auto-reconnect resets cache |
| PortAudio `-9999` errors | sounddevice DLL incompatible with Py3.13 | Use WebSocket audio instead (agentic client) |

---

## Performance Notes

- **GPU:** RTX 3090 Ti (24GB VRAM) — uses ~15GB for the 7B model
- **PyTorch:** 2.6.0+cu124 with CUDA 12.4
- **Real-time factor:** Must stay under 1.0x for real-time audio
- **CUDA Graphs:** Critical optimization — do NOT disable
- **torch.compile:** Disabled (triton incompatible) — causes ~20% perf hit but acceptable with CUDA Graphs
