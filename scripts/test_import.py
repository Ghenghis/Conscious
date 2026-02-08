"""Quick smoke test: verify config loading and basic imports work."""

import sys
sys.path.insert(0, "src")

print("=" * 60)
print("CONSCIOUS - Import & Config Smoke Test")
print("=" * 60)

# 1. Config
from conscious.config import load_config, get_config_value

config = load_config()
print("[PASS] Config loaded")
print(f"  Personality: {get_config_value(config, 'personality.active', 'unknown')}")
print(f"  Device:      {get_config_value(config, 'moshi.device', 'unknown')}")
greeting = get_config_value(config, "greeting.first_time", "")
print(f"  Greeting:    {greeting[:50].strip()}...")

# 2. Voice engine (requires moshi package)
try:
    from conscious.voice.moshi_engine import MoshiEngine, MoshiConfig
    print("[PASS] MoshiEngine imported")
except ImportError as e:
    print(f"[SKIP] MoshiEngine — moshi not installed ({e})")

# 3. Audio stream (requires sounddevice)
try:
    from conscious.voice.audio_stream import AudioStream, AudioStreamConfig
    print("[PASS] AudioStream imported")
except ImportError as e:
    print(f"[SKIP] AudioStream — sounddevice not installed ({e})")

# 4. Server
try:
    from conscious.server import ConsciousServer
    print("[PASS] ConsciousServer imported")
except ImportError as e:
    print(f"[SKIP] ConsciousServer — missing dependency ({e})")

print()
print("Core config system works. Install deps to unlock full imports:")
print("  pip install -e .[all]")
print("=" * 60)
