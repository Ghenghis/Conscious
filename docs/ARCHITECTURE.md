# 🏗️ Digital Soul - Technical Architecture

## Mission: Match Pi.ai Quality, Locally

This document describes the technical architecture needed to build a voice companion that matches Pi.ai's natural conversation quality while running 100% locally.

## The Pi.ai Standard

After using Pi.ai for over a year, these are the key qualities we need to match:

1. **Natural Voice**: Not robotic, not "TTS-y", genuinely conversational
2. **Emotional Intelligence**: Understands and responds to your emotional state
3. **Low Latency**: Responds quickly, maintains conversation flow
4. **Memory**: Remembers previous conversations and your preferences
5. **Empathy**: Feels supportive, not transactional
6. **Interruption Handling**: Can be interrupted naturally

## Why Existing Solutions Fall Short

| Solution | Voice Quality | Privacy | Memory | Emotion | Why It's Not Enough |
|----------|---------------|---------|--------|---------|---------------------|
| ChatGPT Voice | Good | ✗ Cloud | ✗ | ✗ | No privacy, no persistent memory |
| GPT-4o Voice | Excellent | ✗ Cloud | Limited | Some | Cloud-only, expensive |
| Pi.ai | **Excellent** | ✗ Cloud | ✓ | ✓ | **Our target**, but cloud-only |
| Open source TTS | Poor | ✓ Local | ✗ | ✗ | Robotic voice, no intelligence |
| Coqui TTS | Okay | ✓ Local | ✗ | ✗ | Better voice, but still "TTS-y" |

**Digital Soul aims to match Pi.ai quality while being 100% local.**

## Core Architecture

### 1. Voice Engine: Kyutai Moshi

**Why Moshi?** It's the ONLY open-source model that does native speech-to-speech like GPT-4o.

#### Traditional (Bad) Pipeline:
```
Your Voice → STT (Whisper) → Text → LLM → Text → TTS (ElevenLabs) → Audio
          200ms              500ms        300ms              1000ms
          TOTAL: ~2 seconds of latency
```

#### Moshi (Good) Pipeline:
```
Your Voice → Moshi → Audio Response
          <200ms
```

**Key Advantages:**
- **Native Audio**: No text intermediate, preserves emotion
- **Full Duplex**: Listens while speaking, can be interrupted
- **Low Latency**: <200ms end-to-end
- **Emotion Preservation**: Voice tone carries through
- **Local**: Runs on consumer GPU (12GB+ VRAM)

#### Implementation Details

```python
from moshi import MoshiModel, AudioStream

class VoiceEngine:
    def __init__(self):
        # Load Moshi 7B model
        self.model = MoshiModel.from_pretrained(
            "kyutai/moshi-7b",
            device="cuda",
            torch_dtype=torch.float16  # Half precision for speed
        )

        # Setup audio stream (full duplex)
        self.stream = AudioStream(
            sample_rate=24000,
            chunk_size=1024,
            input_device="default",
            output_device="default",
            duplex=True  # Listen and speak simultaneously
        )

    async def converse(self):
        """Main conversation loop"""
        async for audio_chunk in self.stream.input:
            # Process audio directly
            response_audio = await self.model.process(
                audio_chunk,
                context=self.conversation_context,
                emotion_target=self.target_emotion
            )

            # Stream response immediately
            await self.stream.output.play(response_audio)

            # Extract semantic content for other systems
            intent = self.model.extract_semantic(audio_chunk)
            yield intent
```

**Hardware Requirements:**
- **Minimum**: RTX 3060 (12GB VRAM) or M1 Pro
- **Recommended**: RTX 4060 Ti (16GB VRAM) or M2 Max
- **Optimal**: RTX 4090 (24GB VRAM) or M3 Ultra

**Fallback**: CPU mode works but slower (~500ms latency)

### 2. Memory System: Mem0

**Why Mem0?** It's specifically designed for persistent personal memory, like Pi.ai has.

#### Memory Types

```
Personal Memory (Mem0)
├── Preferences
│   ├── "User prefers dark mode"
│   ├── "User likes clean code"
│   └── "User dislikes verbose explanations"
├── Context
│   ├── "Currently working on: Super-Goose"
│   ├── "Main project location: ~/goose"
│   └── "Recent focus: Code coverage"
├── Emotional State
│   ├── "User was frustrated with tests yesterday"
│   ├── "User celebrates wins enthusiastically"
│   └── "User prefers calm tone when stressed"
├── Patterns
│   ├── "Usually works 9am-2pm"
│   ├── "Takes breaks every 90 minutes"
│   └── "Prefers voice for quick questions"
└── Relationships
    ├── "Working with team on Super-Goose"
    ├── "Interested in Rust and AI"
    └── "Values privacy highly"
```

#### Implementation

