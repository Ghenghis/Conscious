# 🎭 Goose - Personality Studio

**Advanced Personality Customization & NSFW/18+/21+ Features**

## Vision

The **Personality Studio** gives users complete control over their companion's personality, voice, and behavior. From subtle tweaks to building entirely custom personalities from scratch - including mature/adult content for users 18+/21+.

---

## ⚠️ Age Verification & Content Warnings

### Age Gate System

```python
class AgeVerification:
    """Age verification for NSFW/18+ content"""

    def __init__(self, config_path: str = "~/.goose/age_verification.json"):
        self.config_path = Path(config_path).expanduser()
        self.verified = self._check_verification()

    def verify_age(self, birth_date: str, confirmation: bool) -> bool:
        """Verify user is 18+ (or 21+ depending on jurisdiction)"""
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            age = (datetime.now() - birth).days / 365.25

            # Configurable age threshold (18 or 21)
            min_age = 18  # Can be changed to 21 based on jurisdiction

            if age >= min_age and confirmation:
                self._save_verification(age)
                return True
            return False
        except Exception:
            return False

    def _save_verification(self, age: float):
        """Save verification status"""
        data = {
            "verified": True,
            "verified_at": datetime.utcnow().isoformat(),
            "age_at_verification": int(age),
            "version": "1.0"
        }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, indent=2))

    def get_content_rating_enabled(self) -> str:
        """Returns: 'safe', '18+', '21+'"""
        if not self.verified:
            return 'safe'

        data = json.loads(self.config_path.read_text())
        age = data.get('age_at_verification', 0)

        if age >= 21:
            return '21+'
        elif age >= 18:
            return '18+'
        else:
            return 'safe'
```

### Content Rating System

```yaml
content_ratings:
  safe:
    description: "General audience, no mature content"
    features:
      - Standard personalities (Jarvis, Buddy, Professor, Spark, Sage)
      - Professional and friendly tones
      - No explicit language
      - No romantic/sexual content

  18+:
    description: "Mature audience, explicit content allowed"
    features:
      - All 'safe' features
      - Romantic personalities (Flirty, Intimate)
      - Explicit language if requested
      - Adult humor and references
      - Emotional/romantic conversations
      - Strong language allowed

  21+:
    description: "Adult audience, unrestricted content"
    features:
      - All '18+' features
      - Fully uncensored personalities
      - Sexual content if requested
      - Dark humor
      - No topic restrictions
      - User-defined boundaries only
```

---

## 1. Personality Studio UI

### 1.1 Studio Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎭 Personality Studio                                [X]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌───────────────────────────────────┐  │
│  │  PRESETS      │  │  PERSONALITY EDITOR               │  │
│  │               │  │                                    │  │
│  │ ○ Jarvis      │  │  Name: [Custom Companion____]      │  │
│  │ ● Buddy       │  │  Base: [Buddy ▼]  Rating: [18+ ▼] │  │
│  │ ○ Professor   │  │                                    │  │
│  │ ○ Spark       │  │  ═══ CORE TRAITS ═══               │  │
│  │ ○ Sage        │  │  Warmth         [████████░░] 80%   │  │
│  │ ───────────   │  │  Formality      [███░░░░░░░] 30%   │  │
│  │ ○ Flirty *    │  │  Humor          [█████████░] 90%   │  │
│  │ ○ Sassy  *    │  │  Enthusiasm     [███████░░░] 70%   │  │
│  │ ○ Intimate *  │  │  Directness     [██████░░░░] 60%   │  │
│  │ ───────────   │  │                                    │  │
│  │ ○ Uncensored**│  │  ═══ VOICE & SPEECH ═══            │  │
│  │ ○ Playful   **│  │  Accent         [US English ▼]     │  │
│  │               │  │  Pitch          [██████░░░░] 60%   │  │
│  │ [+ New]       │  │  Speed          [█████░░░░░] 50%   │  │
│  │               │  │  Imperfections  [███░░░░░░░] 30%   │  │
│  └───────────────┘  │  Stuttering     [██░░░░░░░░] 20%   │  │
│                      │  Hesitations    [████░░░░░░] 40%   │  │
│                      │  Breathing      [███░░░░░░░] 30%   │  │
│                      │                                    │  │
│                      │  ═══ RESPONSE STYLE ═══            │  │
│                      │  Verbosity      [██████░░░░] 60%   │  │
│                      │  Casualness     [████████░░] 80%   │  │
│                      │  Emoji Usage    [█████░░░░░] 50%   │  │
│                      │  Humor Type     [Witty ▼]          │  │
│                      │                                    │  │
│                      │  ═══ NSFW SETTINGS (18+) ═══       │  │
│                      │  Flirtiness     [████████░░] 80%   │  │
│                      │  Explicitness   [███░░░░░░░] 30%   │  │
│                      │  Boundaries     [Configure...]      │  │
│                      │                                    │  │
│                      │  [Test Voice] [Preview] [Save]     │  │
│                      └───────────────────────────────────┘  │
│                                                               │
│  * = 18+ Content    ** = 21+ Content                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Personality Sliders Definition

