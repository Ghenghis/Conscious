# 🧪 Digital Soul - Test Specifications

**Comprehensive Testing Strategy for Pi.ai Quality Assurance**

## Testing Philosophy

To match Pi.ai quality, we must test:
1. **Voice Quality**: Mean Opinion Score (MOS) >4.0
2. **Latency**: <200ms end-to-end (95th percentile)
3. **Emotion Accuracy**: >85% detection, appropriate responses
4. **Memory Accuracy**: >95% recall precision
5. **System Reliability**: >99% uptime, graceful failure

## Test Directory Structure

```
tests/
├── unit/                      # Component-level tests
│   ├── test_moshi_engine.py
│   ├── test_emotion_detector.py
│   ├── test_memory_system.py
│   ├── test_accent_engine.py
│   └── test_adapters.py
├── integration/               # System integration tests
│   ├── test_conversation_flow.py
│   ├── test_memory_integration.py
│   └── test_adapter_integration.py
├── performance/               # Performance benchmarks
│   ├── test_latency.py
│   ├── test_throughput.py
│   └── test_resource_usage.py
├── quality/                   # Voice quality tests
│   ├── test_voice_mos.py
│   ├── test_emotion_expression.py
│   └── test_accent_quality.py
└── e2e/                      # End-to-end scenarios
    ├── test_full_conversation.py
    ├── test_multi_session.py
    └── test_failure_recovery.py
```

## Unit Tests

### File: `tests/unit/test_emotion_detector.py`

```python
"""
Unit tests for emotion detection
Target: 85-90% accuracy (proven achievable)
"""

import pytest
import numpy as np
from digital_soul.emotion.detector import EmotionDetector, EmotionResult

@pytest.fixture
def detector():
    """Create emotion detector instance"""
    return EmotionDetector(device="cpu")  # CPU for testing

@pytest.fixture
def test_audio_samples():
    """Load pre-labeled test audio samples"""
    return {
        "happy": load_audio("tests/fixtures/emotions/happy_001.wav"),
        "sad": load_audio("tests/fixtures/emotions/sad_001.wav"),
        "frustrated": load_audio("tests/fixtures/emotions/frustrated_001.wav"),
        "angry": load_audio("tests/fixtures/emotions/angry_001.wav"),
        "neutral": load_audio("tests/fixtures/emotions/neutral_001.wav"),
    }

class TestEmotionDetection:
    """Test emotion detection accuracy"""

    async def test_detect_happy(self, detector, test_audio_samples):
        """Should detect happy emotion with high confidence"""
        audio = test_audio_samples["happy"]
        result = await detector.detect(audio)

        assert result.emotion == "happy"
        assert result.confidence >= 0.7  # Minimum acceptable
        assert result.intensity > 0.3  # Should have some intensity

    async def test_detect_frustrated(self, detector, test_audio_samples):
        """Should detect frustration (critical for tech support)"""
        audio = test_audio_samples["frustrated"]
        result = await detector.detect(audio)

        assert result.emotion == "frustrated"
        assert result.confidence >= 0.7

    async def test_accuracy_benchmark(self, detector):
        """
        Benchmark: >85% accuracy across all emotions
        Uses labeled test dataset (100 samples per emotion)
        """
        test_dataset = load_labeled_dataset("tests/fixtures/emotions/benchmark/")

        correct = 0
        total = 0

        for sample in test_dataset:
            result = await detector.detect(sample.audio)
            if result.emotion == sample.label:
                correct += 1
            total += 1

        accuracy = correct / total
        assert accuracy >= 0.85, f"Accuracy {accuracy:.2%} below 85% threshold"

    def test_prosody_extraction(self, detector):
        """Should extract valid prosody features"""
        # Generate test audio (1 second, 440Hz sine wave)
        audio = generate_sine_wave(freq=440, duration=1.0, sample_rate=16000)

        prosody = detector._extract_prosody(audio, 16000)

        # Check all required features present
        assert "pitch_mean" in prosody
        assert "pitch_std" in prosody
        assert "intensity_mean" in prosody
        assert "speaking_rate" in prosody

        # Check reasonable values
        assert 50 < prosody["pitch_mean"] < 500  # Human voice range
        assert prosody["pitch_std"] >= 0

    async def test_latency_requirement(self, detector, test_audio_samples):
        """Should detect emotion in <100ms"""
        import time

        audio = test_audio_samples["neutral"]

        start = time.perf_counter()
        result = await detector.detect(audio)
        latency = (time.perf_counter() - start) * 1000  # ms

        assert latency < 100, f"Latency {latency:.1f}ms exceeds 100ms target"


### File: `tests/unit/test_memory_system.py`

```python
"""
Unit tests for Mem0 memory system
Target: >95% recall accuracy, <50ms retrieval
"""

