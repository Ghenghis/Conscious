# 🚀 Getting Started with Digital Soul

**Build your own Pi.ai-quality voice companion in 16 weeks**

This guide will get you from zero to your first conversation with Digital Soul.

## Prerequisites

### Hardware Requirements

**Minimum (Works, but slower)**:
- CPU: Modern x86_64 or ARM64
- RAM: 16GB
- GPU: None (CPU-only mode, ~500ms latency)
- Storage: 20GB free space

**Recommended (Good experience)**:
- CPU: Intel i5/AMD Ryzen 5 or better
- RAM: 32GB
- GPU: NVIDIA RTX 3060 Ti (12GB VRAM)
- Storage: 50GB SSD

**Optimal (Pi.ai quality)**:
- CPU: Intel i7/AMD Ryzen 7 or better
- RAM: 32GB+
- GPU: NVIDIA RTX 4060 Ti (16GB VRAM) or better
- Storage: 100GB NVMe SSD

### Software Requirements

- **OS**: Windows 10/11, macOS 12+, or Linux (Ubuntu 22.04+)
- **Python**: 3.10 or newer
- **CUDA**: 11.8+ (if using GPU)
- **Git**: For cloning repository

## Quick Start (30 minutes)

### Step 1: Clone Repository

```bash
# Clone Digital Soul
git clone https://github.com/yourusername/digital-soul.git
cd digital-soul

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA (for GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or install CPU-only version
pip install torch torchvision torchaudio
```

### Step 3: Download Moshi Model

```bash
# Download Moshi 7B model (~7GB, one-time)
python scripts/download_moshi.py

# This will download to ~/.soul/models/moshi-7b/
# Takes 10-30 minutes depending on internet speed
```

### Step 4: Initial Configuration

```bash
# Run configuration wizard
python scripts/configure.py
```

This will ask you:
- What to call you
- Wake word preference (or always-on)
- GPU vs CPU mode
- Privacy preferences

Creates: `~/.soul/config.yaml`

### Step 5: Test Audio

```bash
# Test microphone and speakers
python scripts/test_audio.py
```

This will:
- Check microphone works
- Check speakers work
- Test audio quality
- Recommend settings

### Step 6: Launch Digital Soul!

```bash
# Start Digital Soul
python -m digital_soul
```

You should see:
```
🌌 Digital Soul v0.1.0
✓ Moshi loaded (GPU mode)
✓ Memory system initialized
✓ Audio devices ready
✓ Soul is alive!

Listening... (say "Soul" to wake, or just start talking)
```

### Step 7: First Conversation

```
You: "Soul, can you hear me?"

Soul: "Yes, I can hear you perfectly. What should I call you?"

You: "Call me Alex."

Soul: "Nice to meet you, Alex. I'm here to help with whatever
      you're working on. What brings you here today?"
```

**Congratulations! You just had your first conversation with Digital Soul! 🎉**

---

## Configuration

### Basic Config (~/.soul/config.yaml)

```yaml
# User settings
user_id: alex
wake_word: soul  # or null for always-on

# Voice settings
moshi:
  device: cuda  # or cpu
  model: moshi-7b
  latency_target_ms: 200

# Memory settings
memory:
  storage: ~/.soul/memory
  encryption: true
  max_memories: 10000

# Privacy settings
privacy:
  recording: false  # Never record unless debugging
  telemetry: false
  backup: daily
```

### Advanced Config

```yaml
# Emotion settings
emotion:
  detection: true
  response_modulation: true
  sensitivity: 0.7

# Voice customization
voice:
  speed: 1.0      # 0.5-1.5
  pitch: 1.0      # 0.5-1.5
  style: natural  # natural, professional, casual

# Performance
performance:
  chunk_size: 1024
  sample_rate: 24000
  use_flash_attention: true
  quantization: 4bit  # 4bit, 8bit, or none
```

---

## Common Issues & Solutions

### Issue: "CUDA out of memory"

**Solution 1**: Use smaller model
```yaml
moshi:
  model: moshi-3b  # Instead of moshi-7b
```

**Solution 2**: Enable quantization
```yaml
performance:
  quantization: 4bit  # Reduces VRAM usage
```

**Solution 3**: Use CPU mode
```yaml
moshi:
  device: cpu
```

### Issue: "Microphone not detected"

**Solution**:
```bash
# List audio devices
python scripts/list_audio_devices.py

# Set specific device in config
audio:
  input_device: "USB Microphone"
```