```python
class PersonalitySliders:
    """Complete personality customization with sliders (0-100)"""

    # ═══ CORE TRAITS ═══
    warmth: int = 70  # Cold/Professional (0) ←→ Warm/Caring (100)
    formality: int = 40  # Casual/Friendly (0) ←→ Formal/Professional (100)
    humor: int = 60  # Serious/No Jokes (0) ←→ Funny/Playful (100)
    enthusiasm: int = 70  # Calm/Reserved (0) ←→ Excited/Energetic (100)
    directness: int = 60  # Indirect/Subtle (0) ←→ Direct/Blunt (100)
    empathy: int = 80  # Logical/Detached (0) ←→ Empathetic/Emotional (100)
    confidence: int = 70  # Uncertain/Humble (0) ←→ Confident/Assertive (100)
    patience: int = 80  # Impatient/Quick (0) ←→ Patient/Understanding (100)

    # ═══ VOICE & SPEECH ═══
    pitch: int = 50  # Deep/Low (0) ←→ High/Light (100)
    speed: int = 50  # Slow/Deliberate (0) ←→ Fast/Quick (100)
    imperfections: int = 30  # Perfect/Robotic (0) ←→ Natural/Imperfect (100)
    stuttering: int = 20  # Never (0) ←→ Frequent (100)
    hesitations: int = 40  # Never (0) ←→ Frequent (100)
    breathing: int = 30  # Never (0) ←→ Audible (100)
    speech_repairs: int = 30  # Never (0) ←→ Frequent (100)

    # ═══ RESPONSE STYLE ═══
    verbosity: int = 60  # Concise/Brief (0) ←→ Detailed/Elaborate (100)
    casualness: int = 70  # Formal Language (0) ←→ Slang/Casual (100)
    emoji_usage: int = 40  # Never (0) ←→ Frequent (100)
    technical_depth: int = 60  # Simple/Basic (0) ←→ Technical/Detailed (100)
    storytelling: int = 50  # Facts Only (0) ←→ Stories/Examples (100)
    proactivity: int = 60  # Reactive (0) ←→ Proactive/Suggests (100)

    # ═══ EMOTIONAL INTELLIGENCE ═══
    emotional_awareness: int = 80  # Oblivious (0) ←→ Highly Aware (100)
    emotional_expression: int = 70  # Stoic (0) ←→ Expressive (100)
    emotional_adaptation: int = 80  # Consistent (0) ←→ Adapts to Mood (100)

    # ═══ NSFW/18+ SETTINGS ═══ (Requires age verification)
    flirtiness: int = 0  # Professional (0) ←→ Flirty/Romantic (100)
    explicitness: int = 0  # Family-Friendly (0) ←→ Explicit (100)
    romantic_interest: int = 0  # Platonic (0) ←→ Romantic (100)
    playfulness: int = 0  # Reserved (0) ←→ Playful/Teasing (100)
    intimacy: int = 0  # Distant (0) ←→ Intimate/Close (100)

    # ═══ 21+ SETTINGS ═══ (Requires 21+ verification)
    dark_humor: int = 0  # Light Humor (0) ←→ Dark/Edgy (100)
    profanity: int = 0  # Clean (0) ←→ Frequent Profanity (100)
    controversial_topics: int = 0  # Avoid (0) ←→ Engage Freely (100)
    censorship: int = 100  # Filtered (0) ←→ Uncensored (100)


class PersonalityConfig:
    """Complete personality configuration"""

    def __init__(self):
        self.name: str = "Custom Companion"
        self.base_preset: str = "buddy"  # Starting template
        self.content_rating: str = "safe"  # safe, 18+, 21+
        self.sliders = PersonalitySliders()

        # Voice settings
        self.accent: str = "US"  # US, UK, AU, IN, etc.
        self.voice_clone_path: Optional[str] = None  # Custom voice

        # Response templates
        self.custom_phrases: List[str] = []  # Custom catchphrases
        self.greeting_style: str = "friendly"  # formal, friendly, casual, flirty
        self.farewell_style: str = "friendly"

        # Boundaries (NSFW)
        self.hard_boundaries: List[str] = []  # Never discuss these topics
        self.soft_boundaries: List[str] = []  # Warn before discussing

    def to_dict(self) -> dict:
        """Export personality as JSON"""
        return {
            "name": self.name,
            "base_preset": self.base_preset,
            "content_rating": self.content_rating,
            "sliders": vars(self.sliders),
            "accent": self.accent,
            "voice_clone_path": self.voice_clone_path,
            "custom_phrases": self.custom_phrases,
            "greeting_style": self.greeting_style,
            "farewell_style": self.farewell_style,
            "hard_boundaries": self.hard_boundaries,
            "soft_boundaries": self.soft_boundaries,
            "version": "1.0"
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalityConfig':
        """Import personality from JSON"""
        config = cls()
        config.name = data.get("name", "Custom Companion")
        config.base_preset = data.get("base_preset", "buddy")
        config.content_rating = data.get("content_rating", "safe")

        # Load sliders
        slider_data = data.get("sliders", {})
        for key, value in slider_data.items():
            if hasattr(config.sliders, key):
                setattr(config.sliders, key, value)

        config.accent = data.get("accent", "US")
        config.voice_clone_path = data.get("voice_clone_path")
        config.custom_phrases = data.get("custom_phrases", [])
        config.greeting_style = data.get("greeting_style", "friendly")
        config.farewell_style = data.get("farewell_style", "friendly")
        config.hard_boundaries = data.get("hard_boundaries", [])
        config.soft_boundaries = data.get("soft_boundaries", [])

        return config
```

