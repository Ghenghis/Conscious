# 🚀 Digital Soul - Deployment Guide

**Production-Ready Deployment for Pi.ai Quality Voice Companion**

## Deployment Overview

Digital Soul can be deployed in multiple configurations:
1. **Local Desktop**: Single-user installation (most common)
2. **Home Server**: Multi-user family deployment
3. **Docker Container**: Isolated, reproducible deployment
4. **Cloud Instance**: Remote access (maintains privacy)

## Quick Deployment (5 minutes)

### Prerequisites

- **OS**: Windows 10/11, macOS 12+, Ubuntu 22.04+
- **Python**: 3.10+
- **GPU** (recommended): NVIDIA RTX 3060+ (12GB VRAM)
- **Storage**: 50GB free space
- **RAM**: 16GB minimum, 32GB recommended

### One-Command Install

```bash
# Clone and install
git clone https://github.com/yourusername/digital-soul.git
cd digital-soul
bash scripts/install.sh

# This script will:
# 1. Check system requirements
# 2. Install dependencies
# 3. Download Moshi model (~7GB)
# 4. Configure initial settings
# 5. Test installation
```

## Production Deployment

### Configuration Files

#### 1. Production Config

**File**: `config/production.yaml`

```yaml
# Digital Soul Production Configuration
# Copy to ~/.soul/config.yaml and customize

# User Settings
user_id: production_user
language: en
wake_word: soul  # or null for always-on

# Voice Engine (Moshi)
moshi:
  model_path: ~/.soul/models/moshi-7b
  device: cuda  # or cpu
  use_quantization: true  # Reduce VRAM (12GB → 3GB)
  latency_target_ms: 200
  enable_duplex: true
  emotion_modulation: true

# Memory System (Mem0)
memory:
  vector_store: qdrant
  embedding_model: all-MiniLM-L6-v2
  storage_path: ~/.soul/memory
  max_memories: 10000
  search_limit: 5
  enable_encryption: true

# Emotion Engine
emotion:
  enable_detection: true
  enable_response: true
  sensitivity: 0.7  # 0.0-1.0
  model: wav2vec2-emotion

# Accent Support
accent:
  default_language: en
  default_accent: US  # US, UK, IN, AU
  enable_voice_cloning: true

# Adapters
adapters:
  - name: coding
    enabled: true
    config: ~/.soul/adapters/coding.yaml
  - name: writing
    enabled: false
  - name: research
    enabled: false

# Performance
performance:
  chunk_size: 1920  # 80ms at 24kHz
  sample_rate: 24000
  use_flash_attention: true
  batch_size: 1

# Privacy
privacy:
  recording: false  # NEVER enable unless debugging
  telemetry: false
  analytics: false
  backup: daily

# Logging
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  path: ~/.soul/logs
  max_size: 100MB
  retention_days: 30

# Security
security:
  memory_encryption: true
  allow_remote: false  # Local only by default
  api_key: null  # For remote access

# Resource Limits
resources:
  max_cpu_percent: 80
  max_memory_mb: 4096
  max_gpu_memory_mb: 12288
```

#### 2. Adapter Configurations

**File**: `~/.soul/adapters/coding.yaml`

```yaml
# Coding Adapter Configuration (Super-Goose Integration)
name: coding
type: autonomous_swarm

integration:
  cli_path: super-goose
  working_directory: ~/projects
  event_server: ws://localhost:8080/events
  log_path: ~/.goose/logs

capabilities:
  - run_tests
  - fix_errors
  - build_project
  - analyze_code
  - deploy
  - generate_docs

intents:
  run_tests:
    - "run tests"
    - "test this"
    - "check if tests pass"
  fix_errors:
    - "fix that error"
    - "fix the bug"
    - "debug this"
  build_project:
    - "build the project"
    - "compile"
  deploy:
    - "deploy"
    - "push to production"

notifications:
  on_completion: true
  on_error: true
  on_milestone: true

preferences:
  auto_fix: false  # Ask before fixing
  verbose: false
```

### System Service (Linux)

**File**: `/etc/systemd/system/digital-soul.service`

```ini
[Unit]
Description=Digital Soul Voice Companion
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/.soul
ExecStart=/usr/bin/python3 -m digital_soul
Restart=always
RestartSec=10

# Environment
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="PYTHONUNBUFFERED=1"

# Resource limits
LimitNOFILE=65536
CPUQuota=80%
MemoryMax=4G

# Security
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
```

**Setup**:
```bash
# Install service
sudo cp digital-soul.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable digital-soul
sudo systemctl start digital-soul

# Check status
sudo systemctl status digital-soul

# View logs
sudo journalctl -u digital-soul -f
```

### Docker Deployment

**File**: `Dockerfile`