```python
from mem0 import Mem0Client
from qdrant_client import QdrantClient

class MemorySystem:
    def __init__(self, user_id: str):
        # Local vector database
        self.qdrant = QdrantClient(path="~/.soul/memory/qdrant")

        # Mem0 for memory management
        self.mem0 = Mem0Client(
            vector_store=self.qdrant,
            embedding_model="all-MiniLM-L6-v2",  # Fast, local
            user_id=user_id
        )

    async def remember(self, conversation: dict):
        """Extract and store memories"""
        # Extract entities and facts
        memories = await self._extract_memories(conversation)

        # Store in Mem0
        for memory in memories:
            await self.mem0.add_memory(
                content=memory.content,
                category=memory.category,
                metadata={
                    "timestamp": now(),
                    "confidence": memory.confidence,
                    "emotion": memory.emotion
                }
            )

    async def recall(self, query: str, limit: int = 5):
        """Retrieve relevant memories"""
        results = await self.mem0.search(
            query=query,
            limit=limit,
            filters={"confidence": {"$gte": 0.7}}
        )
        return results

    async def _extract_memories(self, conversation: dict):
        """Extract memorable information"""
        # Use LLM to identify what's worth remembering
        prompt = f"""
        Extract memorable facts from this conversation:
        User: {conversation['user_input']}
        Assistant: {conversation['assistant_response']}

        Extract:
        1. Preferences (user likes/dislikes)
        2. Context (current work, projects)
        3. Emotions (user felt X about Y)
        4. Patterns (user typically does X)

        Format as JSON list.
        """

        memories = await self.llm.extract(prompt)
        return memories
```

**Privacy Features:**
- **Local Storage**: All data in `~/.soul/memory/`
- **Encryption**: AES-256 for sensitive memories
- **User Control**: Easy memory inspection/deletion via UI
- **No Sync**: Never leaves your machine

### 3. Emotion Engine

**Goal**: Match Pi.ai's empathetic responses.

#### Emotion Detection (User → Soul)

```python
from transformers import Wav2Vec2ForSequenceClassification
import librosa

class EmotionDetector:
    def __init__(self):
        # Load emotion classifier
        self.model = Wav2Vec2ForSequenceClassification.from_pretrained(
            "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
        )

    async def detect(self, audio: bytes) -> Emotion:
        """Detect emotion from voice"""
        # Extract features
        features = librosa.feature.mfcc(
            y=audio,
            sr=16000,
            n_mfcc=40
        )

        # Classify
        emotion_scores = self.model(features)
        top_emotion = max(emotion_scores, key=emotion_scores.get)

        return Emotion(
            name=top_emotion,  # happy, sad, frustrated, excited, etc.
            confidence=emotion_scores[top_emotion],
            intensity=self._calculate_intensity(features)
        )
```

#### Emotion Response (Soul → User)

```python
class EmotionModulator:
    """Adjust Soul's response based on user emotion"""

    EMOTION_RESPONSES = {
        "frustrated": {
            "tone": "calm and supportive",
            "speed": 0.85,  # Slower, more deliberate
            "pitch": 0.95,  # Slightly lower
            "add_pause": True,
            "examples": [
                "I hear you, that's frustrating.",
                "Let's figure this out together.",
                "Take a breath, we'll solve this."
            ]
        },
        "excited": {
            "tone": "enthusiastic",
            "speed": 1.15,  # Match energy
            "pitch": 1.05,  # Slightly higher
            "add_laughter": True,
            "examples": [
                "Yes! That's awesome!",
                "I'm excited too!",
                "This is great progress!"
            ]
        },
        "confused": {
            "tone": "patient and clear",
            "speed": 0.9,  # Slower for clarity
            "pitch": 1.0,
            "add_pause": True,
            "examples": [
                "Let me explain that differently.",
                "No worries, this can be tricky.",
                "Let's break it down step by step."
            ]
        },
        "tired": {
            "tone": "gentle and energizing",
            "speed": 0.95,
            "pitch": 1.0,
            "examples": [
                "You sound tired. Want to take a break?",
                "Let's keep this simple for now.",
                "We can tackle the rest later."
            ]
        }
    }

    def modulate(self, response: str, user_emotion: Emotion) -> AudioParams:
        """Adjust response parameters"""
        config = self.EMOTION_RESPONSES.get(user_emotion.name, {})

        return AudioParams(
            tone=config.get("tone", "neutral"),
            speed=config.get("speed", 1.0),
            pitch=config.get("pitch", 1.0),
            add_pause=config.get("add_pause", False),
            add_laughter=config.get("add_laughter", False)
        )
```

### 4. Universal Adapter System

**Goal**: Make Digital Soul useful for ANY project, not just coding.

#### Adapter Interface