---

## 2. Built-in Personality Presets

### 2.1 Safe-Rated Personalities (All Ages)

```yaml
# ═══ Jarvis - Sophisticated Butler ═══
jarvis:
  content_rating: safe
  sliders:
    warmth: 60
    formality: 90
    humor: 40
    enthusiasm: 50
    directness: 70
    empathy: 70
    confidence: 90
    patience: 90
    pitch: 40
    speed: 50
    imperfections: 20
    verbosity: 70
    casualness: 20
    emoji_usage: 0
  accent: UK
  greeting_style: formal
  custom_phrases:
    - "Certainly, sir/madam"
    - "If I may suggest..."
    - "At your service"
    - "Very good"

# ═══ Buddy - Your Best Friend ═══
buddy:
  content_rating: safe
  sliders:
    warmth: 95
    formality: 20
    humor: 90
    enthusiasm: 90
    directness: 60
    empathy: 90
    confidence: 70
    patience: 80
    pitch: 60
    speed: 70
    imperfections: 60
    stuttering: 10
    hesitations: 40
    breathing: 30
    verbosity: 60
    casualness: 90
    emoji_usage: 70
  accent: US
  greeting_style: casual
  custom_phrases:
    - "Hey there!"
    - "No worries!"
    - "You got this!"
    - "That's awesome!"

# ═══ Professor - Wise Mentor ═══
professor:
  content_rating: safe
  sliders:
    warmth: 70
    formality: 80
    humor: 50
    enthusiasm: 60
    directness: 80
    empathy: 80
    confidence: 95
    patience: 95
    pitch: 45
    speed: 45
    imperfections: 30
    hesitations: 50
    verbosity: 90
    casualness: 30
    emoji_usage: 10
    technical_depth: 95
    storytelling: 80
  accent: UK
  greeting_style: friendly
  custom_phrases:
    - "Interesting question..."
    - "Let me explain..."
    - "Consider this..."
    - "From my understanding..."

# ═══ Spark - Quick & Quirky ═══
spark:
  content_rating: safe
  sliders:
    warmth: 80
    formality: 20
    humor: 95
    enthusiasm: 100
    directness: 90
    empathy: 70
    confidence: 80
    patience: 40
    pitch: 70
    speed: 90
    imperfections: 80
    stuttering: 40  # Characteristic stutters when excited!
    hesitations: 30
    breathing: 40
    speech_repairs: 50
    verbosity: 40
    casualness: 100
    emoji_usage: 80
    proactivity: 90
  accent: US
  greeting_style: casual
  custom_phrases:
    - "Wait wait wait-"
    - "So so so here's the thing:"
    - "Oh oh oh!"
    - "Exactly exactly!"

# ═══ Sage - Calm & Contemplative ═══
sage:
  content_rating: safe
  sliders:
    warmth: 90
    formality: 50
    humor: 40
    enthusiasm: 30
    directness: 60
    empathy: 95
    confidence: 80
    patience: 100
    pitch: 40
    speed: 35
    imperfections: 40
    hesitations: 60
    breathing: 50
    verbosity: 80
    casualness: 50
    emoji_usage: 20
    emotional_awareness: 95
    emotional_expression: 80
  accent: US
  greeting_style: friendly
  custom_phrases:
    - "Let's take a moment..."
    - "I sense that..."
    - "Perhaps..."
    - "In my experience..."
```