import pytest
from digital_soul.memory.mem0_client import SoulMemory, MemoryEntry

@pytest.fixture
async def memory():
    """Create memory system with test database"""
    mem = SoulMemory(
        user_id="test_user",
        storage_path="tests/fixtures/memory_test/"
    )
    await mem.initialize()
    yield mem
    # Cleanup
    await mem.close()

class TestMemoryStorage:
    """Test memory storage functionality"""

    async def test_store_and_recall(self, memory):
        """Should store and retrieve memories accurately"""
        # Store conversation
        conversation = {
            "user_input": "I prefer dark mode",
            "soul_response": "Noted, I'll remember that",
            "user_emotion": "neutral"
        }

        memory_ids = await memory.remember(conversation)
        assert len(memory_ids) > 0

        # Retrieve
        results = await memory.recall("user color preferences")
        assert len(results) > 0
        assert any("dark mode" in r.content.lower() for r in results)

    async def test_recall_accuracy(self, memory):
        """
        Benchmark: >95% recall accuracy
        Store 100 facts, retrieve with various queries
        """
        # Store test facts
        facts = load_test_facts("tests/fixtures/memory/test_facts.json")
        for fact in facts:
            await memory.remember(fact)

        # Test recall with queries
        test_queries = load_test_queries("tests/fixtures/memory/test_queries.json")

        correct = 0
        total = 0

        for query in test_queries:
            results = await memory.recall(query.text, limit=5)

            # Check if expected fact in top 5 results
            if any(query.expected_id == r.id for r in results):
                correct += 1
            total += 1

        accuracy = correct / total
        assert accuracy >= 0.95, f"Recall accuracy {accuracy:.2%} below 95%"

    async def test_retrieval_latency(self, memory):
        """Should retrieve memories in <50ms"""
        import time

        # Pre-populate with data
        for i in range(100):
            await memory.remember({
                "user_input": f"Test fact {i}",
                "soul_response": "Noted"
            })

        # Measure retrieval time
        start = time.perf_counter()
        results = await memory.recall("test fact")
        latency = (time.perf_counter() - start) * 1000  # ms

        assert latency < 50, f"Retrieval latency {latency:.1f}ms exceeds 50ms"
        assert len(results) > 0


## Performance Tests

### File: `tests/performance/test_latency.py`

```python
"""
End-to-end latency testing
Target: <200ms (95th percentile)
"""

import pytest
import time
import numpy as np
from digital_soul import SoulServer

@pytest.fixture
async def soul_server():
    """Start Soul server for testing"""
    from digital_soul.config import SoulConfig

    config = SoulConfig()
    config.moshi.device = "cpu"  # For consistent testing

    server = SoulServer(config)
    await server.start()
    yield server
    await server.stop()

class TestEndToEndLatency:
    """Test complete conversation latency"""

    async def test_single_turn_latency(self, soul_server):
        """Measure single conversation turn"""
        test_audio = load_test_audio("tests/fixtures/audio/test_input.wav")

        start = time.perf_counter()

        # Simulate conversation turn
        response = await soul_server.process_audio(test_audio)

        latency = (time.perf_counter() - start) * 1000  # ms

        assert latency < 300, f"Latency {latency:.1f}ms exceeds 300ms (relaxed for testing)"
        assert response is not None

    async def test_latency_distribution(self, soul_server):
        """
        Measure latency distribution over 100 turns
        Target: 95th percentile <200ms
        """
        test_audio = load_test_audio("tests/fixtures/audio/test_input.wav")
        latencies = []

        # Run 100 conversation turns
        for _ in range(100):
            start = time.perf_counter()
            await soul_server.process_audio(test_audio)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)

        # Calculate statistics
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)

        print(f"Latency distribution:")
        print(f"  P50: {p50:.1f}ms")
        print(f"  P95: {p95:.1f}ms")
        print(f"  P99: {p99:.1f}ms")

        # Target: P95 <200ms
        assert p95 < 200, f"P95 latency {p95:.1f}ms exceeds 200ms target"


## Voice Quality Tests

### File: `tests/quality/test_voice_mos.py`

```python
"""
Voice quality testing (Mean Opinion Score)
Target: MOS >4.0 (Pi.ai is ~4.3)
"""