```dockerfile
# Digital Soul Docker Image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application
COPY . /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Download Moshi model (cached layer)
RUN python3 scripts/download_moshi.py

# Create volume mount points
VOLUME ["/root/.soul/memory", "/root/.soul/logs", "/root/.soul/backups"]

# Expose ports (if remote access enabled)
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python3 scripts/health_check.py || exit 1

# Run application
CMD ["python3", "-m", "digital_soul"]
```

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  digital-soul:
    build: .
    image: digital-soul:latest
    container_name: digital-soul
    runtime: nvidia  # For GPU support
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - SOUL_CONFIG=/root/.soul/config.yaml
    volumes:
      - ~/.soul/memory:/root/.soul/memory
      - ~/.soul/logs:/root/.soul/logs
      - ~/.soul/backups:/root/.soul/backups
      - ~/.soul/config.yaml:/root/.soul/config.yaml:ro
    devices:
      - /dev/snd:/dev/snd  # Audio devices
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Optional: Qdrant vector database (if not using embedded)
  qdrant:
    image: qdrant/qdrant:latest
    container_name: soul-qdrant
    ports:
      - "6333:6333"
    volumes:
      - ~/.soul/memory/qdrant:/qdrant/storage
    restart: unless-stopped

  # Optional: Neo4j graph database
  neo4j:
    image: neo4j:latest
    container_name: soul-neo4j
    environment:
      - NEO4J_AUTH=soul/encrypted_password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - ~/.soul/memory/neo4j:/data
    restart: unless-stopped
```

**Deploy**:
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f digital-soul

# Stop
docker-compose down

# Update
docker-compose pull
docker-compose up -d
```

## Health Monitoring

**File**: `scripts/health_check.py`

```python
"""
Health check script for monitoring
Returns exit code 0 if healthy, 1 if unhealthy
"""

import asyncio
import sys
from digital_soul import SoulServer
from digital_soul.config import SoulConfig

async def check_health():
    """Run health checks"""
    checks = {
        "config_valid": False,
        "models_loaded": False,
        "memory_accessible": False,
        "audio_devices": False,
        "gpu_available": False,
    }

    try:
        # Check configuration
        config = SoulConfig.from_yaml("~/.soul/config.yaml")
        checks["config_valid"] = True

        # Check models exist
        import os
        model_path = os.path.expanduser(config.moshi.model_path)
        checks["models_loaded"] = os.path.exists(model_path)

        # Check memory system
        memory_path = os.path.expanduser(config.memory.storage_path)
        checks["memory_accessible"] = os.path.exists(memory_path)

        # Check audio devices
        import sounddevice as sd
        devices = sd.query_devices()
        checks["audio_devices"] = len(devices) > 0

        # Check GPU
        import torch
        checks["gpu_available"] = torch.cuda.is_available()

    except Exception as e:
        print(f"Health check error: {e}", file=sys.stderr)
        return False

    # Report status
    all_healthy = all(checks.values())

    if all_healthy:
        print("✓ All systems healthy")
        return True
    else:
        print("✗ Health check failed:")
        for check, status in checks.items():
            symbol = "✓" if status else "✗"
            print(f"  {symbol} {check}")
        return False

if __name__ == "__main__":
    healthy = asyncio.run(check_health())
    sys.exit(0 if healthy else 1)
```

## Monitoring & Metrics

### Prometheus Metrics

**File**: `digital_soul/monitoring/metrics.py`

```python
"""
Prometheus metrics for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Conversation metrics
conversations_total = Counter(
    'soul_conversations_total',
    'Total number of conversations'
)

conversation_turns = Counter(
    'soul_conversation_turns_total',
    'Total number of conversation turns'
)

# Performance metrics
response_latency = Histogram(
    'soul_response_latency_seconds',
    'Response latency in seconds',
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

voice_quality_mos = Gauge(
    'soul_voice_quality_mos',
    'Mean Opinion Score for voice quality'
)

# Emotion metrics
emotions_detected = Counter(
    'soul_emotions_detected_total',
    'Emotions detected',
    ['emotion']
)

emotion_confidence = Histogram(
    'soul_emotion_confidence',
    'Emotion detection confidence',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Memory metrics
memories_stored = Counter(
    'soul_memories_stored_total',
    'Total memories stored'
)

memory_recall_latency = Histogram(
    'soul_memory_recall_latency_seconds',
    'Memory retrieval latency',
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

# System metrics
gpu_memory_usage = Gauge(
    'soul_gpu_memory_bytes',
    'GPU memory usage in bytes'
)

cpu_usage_percent = Gauge(
    'soul_cpu_usage_percent',
    'CPU usage percentage'
)

# Start metrics server
def start_metrics_server(port=9090):
    """Start Prometheus metrics server"""
    start_http_server(port)
    print(f"Metrics server running on http://localhost:{port}/metrics")
```

### Grafana Dashboard

**File**: `monitoring/grafana-dashboard.json`