### Issue: "High latency (>500ms)"

**Causes & Solutions**:

1. **CPU mode**: Switch to GPU if possible
2. **Large model**: Use moshi-3b instead of moshi-7b
3. **No quantization**: Enable 4-bit quantization
4. **Background apps**: Close other GPU-intensive apps

```bash
# Check performance
python scripts/benchmark.py
```

### Issue: "Voice sounds robotic"

**Solution**: Tune voice parameters
```yaml
voice:
  speed: 0.95     # Slightly slower
  pitch: 1.05     # Slightly higher
  emotion_modulation: true  # Enable emotion
```

---

## Next Steps

### 1. Setup Your First Adapter

Let's connect Digital Soul to a project:

**For Coding (Super-Goose)**:
```bash
python scripts/setup_adapter.py --type coding --path ~/goose
```

**For Writing (Obsidian)**:
```bash
python scripts/setup_adapter.py --type writing --path ~/Documents/Vault
```

**For Research (Zotero)**:
```bash
python scripts/setup_adapter.py --type research --library ~/Zotero
```

### 2. Customize Voice Response

Edit emotion responses:
```yaml
emotion:
  emotions:
    frustrated:
      tone: "very calm and supportive"
      speed: 0.80  # Even slower
      examples:
        - "I'm here, let's work through this together."
        - "Take a breath, we'll figure it out."
```

### 3. Train Your Soul

Have conversations! Soul learns from:
- Your preferences ("I prefer dark mode")
- Your patterns (when you work, how you communicate)
- Your emotional responses
- Your project context

**The more you talk, the better Soul understands you.**

### 4. Manage Memory

```bash
# View all memories
python scripts/view_memories.py

# Search memories
python scripts/search_memories.py "preferences"

# Delete memory
python scripts/delete_memory.py <memory_id>

# Export memories (backup)
python scripts/export_memories.py ~/backup.json
```

---

## Testing Your Setup

### Voice Quality Test

```bash
python scripts/test_voice_quality.py
```

This will:
- Generate test phrases
- Measure MOS (Mean Opinion Score)
- Compare to baseline
- Suggest improvements

**Target**: MOS >4.0 (Pi.ai is ~4.3)

### Latency Test

```bash
python scripts/test_latency.py
```

This will:
- Measure end-to-end latency
- Identify bottlenecks
- Suggest optimizations

**Target**: <200ms (95th percentile)

### Memory Test

```bash
python scripts/test_memory.py
```

This will:
- Store test memories
- Test recall accuracy
- Measure retrieval speed

**Target**: >95% accuracy, <50ms retrieval

---

## Development Mode

Want to contribute or customize?

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with debug logging
python -m digital_soul --debug

# Profile performance
python scripts/profile.py
```

---

## Troubleshooting

### Full Diagnostic

```bash
# Run complete system check
python scripts/diagnose.py
```

This checks:
- Python version
- Dependencies
- GPU availability
- Audio devices
- Model files
- Config validity
- Network isolation

### Enable Debug Logging

```yaml
log_level: DEBUG
```

Then check logs:
```bash
tail -f ~/.soul/logs/soul.log
```

### Reset Everything

```bash
# Backup first!
cp -r ~/.soul ~/.soul.backup

# Reset configuration
rm ~/.soul/config.yaml
python scripts/configure.py

# Reset memories (careful!)
rm -rf ~/.soul/memory/*
```

---

## Getting Help

### Documentation
- [Architecture Deep Dive](ARCHITECTURE.md)
- [Adapter Development Guide](docs/ADAPTER_GUIDE.md)
- [Memory System Guide](docs/MEMORY_GUIDE.md)
- [Voice Tuning Guide](docs/VOICE_TUNING.md)

### Community
- Discord: [Join here]
- GitHub Discussions: [Ask questions]
- GitHub Issues: [Report bugs]

### FAQ
- [Frequently Asked Questions](docs/FAQ.md)
- [Performance Optimization](docs/OPTIMIZATION.md)
- [Privacy & Security](docs/PRIVACY.md)

---

## What's Next?

You're ready to:

1. **Talk to Soul**: Have natural conversations
2. **Connect Projects**: Setup adapters for your work
3. **Customize**: Tune voice and emotion responses
4. **Contribute**: Build custom adapters or improve core

**Remember**: The goal is Pi.ai quality, but local and yours.

---

**Welcome to Digital Soul. Your companion for the digital age.** 🌌