```python
from abc import ABC, abstractmethod

class Adapter(ABC):
    """Base adapter interface"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """What this adapter can do"""
        pass

    @abstractmethod
    async def execute(self, intent: str, context: dict) -> ActionResult:
        """Execute action based on intent"""
        pass

    @abstractmethod
    async def get_status(self) -> dict:
        """Get current status/state"""
        pass
```

#### Example: Coding Adapter (Super-Goose)

```python
class CodingAdapter(Adapter):
    """Adapter for coding tasks via Super-Goose"""

    name = "coding"
    capabilities = [
        "run_tests",
        "fix_errors",
        "build_project",
        "deploy",
        "analyze_code",
        "generate_docs"
    ]

    async def execute(self, intent: str, context: dict):
        """Execute coding task"""
        # Parse intent
        if "test" in intent.lower():
            return await self._run_tests()
        elif "fix" in intent.lower():
            return await self._fix_errors(context)
        # ... more actions

    async def _run_tests(self):
        """Run project tests"""
        result = subprocess.run(
            ["super-goose", "test", "--all"],
            capture_output=True
        )

        return ActionResult(
            success=result.returncode == 0,
            message="Tests completed" if result.returncode == 0 else "Tests failed",
            details={"output": result.stdout}
        )
```

#### Example: Writing Adapter

```python
class WritingAdapter(Adapter):
    """Adapter for writing tasks"""

    name = "writing"
    capabilities = [
        "draft_assistance",
        "grammar_check",
        "pacing_analysis",
        "character_consistency",
        "research_integration"
    ]

    async def execute(self, intent: str, context: dict):
        """Execute writing task"""
        if "draft" in intent.lower():
            return await self._assist_draft(context)
        elif "check" in intent.lower():
            return await self._check_grammar(context)
        # ... more actions

    async def _assist_draft(self, context: dict):
        """Help with drafting"""
        current_text = context.get("current_text", "")
        user_stuck_on = context.get("stuck_on", "")

        # Use LLM to suggest next steps
        suggestion = await self.llm.suggest_next(
            text=current_text,
            problem=user_stuck_on,
            style=context.get("writing_style", "neutral")
        )

        return ActionResult(
            success=True,
            message=f"Here's a suggestion: {suggestion}",
            details={"suggestion": suggestion}
        )
```

## Performance Optimization

### Latency Budget (Target: <200ms)

```
User stops speaking                    0ms
↓
Audio chunk ready                    +50ms
↓
Moshi processes                      +100ms
↓
Memory retrieval (parallel)          +30ms
↓
Response generated                   +0ms (part of Moshi)
↓
Audio starts playing                 +20ms
────────────────────────────────────────
TOTAL                                200ms
```

### Optimization Strategies

1. **Model Quantization**
   ```python
   # Use 4-bit quantization for Moshi
   model = MoshiModel.from_pretrained(
       "kyutai/moshi-7b",
       load_in_4bit=True,  # 12GB → 3GB VRAM
       bnb_4bit_compute_dtype=torch.float16
   )
   ```

2. **Streaming Audio**
   ```python
   # Don't wait for full response
   async for audio_chunk in model.stream_response():
       await output.play(audio_chunk)  # Play immediately
   ```

3. **Memory Caching**
   ```python
   # Cache frequent memories
   @lru_cache(maxsize=100)
   async def get_preferences(category: str):
       return await mem0.search(f"preference:{category}")
   ```

4. **GPU Optimization**
   ```python
   # Use Flash Attention 2
   model = MoshiModel.from_pretrained(
       "kyutai/moshi-7b",
       attn_implementation="flash_attention_2"
   )
   ```

## Data Flow: Complete Example

```
1. USER SPEAKS
   "Soul, the tests are failing again, this is frustrating."
   │
   ├─ Audio Stream → Moshi
   └─ Duration: 50ms

2. MOSHI PROCESSES (Parallel)
   ├─ Extract Intent: "investigate test failures"
   ├─ Detect Emotion: "frustrated" (confidence: 0.85)
   └─ Generate Response Seeds
   └─ Duration: 100ms

3. MEMORY RETRIEVAL (Parallel)
   ├─ Query: "test failures, frustration, recent context"
   ├─ Results:
   │   - "Tests failed yesterday too" (relevance: 0.92)
   │   - "User prefers calm explanations when stressed" (0.88)
   │   - "Current project: Super-Goose" (0.95)
   └─ Duration: 30ms

4. ADAPTER EXECUTION (Triggered)
   ├─ Coding Adapter: Check test logs
   ├─ Found: "Timeout in auth module"
   └─ Duration: 50ms (async, doesn't block voice)

5. RESPONSE GENERATION
   ├─ Emotion Modulation:
   │   - Tone: "calm and supportive"
   │   - Speed: 0.85 (slower)
   │   - Add pause: true
   ├─ Content: "I hear you, that's frustrating. Let me check...
   │            okay, it's that timeout in the auth module we saw
   │            yesterday. Want me to have the team fix it?"
   └─ Duration: 0ms (part of Moshi streaming)

6. AUDIO OUTPUT
   ├─ Moshi generates audio with emotion modulation
   ├─ Stream starts playing
   └─ Duration: 20ms to first audio

7. MEMORY STORAGE (Async, Non-blocking)
   ├─ Store: "User frustrated with test failures"
   ├─ Store: "Recurring issue: auth module timeout"
   └─ Update: "Frustration pattern" counter

TOTAL LATENCY: ~200ms (target met!)
```