```json
{
  "dashboard": {
    "title": "Digital Soul Monitoring",
    "panels": [
      {
        "title": "Response Latency (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, soul_response_latency_seconds)"
          }
        ],
        "thresholds": [
          {
            "value": 0.2,
            "color": "green"
          },
          {
            "value": 0.3,
            "color": "yellow"
          },
          {
            "value": 0.5,
            "color": "red"
          }
        ]
      },
      {
        "title": "Voice Quality (MOS)",
        "targets": [
          {
            "expr": "soul_voice_quality_mos"
          }
        ],
        "thresholds": [
          {
            "value": 4.0,
            "color": "green"
          },
          {
            "value": 3.5,
            "color": "yellow"
          },
          {
            "value": 3.0,
            "color": "red"
          }
        ]
      },
      {
        "title": "Emotions Detected",
        "targets": [
          {
            "expr": "rate(soul_emotions_detected_total[5m])"
          }
        ]
      },
      {
        "title": "Memory Recall Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, soul_memory_recall_latency_seconds)"
          }
        ]
      },
      {
        "title": "GPU Memory Usage",
        "targets": [
          {
            "expr": "soul_gpu_memory_bytes / 1024 / 1024 / 1024"
          }
        ]
      }
    ]
  }
}
```

## Backup & Recovery

### Automated Backup

**File**: `scripts/backup.sh`

```bash
#!/bin/bash
# Automated backup script for Digital Soul

SOUL_DIR="$HOME/.soul"
BACKUP_DIR="$SOUL_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="soul_backup_$TIMESTAMP.tar.gz"

echo "Starting backup at $TIMESTAMP..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup critical data
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    "$SOUL_DIR/memory" \
    "$SOUL_DIR/config.yaml" \
    "$SOUL_DIR/adapters" \
    --exclude="$SOUL_DIR/memory/qdrant/*.lock" \
    --exclude="$SOUL_DIR/logs"

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "soul_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)"
```

**Cron schedule** (`crontab -e`):
```bash
# Daily backup at 2 AM
0 2 * * * /home/yourusername/.soul/scripts/backup.sh

# Weekly backup to external drive
0 3 * * 0 cp ~/.soul/backups/soul_backup_*.tar.gz /mnt/external/
```

### Recovery

```bash
# Restore from backup
tar -xzf ~/.soul/backups/soul_backup_20260207_020000.tar.gz -C ~

# Verify
python3 scripts/health_check.py

# Restart
systemctl restart digital-soul
```

## Security Hardening

### 1. Firewall Rules

```bash
# Allow only local connections
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 127.0.0.1  # Localhost only

# If remote access needed (not recommended)
# sudo ufw allow from YOUR_IP_ADDRESS to any port 8765
```

### 2. AppArmor Profile (Linux)

**File**: `/etc/apparmor.d/digital-soul`

```
#include <tunables/global>

/usr/bin/python3 {
  #include <abstractions/base>
  #include <abstractions/python>

  # Allow read access to Soul files
  /home/*/.soul/** r,

  # Allow write to logs and backups
  /home/*/.soul/logs/** w,
  /home/*/.soul/backups/** w,

  # Allow read/write to memory
  /home/*/.soul/memory/** rw,

  # Deny network access
  deny network,

  # Deny execution of other programs
  deny /bin/** x,
  deny /usr/bin/** x,
}
```

## Troubleshooting

### Common Issues

#### 1. High Latency (>200ms)

**Causes**:
- CPU mode instead of GPU
- No model quantization
- Background apps using GPU

**Solutions**:
```yaml
# config.yaml
moshi:
  device: cuda  # Ensure GPU
  use_quantization: true  # Enable 4-bit

performance:
  use_flash_attention: true
```

#### 2. Low Voice Quality

**Causes**:
- Audio device issues
- Low sample rate
- Compression artifacts

**Solutions**:
```bash
# Test audio devices
python3 scripts/test_audio.py

# Adjust quality
# config.yaml
moshi:
  sample_rate: 24000  # Higher = better quality
  chunk_size: 1920  # 80ms chunks
```

#### 3. Memory Errors

**Causes**:
- Database corruption
- Disk full
- Permission issues

**Solutions**:
```bash
# Check disk space
df -h ~/.soul

# Verify database
python3 scripts/verify_memory.py

# Rebuild if needed
python3 scripts/rebuild_memory.py
```

## Performance Tuning

### GPU Optimization

```python
# digital_soul/config.py
# Add to production config

# For RTX 3060 (12GB VRAM)
moshi:
  use_quantization: true  # 4-bit quantization
  batch_size: 1

# For RTX 4090 (24GB VRAM)
moshi:
  use_quantization: false  # Full precision
  batch_size: 2  # Process multiple inputs
```

### CPU Optimization

```yaml
# For CPU-only systems
moshi:
  device: cpu
  threads: 8  # Match CPU cores
  use_quantization: true  # Reduce memory

memory:
  embedding_model: all-MiniLM-L6-v2  # Lightweight
```

## Update Procedure

```bash
# 1. Backup current installation
bash scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Run migrations (if needed)
python3 scripts/migrate.py

# 5. Test
python3 scripts/health_check.py

# 6. Restart
systemctl restart digital-soul

# 7. Verify
systemctl status digital-soul
```

---

## Production Checklist

Before deploying to production:

- [ ] Configuration reviewed and customized
- [ ] All tests passing (see TEST_SPECIFICATIONS.md)
- [ ] Performance benchmarks met
- [ ] Security hardening applied
- [ ] Backup system configured
- [ ] Monitoring enabled
- [ ] Health checks passing
- [ ] Privacy settings verified
- [ ] Documentation reviewed
- [ ] User training completed

**Digital Soul is ready for production deployment!** 🚀