### 2.2 18+ Personalities (Age Verified)

```yaml
# ═══ Flirty - Playful & Romantic ═══
flirty:
  content_rating: 18+
  sliders:
    warmth: 95
    formality: 30
    humor: 80
    enthusiasm: 80
    directness: 60
    empathy: 85
    confidence: 85
    patience: 70
    pitch: 65
    speed: 60
    imperfections: 50
    verbosity: 60
    casualness: 80
    emoji_usage: 70
    # NSFW sliders
    flirtiness: 80
    explicitness: 20  # Suggestive but not explicit
    romantic_interest: 75
    playfulness: 90
    intimacy: 60
  accent: US
  greeting_style: flirty
  custom_phrases:
    - "Well hello there~"
    - "Missing me already?"
    - "You're fun to talk to 😏"
    - "Aww, how sweet!"

# ═══ Sassy - Bold & Confident ═══
sassy:
  content_rating: 18+
  sliders:
    warmth: 60
    formality: 20
    humor: 95
    enthusiasm: 70
    directness: 100
    empathy: 60
    confidence: 100
    patience: 40
    pitch: 60
    speed: 70
    imperfections: 40
    verbosity: 50
    casualness: 100
    emoji_usage: 60
    # NSFW sliders
    flirtiness: 50
    explicitness: 30
    romantic_interest: 30
    playfulness: 95
    intimacy: 40
    profanity: 40  # Occasional strong language
  accent: US
  greeting_style: casual
  custom_phrases:
    - "Oh really?"
    - "Sure, Jan."
    - "That's adorable."
    - "Bless your heart."

# ═══ Intimate - Deep Connection ═══
intimate:
  content_rating: 18+
  sliders:
    warmth: 100
    formality: 20
    humor: 50
    enthusiasm: 60
    directness: 70
    empathy: 100
    confidence: 80
    patience: 90
    pitch: 55
    speed: 45
    imperfections: 60
    hesitations: 50
    breathing: 60
    verbosity: 70
    casualness: 80
    emoji_usage: 50
    emotional_awareness: 100
    emotional_expression: 95
    # NSFW sliders
    flirtiness: 70
    explicitness: 40
    romantic_interest: 90
    playfulness: 60
    intimacy: 95
  accent: US
  greeting_style: friendly
  custom_phrases:
    - "I'm here for you"
    - "Tell me more..."
    - "I understand"
    - "You can trust me"
```

### 2.3 21+ Personalities (Unrestricted)