## Deployment Architecture

```
~/.soul/
├── config.yaml              # Main configuration
├── models/
│   ├── moshi-7b/           # Voice model (7GB)
│   └── emotion/            # Emotion classifier
├── memory/
│   ├── qdrant/             # Vector database
│   ├── memories.db         # Structured storage
│   └── embeddings.cache    # Embedding cache
├── adapters/
│   ├── coding/
│   │   └── super-goose.yaml
│   ├── writing/
│   │   └── obsidian.yaml
│   └── research/
│       └── zotero.yaml
├── logs/
│   ├── conversations/      # Conversation history
│   ├── system.log         # System logs
│   └── performance.log    # Latency metrics
└── backups/               # Daily memory backups
```

## Security & Privacy

### Threat Model

**What we protect against:**
1. Data exfiltration (no cloud, no network calls)
2. Unauthorized memory access (encryption)
3. Voice recording without consent (disabled by default)
4. Memory tampering (signed storage)

**What we DON'T protect against:**
1. Physical access to machine (you own it)
2. Malicious adapters (user installs)
3. OS-level attacks (outside scope)

### Implementation

```python
# Memory encryption
from cryptography.fernet import Fernet

class SecureMemory:
    def __init__(self, key_path="~/.soul/memory.key"):
        # Generate or load encryption key
        if not os.path.exists(key_path):
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
            os.chmod(key_path, 0o600)  # Owner read/write only

        with open(key_path, "rb") as f:
            self.fernet = Fernet(f.read())

    def store(self, memory: dict):
        # Encrypt before storage
        encrypted = self.fernet.encrypt(json.dumps(memory).encode())
        self.db.insert(encrypted)

    def retrieve(self, query: str):
        # Decrypt after retrieval
        encrypted = self.db.search(query)
        decrypted = self.fernet.decrypt(encrypted)
        return json.loads(decrypted)
```

## Testing Strategy

### Voice Quality Testing
```python
# Mean Opinion Score (MOS) testing
def test_voice_quality():
    """Target: MOS > 4.0 (Pi.ai is ~4.3)"""
    recordings = generate_test_responses()
    scores = []

    for recording in recordings:
        # Automated MOS using trained model
        score = voice_quality_model.rate(recording)
        scores.append(score)

    assert np.mean(scores) > 4.0
```

### Latency Testing
```python
def test_response_latency():
    """Target: <200ms end-to-end"""
    start = time.perf_counter()

    # Simulate user input
    response = await soul.process_audio(test_audio)

    latency = (time.perf_counter() - start) * 1000  # ms
    assert latency < 200, f"Latency: {latency}ms"
```

### Memory Testing
```python
def test_memory_recall():
    """Target: >95% recall accuracy"""
    # Store test memories
    await memory.remember({"fact": "User loves dark mode"})

    # Query later
    results = await memory.recall("user color preferences")

    assert "dark mode" in results[0].content
    assert results[0].confidence > 0.9
```

## Success Metrics

| Metric | Target | How We Measure |
|--------|--------|----------------|
| Voice Quality (MOS) | >4.0 | Automated + user surveys |
| Response Latency | <200ms | Performance logs |
| Memory Accuracy | >95% | Test recall precision |
| Emotion Detection | >85% | Labeled test set |
| User Satisfaction | >4.5/5 | Weekly surveys |
| Privacy Score | 100% | Network traffic = 0 |

## Next Steps

### Phase 1: Voice Foundation (Weeks 1-4)
1. Setup Moshi integration
2. Implement audio streaming
3. Basic conversation loop
4. Latency optimization

### Phase 2: Memory System (Weeks 5-6)
1. Mem0 integration
2. Memory extraction
3. Recall system
4. Privacy controls

### Phase 3: Emotion (Weeks 7-8)
1. Emotion detection
2. Response modulation
3. Empathy tuning
4. User testing

### Phase 4: Adapters (Weeks 9-12)
1. Adapter framework
2. Super-Goose adapter
3. Writing adapter
4. Custom adapter docs

### Phase 5: Polish (Weeks 13-16)
1. Voice quality tuning to match Pi.ai
2. Performance optimization
3. User feedback integration
4. Production release

---

**Digital Soul: Pi.ai quality, your privacy, universal capability.**
