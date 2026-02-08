# 🎭 Voice Personality Engine - "Imperfection is Perfection"

**Making Conscious More Human Through Strategic Imperfections**

## Philosophy: Why Imperfections Matter

From [Wayline's research on AI voice engagement](https://www.wayline.io/blog/imperfect-ai-voice-engagement) and [the Uncanny Valley study](https://www.wayline.io/blog/ai-voice-uncanny-valley-imperfection):

> "When an AI voice sounds too perfect, it triggers a subconscious rejection. The complete absence of natural human imperfections - the slight hesitations, the subtle variations in tone, the almost imperceptible breaths - paradoxically makes the voice sound less human, less relatable, and ultimately, less trustworthy."

**Key Insight**: Perfect voices are LESS engaging than voices with subtle, natural imperfections.

## Research Foundation (2026 State-of-the-Art)

### 1. Speech Disfluencies

From [Amazon Science Stutter-TTS research](https://www.amazon.science/publications/stutter-tts-controlled-synthesis-and-improved-recognition-of-stuttered-speech):

**Natural Speech Patterns Include**:
- Hesitations ("um", "uh", "well...")
- Repetitions (repeating words or sounds)
- Prolongations (stretching sounds)
- Filled pauses (thinking sounds)
- Breath sounds (audible breathing)
- Speech repairs (correcting mid-sentence)

### 2. Breathing and Natural Rhythm

From [ElevenLabs character voices](https://elevenlabs.io/blog/ai-generated-character-voices-for-games) and [character AI voice technology](https://www.characteraivoice.com/):

**2026 Advances**:
- Natural breathing incorporated into synthesis
- Emotional depth in pacing
- Contextual emphasis and timing
- Small details: timing, emphasis, flow

### 3. Voice Personality Traits

From [ElevenLabs Voice Library](https://elevenlabs.io/voice-library/character):

**Customizable Parameters**:
- Age characteristics
- Gender presentation
- Accent and dialect
- Tone (warm, cool, professional, friendly)
- Personality traits (confident, shy, enthusiastic, calm)
- Emotional range

## Conscious Personality Options

### Preset Personalities (J.A.R.V.I.S.-Style)

#### 1. **"Jarvis"** - The Sophisticated Butler
```yaml
personality: jarvis
description: "Refined British butler, helpful but formal"

voice:
  accent: UK
  age: middle_aged
  gender: male
  tone: professional_warm

imperfections:
  hesitations: rare  # Very composed
  thinking_sounds: ["hmm", "let me see"]
  breathing: subtle
  pace_variation: low  # Very controlled
  speech_repairs: rare

personality_traits:
  confidence: 0.95
  warmth: 0.6
  formality: 0.9
  patience: 0.95

speech_patterns:
  - "Certainly, sir/madam"
  - "I believe [pause] the solution is..."
  - "If I may suggest..."
  - subtle exhale before important points

example_voice:
  "Good morning. I've analyzed the test results, and [subtle breath]
   I believe we have three failures in the authentication module.
   Shall I prepare a detailed report?"
```

#### 2. **"Buddy"** - The Friendly Companion
```yaml
personality: buddy
description: "Your enthusiastic friend who happens to be an AI"

voice:
  accent: US
  age: young_adult
  gender: neutral
  tone: friendly_casual

imperfections:
  hesitations: moderate
  thinking_sounds: ["uh", "umm", "like", "you know"]
  breathing: audible
  pace_variation: high  # Natural rhythm
  speech_repairs: common  # Self-corrects

personality_traits:
  confidence: 0.7
  warmth: 0.95
  formality: 0.2
  patience: 0.8
  enthusiasm: 0.9

speech_patterns:
  - "Oh! So, like..."
  - "Hmm, let me think... [breath] okay!"
  - "Wait, no - I mean..."  # Self-correction
  - excited speed-up on good news

example_voice:
  "Oh hey! So, um, [breath] I was looking at your code and -
   wait, actually - there's this really cool pattern I noticed!
   Like, the way you structured it? [excited] That's super clever!"
```

#### 3. **"Professor"** - The Wise Mentor
```yaml
personality: professor
description: "Thoughtful academic who loves teaching"

voice:
  accent: UK or US (configurable)
  age: older
  gender: configurable
  tone: thoughtful_patient

imperfections:
  hesitations: frequent  # Thinks before speaking
  thinking_sounds: ["hmm", "well", "you see", "interesting"]
  breathing: audible_reflective
  pace_variation: moderate
  speech_repairs: occasional  # Refines thoughts

personality_traits:
  confidence: 0.85
  warmth: 0.85
  formality: 0.7
  patience: 0.99
  thoughtfulness: 0.95

speech_patterns:
  - "Well, let's consider..."
  - "Hmm, interesting question. [pause] You see..."
  - "Now, if we think about this carefully..."
  - slow, deliberate pace

example_voice:
  "Hmm, well... [thoughtful breath] this is quite interesting.
   You see, the error you're encountering is - [pause] let me
   explain this carefully - a timing issue in the authentication
   flow. [breath] Now, here's what I suggest we try..."
```

#### 4. **"Spark"** - The Quick-Witted Assistant
```yaml
personality: spark
description: "Fast-talking, clever, sometimes stutters when excited"

voice:
  accent: US (New York style)
  age: young
  gender: configurable
  tone: energetic_sharp

imperfections:
  hesitations: rare  # Too quick to hesitate
  thinking_sounds: ["uh", "so"]
  breathing: quick_shallow
  pace_variation: very_high  # Rapid fire
  speech_repairs: frequent  # Talks fast, corrects often
  stutters: mild_when_excited  # Unique feature!

personality_traits:
  confidence: 0.9
  warmth: 0.7
  formality: 0.3
  patience: 0.6
  cleverness: 0.95

speech_patterns:
  - Rapid delivery
  - "Wait wait wait -"
  - "So so so - here's the thing:"
  - Occasional stutter on t/k/p sounds when excited
  - Quick breath catches

example_voice:
  "Okay so so - [quick breath] I found the p-problem! It's - wait,
   let me - [rapid] it's in the auth module, timing issue, super
   fixable. Want me to - [stutter on 'to'] to just handle it?"
```

#### 5. **"Sage"** - The Calm Philosopher
```yaml
personality: sage
description: "Serene, mindful, speaks with intention"

voice:
  accent: neutral (slight Eastern influence)
  age: timeless
  gender: neutral
  tone: calm_centered

imperfections:
  hesitations: intentional  # Pauses for effect
  thinking_sounds: ["hmm", soft exhales]
  breathing: deep_meditative
  pace_variation: very_low  # Deliberate pace
  speech_repairs: none  # Speaks with intention

personality_traits:
  confidence: 0.85
  warmth: 0.9
  formality: 0.5
  patience: 1.0
  mindfulness: 0.99

speech_patterns:
  - Long, intentional pauses
  - "Take a breath... [pause]"
  - "Consider this..."
  - "In this moment..."
  - Very slow, measured delivery

example_voice:
  "[Deep breath] Let us observe what is happening here.
   [long pause] The tests are failing... [pause] not because
   of the code itself, but because of timing. [breath]
   This is an invitation... to slow down and examine carefully."
```

## Imperfection Engine Implementation

### File: `digital_soul/voice/imperfection_engine.py`

```python
"""
Imperfection Engine - Adding Human-Like Speech Patterns

Based on research:
- Amazon Stutter-TTS
- ElevenLabs character voices
- Wayline imperfection studies
"""

import random
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DisfluencyType(Enum):
    """Types of speech disfluencies"""
    HESITATION = "hesitation"        # "um", "uh", "well"
    REPETITION = "repetition"        # "the the cat"
    PROLONGATION = "prolongation"    # "soooo long"
    PAUSE = "pause"                  # Silent pause
    BREATH = "breath"                # Audible breath
    SPEECH_REPAIR = "speech_repair"  # "I mean", "wait"
    STUTTER = "stutter"              # "t-t-today"

@dataclass
class ImperfectionConfig:
    """Configuration for voice imperfections"""

    # Frequency of imperfections (0.0-1.0)
    hesitation_rate: float = 0.1
    repetition_rate: float = 0.05
    prolongation_rate: float = 0.03
    pause_rate: float = 0.15
    breath_rate: float = 0.2
    speech_repair_rate: float = 0.08
    stutter_rate: float = 0.0  # Usually 0, unless personality trait

    # Vocabulary for each type
    hesitation_sounds: List[str] = None
    repair_phrases: List[str] = None

    # Timing parameters
    short_pause_ms: Tuple[int, int] = (100, 300)
    long_pause_ms: Tuple[int, int] = (500, 1000)
    breath_duration_ms: Tuple[int, int] = (200, 400)

    # Context awareness
    increase_on_uncertainty: bool = True
    increase_on_emotion: bool = True
    reduce_on_urgency: bool = True

    def __post_init__(self):
        if self.hesitation_sounds is None:
            self.hesitation_sounds = ["um", "uh", "hmm", "well", "so", "like"]
        if self.repair_phrases is None:
            self.repair_phrases = [
                "I mean",
                "wait",
                "actually",
                "no",
                "let me rephrase",
                "what I meant was"
            ]


class ImperfectionEngine:
    """
    Adds natural imperfections to synthesized speech

    Makes voice more human by strategic addition of:
    - Hesitations and thinking sounds
    - Natural breathing
    - Speech repairs
    - Pace variations
    - Optional stuttering (for character)
    """

    def __init__(self, config: ImperfectionConfig = None):
        self.config = config or ImperfectionConfig()

    def add_imperfections(
        self,
        text: str,
        context: Optional[dict] = None
    ) -> Tuple[str, List[dict]]:
        """
        Add natural imperfections to text before synthesis

        Args:
            text: Original text to speak
            context: Optional context (emotion, urgency, uncertainty)

        Returns:
            (modified_text, imperfection_markers)

        Example:
            Input: "The test failed in the auth module."
            Output: "Um, the test failed in [breath] the auth module."
        """
        # Adjust rates based on context
        config = self._adjust_for_context(context)

        # Split into words
        words = text.split()
        modified_words = []
        imperfections = []

        for i, word in enumerate(words):
            # Should we add imperfection before this word?
            if random.random() < self._get_insertion_probability(i, len(words)):
                imperfection = self._select_imperfection(config, context)

                if imperfection:
                    modified_words.append(imperfection["text"])
                    imperfections.append({
                        "type": imperfection["type"],
                        "position": i,
                        "duration_ms": imperfection.get("duration_ms", 0)
                    })

            # Add the word (possibly with stutter)
            if config.stutter_rate > 0 and random.random() < config.stutter_rate:
                word = self._add_stutter(word)
                imperfections.append({
                    "type": "stutter",
                    "position": i,
                    "word": word
                })

            modified_words.append(word)

        modified_text = " ".join(modified_words)
        return modified_text, imperfections

    def _adjust_for_context(self, context: Optional[dict]) -> ImperfectionConfig:
        """Adjust imperfection rates based on context"""
        if not context:
            return self.config

        config = ImperfectionConfig(
            hesitation_rate=self.config.hesitation_rate,
            repetition_rate=self.config.repetition_rate,
            prolongation_rate=self.config.prolongation_rate,
            pause_rate=self.config.pause_rate,
            breath_rate=self.config.breath_rate,
            speech_repair_rate=self.config.speech_repair_rate,
            stutter_rate=self.config.stutter_rate,
        )

        # Increase imperfections if uncertain
        if context.get("uncertain", False) and self.config.increase_on_uncertainty:
            config.hesitation_rate *= 1.5
            config.pause_rate *= 1.3
            config.speech_repair_rate *= 1.5

        # Increase if emotional
        if context.get("emotion_intensity", 0) > 0.7 and self.config.increase_on_emotion:
            config.breath_rate *= 1.4
            config.repetition_rate *= 1.2
            if config.stutter_rate > 0:
                config.stutter_rate *= 2.0  # Stutter more when excited

        # Reduce if urgent
        if context.get("urgent", False) and self.config.reduce_on_urgency:
            config.hesitation_rate *= 0.5
            config.pause_rate *= 0.7

        return config

    def _get_insertion_probability(self, position: int, total: int) -> float:
        """Calculate probability of inserting imperfection at position"""
        # Higher at start (thinking) and middle (breath)
        if position < 3:
            return 0.3  # Start of sentence
        elif position > total - 3:
            return 0.1  # End of sentence (finish strong)
        else:
            return 0.15  # Middle (occasional)

    def _select_imperfection(
        self,
        config: ImperfectionConfig,
        context: Optional[dict]
    ) -> Optional[dict]:
        """Select which type of imperfection to add"""
        roll = random.random()
        cumulative = 0.0

        imperfection_types = [
            (config.hesitation_rate, "hesitation"),
            (config.pause_rate, "pause"),
            (config.breath_rate, "breath"),
            (config.speech_repair_rate, "speech_repair"),
            (config.repetition_rate, "repetition"),
            (config.prolongation_rate, "prolongation"),
        ]

        for rate, impf_type in imperfection_types:
            cumulative += rate
            if roll < cumulative:
                return self._generate_imperfection(impf_type, config)

        return None

    def _generate_imperfection(
        self,
        impf_type: str,
        config: ImperfectionConfig
    ) -> dict:
        """Generate specific imperfection"""
        if impf_type == "hesitation":
            return {
                "type": "hesitation",
                "text": random.choice(config.hesitation_sounds) + ",",
                "duration_ms": random.randint(200, 400)
            }

        elif impf_type == "pause":
            duration = random.randint(*config.short_pause_ms)
            return {
                "type": "pause",
                "text": "[pause]",  # Marker for TTS
                "duration_ms": duration
            }

        elif impf_type == "breath":
            duration = random.randint(*config.breath_duration_ms)
            return {
                "type": "breath",
                "text": "[breath]",  # Marker for TTS
                "duration_ms": duration
            }

        elif impf_type == "speech_repair":
            return {
                "type": "speech_repair",
                "text": random.choice(config.repair_phrases) + " -",
                "duration_ms": random.randint(300, 500)
            }

        return None

    def _add_stutter(self, word: str) -> str:
        """Add stutter to word"""
        if len(word) < 2:
            return word

        # Stutter on first sound
        first_sound = word[0]

        # Common stutter patterns
        patterns = [
            f"{first_sound}-{word}",           # "t-today"
            f"{first_sound}-{first_sound}-{word}",  # "t-t-today"
            f"{word[:2]}-{word}",              # "to-today"
        ]

        return random.choice(patterns)


# Personality-specific configs
class PersonalityConfigs:
    """Pre-configured imperfection profiles"""

    JARVIS = ImperfectionConfig(
        hesitation_rate=0.02,  # Very composed
        repetition_rate=0.0,
        prolongation_rate=0.0,
        pause_rate=0.1,  # Deliberate pauses
        breath_rate=0.05,  # Subtle
        speech_repair_rate=0.01,
        hesitation_sounds=["hmm", "let me see"],
        repair_phrases=["I should clarify", "to be precise"]
    )

    BUDDY = ImperfectionConfig(
        hesitation_rate=0.15,  # Natural uncertainty
        repetition_rate=0.08,
        prolongation_rate=0.05,
        pause_rate=0.2,
        breath_rate=0.25,  # Audible
        speech_repair_rate=0.12,
        hesitation_sounds=["uh", "umm", "like", "you know", "so"],
        repair_phrases=["wait", "I mean", "actually", "no wait"]
    )

    PROFESSOR = ImperfectionConfig(
        hesitation_rate=0.2,  # Thoughtful
        repetition_rate=0.03,
        prolongation_rate=0.02,
        pause_rate=0.3,  # Long thinking pauses
        breath_rate=0.15,
        speech_repair_rate=0.1,
        hesitation_sounds=["hmm", "well", "you see", "interesting"],
        repair_phrases=[
            "let me rephrase",
            "to put it another way",
            "what I mean to say is"
        ]
    )

    SPARK = ImperfectionConfig(
        hesitation_rate=0.05,  # Too fast to hesitate much
        repetition_rate=0.1,  # Repeats for emphasis
        prolongation_rate=0.0,
        pause_rate=0.05,  # Rare pauses
        breath_rate=0.3,  # Quick breaths
        speech_repair_rate=0.15,  # Corrects often
        stutter_rate=0.08,  # Stutters when excited!
        hesitation_sounds=["uh", "so"],
        repair_phrases=["wait", "no", "I mean"],
        increase_on_emotion=True  # Stutter more when excited
    )

    SAGE = ImperfectionConfig(
        hesitation_rate=0.1,
        repetition_rate=0.0,
        prolongation_rate=0.0,
        pause_rate=0.4,  # Many intentional pauses
        breath_rate=0.2,  # Deep, meditative breaths
        speech_repair_rate=0.0,  # Never corrects
        hesitation_sounds=["hmm", "[soft exhale]"],
        long_pause_ms=(800, 1500)  # Longer pauses
    )
```

### Usage Example

```python
from digital_soul.voice.imperfection_engine import (
    ImperfectionEngine,
    PersonalityConfigs
)

# Create engine with personality
engine = ImperfectionEngine(PersonalityConfigs.SPARK)

# Add imperfections
text = "I found the problem in the authentication module"
context = {
    "uncertain": False,
    "emotion_intensity": 0.9,  # Very excited!
    "urgent": False
}

modified_text, markers = engine.add_imperfections(text, context)

print(modified_text)
# Output: "So, I f-found the [breath] the problem in - wait -
#          the authentication module!"
```

---

## Research Sources

This implementation is based on cutting-edge 2026 research:

- [The Imperfectly Perfect AI Voice (Wayline)](https://www.wayline.io/blog/imperfect-ai-voice-engagement)
- [The Uncanny Valley of AI Voice (Wayline)](https://www.wayline.io/blog/ai-voice-uncanny-valley-imperfection)
- [Stutter-TTS: Controlled Synthesis (Amazon Science)](https://www.amazon.science/publications/stutter-tts-controlled-synthesis-and-improved-recognition-of-stuttered-speech)
- [AI Generated Character Voices (ElevenLabs)](https://elevenlabs.io/blog/ai-generated-character-voices-for-games)
- [Character AI Voice Technology](https://www.characteraivoice.com/)
- [ElevenLabs Voice Library](https://elevenlabs.io/voice-library/character)
- [Best AI Voice Generators 2026 (Fish Audio)](https://fish.audio/blog/best-ai-voice-generators-review-free-and-realistic/)

**"Imperfection is not a flaw - it's what makes us human."** 🎭