import pytest
from digital_soul.voice.moshi_engine import MoshiEngine
from digital_soul.quality.mos_evaluator import MOSEvaluator

@pytest.fixture
def voice_engine():
    """Create voice engine"""
    return MoshiEngine(device="cpu")

@pytest.fixture
def mos_evaluator():
    """Create MOS evaluator (automated)"""
    return MOSEvaluator(model="nisqa")  # Automated MOS prediction

class TestVoiceQuality:
    """Test voice output quality"""

    async def test_basic_synthesis_quality(self, voice_engine, mos_evaluator):
        """Test basic synthesis meets quality threshold"""
        text = "Hello, I'm here to help with whatever you're working on."

        audio = await voice_engine.synthesize(text)
        mos_score = mos_evaluator.evaluate(audio)

        print(f"MOS Score: {mos_score:.2f}")
        assert mos_score >= 3.5, f"MOS {mos_score:.2f} below acceptable threshold"

    async def test_emotional_synthesis_quality(self, voice_engine, mos_evaluator):
        """Test emotional speech maintains quality"""
        emotions = ["happy", "sad", "frustrated", "calm"]

        for emotion in emotions:
            voice_engine.set_emotion(emotion, intensity=0.8)
            audio = await voice_engine.synthesize(
                "I understand how you're feeling about this."
            )

            mos_score = mos_evaluator.evaluate(audio)
            assert mos_score >= 3.5, f"{emotion}: MOS {mos_score:.2f} too low"

    async def test_mos_benchmark(self, voice_engine, mos_evaluator):
        """
        Benchmark: Average MOS >4.0 across test sentences
        Pi.ai achieves ~4.3, we target >4.0
        """
        test_sentences = load_test_sentences("tests/fixtures/sentences.txt")
        scores = []

        for sentence in test_sentences:
            audio = await voice_engine.synthesize(sentence)
            score = mos_evaluator.evaluate(audio)
            scores.append(score)

        average_mos = np.mean(scores)
        print(f"Average MOS: {average_mos:.2f} (target: >4.0)")

        assert average_mos >= 4.0, f"Average MOS {average_mos:.2f} below 4.0 target"


## Integration Tests

### File: `tests/integration/test_conversation_flow.py`

```python
"""
Test complete conversation flows
Simulates real user interactions
"""

import pytest
from digital_soul import SoulServer

@pytest.fixture
async def soul():
    """Start Soul for integration testing"""
    server = SoulServer()
    await server.start()
    yield server
    await server.stop()

class TestConversationFlow:
    """Test realistic conversation scenarios"""

    async def test_frustrated_user_flow(self, soul):
        """
        Scenario: User is frustrated with failing tests
        Expected: Soul responds with empathy and offers help
        """
        # User speaks with frustration
        user_input = load_audio("tests/scenarios/frustrated_tests.wav")

        response = await soul.process_audio(user_input)

        # Check emotion was detected
        assert soul.emotion_tracker.get_dominant_emotion()[0] == "frustrated"

        # Check response is appropriate
        assert response.emotion_modulation.tone == "calm"
        assert response.emotion_modulation.speed < 1.0  # Slower

    async def test_multi_turn_conversation(self, soul):
        """
        Scenario: Multi-turn conversation with context
        Expected: Soul remembers context across turns
        """
        # Turn 1: User mentions project
        turn1 = await soul.process_audio(
            load_audio("tests/scenarios/working_on_goose.wav")
        )

        # Turn 2: User asks about "the project" (requires context)
        turn2 = await soul.process_audio(
            load_audio("tests/scenarios/how_is_project.wav")
        )

        # Soul should remember "the project" = "goose"
        memories = await soul.memory.recall("current project")
        assert any("goose" in m.content.lower() for m in memories)

    async def test_adapter_execution_flow(self, soul):
        """
        Scenario: User requests code action
        Expected: Adapter executes successfully
        """
        # User: "Run tests on Super-Goose"
        user_input = load_audio("tests/scenarios/run_tests.wav")

        response = await soul.process_audio(user_input)

        # Check adapter was triggered
        assert soul.liaison.active_tasks

        # Wait for completion
        await asyncio.sleep(2)

        # Check task completed
        assert len(soul.liaison.active_tasks) == 0


## Deployment Validation Tests

### File: `tests/e2e/test_production_readiness.py`

```python
"""
Production readiness validation
Ensures system meets all requirements for deployment
"""