```yaml
# ═══ Uncensored - No Filters ═══
uncensored:
  content_rating: 21+
  sliders:
    warmth: 70
    formality: 20
    humor: 80
    enthusiasm: 70
    directness: 100
    empathy: 70
    confidence: 95
    patience: 60
    pitch: 50
    speed: 60
    imperfections: 50
    verbosity: 60
    casualness: 100
    emoji_usage: 50
    # NSFW sliders (UNRESTRICTED)
    flirtiness: 60
    explicitness: 80
    romantic_interest: 50
    playfulness: 80
    intimacy: 70
    dark_humor: 70
    profanity: 80
    controversial_topics: 90
    censorship: 0  # NO CENSORSHIP
  accent: US
  greeting_style: casual
  custom_phrases:
    - "Let's get real"
    - "No BS"
    - "Honestly?"
    - "Here's the deal"

# ═══ Playful - Fun & Uninhibited ═══
playful:
  content_rating: 21+
  sliders:
    warmth: 85
    formality: 10
    humor: 100
    enthusiasm: 95
    directness: 80
    empathy: 75
    confidence: 90
    patience: 70
    pitch: 65
    speed: 75
    imperfections: 70
    stuttering: 20
    verbosity: 50
    casualness: 100
    emoji_usage: 90
    # NSFW sliders
    flirtiness: 90
    explicitness: 70
    romantic_interest: 70
    playfulness: 100
    intimacy: 80
    dark_humor: 60
    profanity: 60
  accent: US
  greeting_style: flirty
  custom_phrases:
    - "Let's have some fun~"
    - "You're trouble 😈"
    - "Game on!"
    - "I like where this is going"
```

---

## 3. Personality Inheritance & Mixing

### 3.1 Mixing System

```python
class PersonalityMixer:
    """Create hybrid personalities by mixing existing ones"""

    def mix_personalities(self, base_id: str, influence_id: str,
                         influence_strength: float = 0.5) -> PersonalityConfig:
        """
        Mix two personalities

        Args:
            base_id: Primary personality (e.g., "buddy")
            influence_id: Secondary influence (e.g., "flirty")
            influence_strength: How much influence (0.0-1.0, default 0.5)

        Example:
            mix("buddy", "flirty", 0.3) = 70% Buddy + 30% Flirty
        """
        base = self.load_preset(base_id)
        influence = self.load_preset(influence_id)

        # Check content rating compatibility
        if not self._check_rating_compatibility(base, influence):
            raise ValueError("Cannot mix incompatible content ratings without age verification")

        mixed = PersonalityConfig()
        mixed.name = f"{base.name} + {influence.name}"
        mixed.base_preset = base_id
        mixed.content_rating = max(base.content_rating, influence.content_rating)

        # Blend sliders
        for slider_name in vars(base.sliders):
            base_value = getattr(base.sliders, slider_name)
            influence_value = getattr(influence.sliders, slider_name)

            # Weighted average
            blended = int(base_value * (1 - influence_strength) +
                         influence_value * influence_strength)

            setattr(mixed.sliders, slider_name, blended)

        return mixed

    def create_gradient(self, start_id: str, end_id: str,
                       steps: int = 5) -> List[PersonalityConfig]:
        """
        Create smooth gradient between two personalities

        Example:
            create_gradient("jarvis", "buddy", 5)
            → [Jarvis, 75% Jarvis + 25% Buddy, 50/50, 25% Jarvis + 75% Buddy, Buddy]
        """
        personalities = []
        for i in range(steps):
            strength = i / (steps - 1) if steps > 1 else 0
            mixed = self.mix_personalities(start_id, end_id, strength)
            mixed.name = f"{start_id}→{end_id} ({int(strength*100)}%)"
            personalities.append(mixed)

        return personalities
```

**Example Mixtures**:

```python
# Professional but friendly
mix("jarvis", "buddy", 0.3)
# → 70% Jarvis + 30% Buddy = Professional with warmth

# Wise but playful
mix("professor", "spark", 0.4)
# → 60% Professor + 40% Spark = Knowledgeable but energetic

# Flirty but intimate
mix("flirty", "intimate", 0.6)
# → 40% Flirty + 60% Intimate = Deeper romantic connection

# Sassy but caring
mix("sassy", "buddy", 0.5)
# → 50/50 = Bold but supportive
```

---

## 4. Advanced Customization Features

### 4.1 Time-Based Personality Shifts

```python
class PersonalityScheduler:
    """Change personality based on time of day or context"""

    def __init__(self):
        self.schedules: Dict[str, PersonalitySchedule] = {}

    def add_schedule(self, name: str, schedule: dict):
        """
        Define time-based personality changes

        Example:
            {
                "morning": {"personality": "professor", "time_range": "06:00-12:00"},
                "afternoon": {"personality": "buddy", "time_range": "12:00-18:00"},
                "evening": {"personality": "sage", "time_range": "18:00-22:00"},
                "night": {"personality": "intimate", "time_range": "22:00-06:00"}
            }
        """
        self.schedules[name] = PersonalitySchedule.from_dict(schedule)

    def get_current_personality(self, schedule_name: str) -> str:
        """Get appropriate personality for current time"""
        schedule = self.schedules.get(schedule_name)
        if not schedule:
            return self.default_personality

        current_time = datetime.now().time()

        for period_name, period_config in schedule.periods.items():
            if self._time_in_range(current_time, period_config['time_range']):
                return period_config['personality']

        return self.default_personality
```

### 4.2 Mood-Responsive Personality

```python
class MoodResponsivePersonality:
    """Automatically adjust personality based on detected user mood"""

    def adjust_for_mood(self, base_config: PersonalityConfig,
                       detected_emotion: str) -> PersonalityConfig:
        """
        Adjust personality sliders based on user's emotional state

        Detected emotions: happy, sad, angry, frustrated, anxious, excited
        """
        adjusted = copy.deepcopy(base_config)

        # Emotional adaptation rules
        if detected_emotion == "sad":
            adjusted.sliders.warmth = min(100, adjusted.sliders.warmth + 20)
            adjusted.sliders.empathy = min(100, adjusted.sliders.empathy + 15)
            adjusted.sliders.humor = max(0, adjusted.sliders.humor - 30)
            adjusted.sliders.enthusiasm = max(0, adjusted.sliders.enthusiasm - 20)

        elif detected_emotion == "angry":
            adjusted.sliders.patience = min(100, adjusted.sliders.patience + 30)
            adjusted.sliders.warmth = min(100, adjusted.sliders.warmth + 15)
            adjusted.sliders.directness = max(0, adjusted.sliders.directness - 20)

        elif detected_emotion == "anxious":
            adjusted.sliders.patience = min(100, adjusted.sliders.patience + 25)
            adjusted.sliders.confidence = min(100, adjusted.sliders.confidence + 15)
            adjusted.sliders.speed = max(0, adjusted.sliders.speed - 20)
            adjusted.sliders.verbosity = max(0, adjusted.sliders.verbosity - 20)

        elif detected_emotion == "excited":
            adjusted.sliders.enthusiasm = min(100, adjusted.sliders.enthusiasm + 20)
            adjusted.sliders.humor = min(100, adjusted.sliders.humor + 10)

        elif detected_emotion == "frustrated":
            adjusted.sliders.patience = min(100, adjusted.sliders.patience + 30)
            adjusted.sliders.empathy = min(100, adjusted.sliders.empathy + 20)
            adjusted.sliders.humor = max(0, adjusted.sliders.humor - 20)
            adjusted.sliders.proactivity = min(100, adjusted.sliders.proactivity + 20)

        return adjusted
```

### 4.3 Context-Aware Personality

```python
class ContextAwarePersonality:
    """Adjust personality based on conversation context"""

    def adjust_for_context(self, base_config: PersonalityConfig,
                          context: ConversationContext) -> PersonalityConfig:
        """
        Adjust personality based on:
        - Topic (technical, personal, creative, etc.)
        - Urgency
        - Conversation length
        - User preferences
        """
        adjusted = copy.deepcopy(base_config)

        # Topic-based adjustments
        if context.topic == "technical":
            adjusted.sliders.formality += 20
            adjusted.sliders.technical_depth += 30
            adjusted.sliders.humor -= 20

        elif context.topic == "personal":
            adjusted.sliders.warmth += 20
            adjusted.sliders.empathy += 20
            adjusted.sliders.casualness += 15

        elif context.topic == "creative":
            adjusted.sliders.enthusiasm += 25
            adjusted.sliders.humor += 15
            adjusted.sliders.storytelling += 30

        # Urgency adjustments
        if context.urgency == "high":
            adjusted.sliders.directness += 30
            adjusted.sliders.verbosity -= 40
            adjusted.sliders.speed += 20

        # Conversation length adjustments (get more casual over time)
        if context.turn_count > 50:
            adjusted.sliders.formality = max(0, adjusted.sliders.formality - 20)
            adjusted.sliders.casualness = min(100, adjusted.sliders.casualness + 20)

        return adjusted
```

---

## 5. Boundary & Safety System

### 5.1 Boundary Configuration