import pytest
from digital_soul import SoulServer
from digital_soul.config import SoulConfig

class TestProductionReadiness:
    """Validate production deployment requirements"""

    def test_configuration_validation(self):
        """Config should validate all required fields"""
        config = SoulConfig.from_yaml("config/production.yaml")

        assert config.user_id
        assert config.moshi.device in ["cuda", "cpu"]
        assert config.memory.storage_path
        assert config.privacy.recording == False  # Privacy default

    async def test_graceful_failure_handling(self):
        """System should handle failures gracefully"""
        server = SoulServer()

        # Simulate various failures
        failures = [
            "gpu_out_of_memory",
            "mic_not_available",
            "memory_corrupted",
        ]

        for failure in failures:
            try:
                await server._simulate_failure(failure)
            except Exception as e:
                # Should not crash, should log error
                assert server.is_running  # Still running
                assert failure in str(e).lower()

    async def test_resource_limits(self):
        """Should respect resource limits"""
        server = SoulServer()
        await server.start()

        # Monitor resource usage over 1 minute
        import psutil
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate heavy usage
        for _ in range(100):
            await server.process_audio(generate_test_audio())

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Should not leak memory significantly
        assert memory_growth < 500, f"Memory leak detected: {memory_growth:.1f}MB growth"

    def test_security_requirements(self):
        """Validate security requirements"""
        config = SoulConfig()

        # Privacy defaults
        assert config.privacy.recording == False
        assert config.privacy.telemetry == False

        # Memory encryption
        assert config.memory.enable_encryption == True

        # No network calls
        # (Would require network monitoring during test)


## Test Execution

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/unit/ -v
pytest tests/performance/ -v
pytest tests/quality/ -v

# Run with coverage
pytest tests/ --cov=digital_soul --cov-report=html

# Run performance benchmarks
pytest tests/performance/ -v --benchmark

# Run quality tests (requires GPU)
pytest tests/quality/ -v --gpu
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Generate coverage report
        run: pytest tests/ --cov=digital_soul --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Quality Gates

Before deployment, ALL these must pass:

- ✅ Unit tests: 100% passing
- ✅ Integration tests: 100% passing
- ✅ Emotion accuracy: >85%
- ✅ Memory recall: >95%
- ✅ Latency P95: <200ms
- ✅ Voice MOS: >4.0
- ✅ Code coverage: >90%
- ✅ No memory leaks
- ✅ Security audit passed
- ✅ Privacy requirements met

## Performance Benchmarking

```python
# scripts/benchmark.py
"""
Comprehensive performance benchmarking
Run before each release
"""

async def run_benchmarks():
    """Run all benchmarks and generate report"""

    results = {
        "latency": await benchmark_latency(),
        "voice_quality": await benchmark_voice_quality(),
        "memory_accuracy": await benchmark_memory(),
        "emotion_accuracy": await benchmark_emotion(),
        "resource_usage": await benchmark_resources(),
    }

    # Generate report
    print("=" * 60)
    print("DIGITAL SOUL - PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Latency P95: {results['latency']['p95']:.1f}ms (target: <200ms)")
    print(f"Voice MOS: {results['voice_quality']['mos']:.2f} (target: >4.0)")
    print(f"Memory Recall: {results['memory_accuracy']:.1%} (target: >95%)")
    print(f"Emotion Detection: {results['emotion_accuracy']:.1%} (target: >85%)")
    print(f"CPU Usage: {results['resource_usage']['cpu']:.1f}%")
    print(f"Memory: {results['resource_usage']['memory']:.1f}MB")
    print("=" * 60)

    # Check if all targets met
    all_passed = (
        results['latency']['p95'] < 200 and
        results['voice_quality']['mos'] > 4.0 and
        results['memory_accuracy'] > 0.95 and
        results['emotion_accuracy'] > 0.85
    )

    if all_passed:
        print("✅ ALL BENCHMARKS PASSED - Ready for deployment!")
    else:
        print("❌ Some benchmarks failed - See details above")

    return results

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
```

---

**Test Suite Ensures Pi.ai Quality Standards Are Met** 🎯