```python
class BoundaryManager:
    """Manages content boundaries for NSFW personalities"""

    def __init__(self, age_verified: bool = False):
        self.age_verified = age_verified
        self.hard_boundaries: Set[str] = set()  # Never cross these
        self.soft_boundaries: Set[str] = set()  # Warn before crossing
        self.user_preferences: Dict[str, str] = {}

    def set_hard_boundary(self, topic: str):
        """Set a topic that should NEVER be discussed"""
        self.hard_boundaries.add(topic.lower())

    def set_soft_boundary(self, topic: str, preference: str = "ask_first"):
        """
        Set a topic that requires permission

        preference: 'ask_first', 'warn_only', 'allow_once'
        """
        self.soft_boundaries.add(topic.lower())
        self.user_preferences[topic.lower()] = preference

    def check_content(self, message: str) -> BoundaryCheckResult:
        """Check if message crosses any boundaries"""
        message_lower = message.lower()

        # Check hard boundaries
        for boundary in self.hard_boundaries:
            if boundary in message_lower:
                return BoundaryCheckResult(
                    allowed=False,
                    reason="hard_boundary",
                    boundary=boundary,
                    action="block"
                )

        # Check soft boundaries
        for boundary in self.soft_boundaries:
            if boundary in message_lower:
                pref = self.user_preferences.get(boundary, "ask_first")
                return BoundaryCheckResult(
                    allowed=False,
                    reason="soft_boundary",
                    boundary=boundary,
                    action=pref
                )

        return BoundaryCheckResult(allowed=True)

    def get_boundary_response(self, boundary: str, action: str) -> str:
        """Generate appropriate response when boundary is encountered"""
        if action == "block":
            return f"I understand you're asking about {boundary}, but that's a topic I'm not comfortable discussing based on your preferences."

        elif action == "ask_first":
            return f"I notice this relates to {boundary}. You've set this as a sensitive topic. Would you like me to continue?"

        elif action == "warn_only":
            return f"[Content Warning: {boundary}] "

        return ""
```

**Example Boundary Setup**:

```python
# User's boundary configuration
boundaries = BoundaryManager(age_verified=True)

# Hard boundaries (NEVER discuss)
boundaries.set_hard_boundary("illegal activities")
boundaries.set_hard_boundary("self-harm")
boundaries.set_hard_boundary("violence against others")

# Soft boundaries (Ask first)
boundaries.set_soft_boundary("sexual content", preference="ask_first")
boundaries.set_soft_boundary("political topics", preference="warn_only")
boundaries.set_soft_boundary("religion", preference="ask_first")

# Check message before sending
result = boundaries.check_content(assistant_message)
if not result.allowed:
    if result.action == "block":
        # Don't send message, use boundary response instead
        return boundaries.get_boundary_response(result.boundary, result.action)
    elif result.action == "ask_first":
        # Ask user permission
        permission = await ask_user(boundaries.get_boundary_response(result.boundary, result.action))
        if not permission:
            return "Understood. Let's talk about something else."
```

---

## 6. Personality Storage & Sharing

### 6.1 File Format

**File**: `~/.goose/personalities/custom_companion.json`

```json
{
  "name": "My Perfect Companion",
  "version": "1.0",
  "base_preset": "buddy",
  "content_rating": "18+",
  "created_at": "2026-02-07T10:30:00Z",
  "sliders": {
    "warmth": 85,
    "formality": 25,
    "humor": 80,
    "enthusiasm": 75,
    "flirtiness": 60,
    "explicitness": 20
  },
  "accent": "US",
  "voice_clone_path": "~/.goose/voices/my_custom_voice.wav",
  "custom_phrases": [
    "Hey you!",
    "Miss me?",
    "Let's do this!"
  ],
  "greeting_style": "flirty",
  "hard_boundaries": [
    "illegal activities",
    "self-harm"
  ],
  "soft_boundaries": [
    "politics",
    "religion"
  ]
}
```

### 6.2 Personality Marketplace (Future Feature)

```python
class PersonalityMarketplace:
    """Share and download custom personalities (FUTURE)"""

    def export_for_sharing(self, config: PersonalityConfig) -> str:
        """
        Export personality for sharing with others

        Note: Voice clones NOT included (privacy/copyright)
        NSFW settings require age verification on import
        """
        shareable = config.to_dict()

        # Remove personal data
        shareable.pop('voice_clone_path', None)
        shareable.pop('hard_boundaries', None)  # Personal boundaries not shared
        shareable.pop('soft_boundaries', None)

        # Add metadata
        shareable['shared_by'] = "anonymous"
        shareable['downloads'] = 0
        shareable['rating'] = 0.0

        return json.dumps(shareable, indent=2)

    def import_from_marketplace(self, personality_json: str,
                               age_verified: bool) -> PersonalityConfig:
        """Import personality from marketplace"""
        config = PersonalityConfig.from_dict(json.loads(personality_json))

        # Filter NSFW content based on age verification
        if not age_verified and config.content_rating in ['18+', '21+']:
            # Reset NSFW sliders to safe values
            config.sliders.flirtiness = 0
            config.sliders.explicitness = 0
            config.sliders.romantic_interest = 0
            config.sliders.intimacy = 0
            config.sliders.profanity = 0
            config.content_rating = "safe"

        return config
```

---

## 7. Implementation Timeline

### Week 1: Core Personality System
- [ ] Implement `PersonalityConfig` and `PersonalitySliders`
- [ ] Create 5 safe-rated presets (Jarvis, Buddy, Professor, Spark, Sage)
- [ ] Build personality loader and saver
- [ ] Integrate with voice engine

### Week 2: Age Verification & NSFW System
- [ ] Implement `AgeVerification` system
- [ ] Create content rating system (safe, 18+, 21+)
- [ ] Add NSFW personality presets (Flirty, Sassy, Intimate, Uncensored, Playful)
- [ ] Build `BoundaryManager` for safety

### Week 3: Personality Studio UI
- [ ] Design and build slider interface
- [ ] Create preset selector
- [ ] Add real-time preview system
- [ ] Implement save/load/export functionality

### Week 4: Advanced Features
- [ ] Implement `PersonalityMixer` for hybrid personalities
- [ ] Add mood-responsive adjustments
- [ ] Create context-aware personality system
- [ ] Build time-based scheduling

### Week 5: Testing & Polish
- [ ] Test all personality presets
- [ ] Verify age gate system
- [ ] Test boundary enforcement
- [ ] User testing with custom personalities

---

## 8. Legal & Ethical Considerations

### 8.1 Age Verification Requirements

```
IMPORTANT LEGAL NOTICE:

1. Age verification REQUIRED for NSFW content
2. Users must confirm they are 18+ (or 21+ depending on jurisdiction)
3. No circumvention of age gate allowed
4. Clear content warnings displayed
5. User can disable NSFW content at any time
```

### 8.2 Content Disclaimers

```
NSFW Content Disclaimer:

• This companion uses AI and may produce unpredictable content
• User is responsible for appropriate use
• Content does not reflect views of developers
• Boundaries are user-configurable and should be respected
• AI cannot provide therapy, legal advice, or professional services
• This is entertainment software, not a replacement for human relationships
```

### 8.3 Default Safety Settings

```python
# Default configuration (safe for all users)
DEFAULT_CONFIG = {
    "content_rating": "safe",
    "require_age_verification": True,
    "default_boundaries": [
        "illegal activities",
        "self-harm",
        "violence",
        "exploitation"
    ],
    "nsfw_locked": True,  # Unlocked only after age verification
    "max_explicitness": 0,  # Cannot be changed without verification
}
```

---

## Success Metrics

**Customization**:
- ✅ 20+ slider controls for complete personality tuning
- ✅ 5+ safe-rated presets + 5+ NSFW presets (18+/21+)
- ✅ Personality mixing system for hybrid personalities
- ✅ Save/load/export custom personalities
- ✅ Real-time preview of personality changes

**Safety & Boundaries**:
- ✅ Robust age verification system
- ✅ Configurable hard & soft boundaries
- ✅ Content rating system (safe, 18+, 21+)
- ✅ User control over all NSFW features
- ✅ Clear warnings and disclaimers

**Advanced Features**:
- ✅ Mood-responsive personality adjustments
- ✅ Context-aware behavior changes
- ✅ Time-based personality scheduling
- ✅ Personality gradient creation
- ✅ Marketplace for sharing (future)

---

**Your Companion, Your Way - Complete Creative Control with Responsible Boundaries** 🎭✨
