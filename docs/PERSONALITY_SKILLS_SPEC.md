# 🎯 Goose - Personality Skills System

**Give Your Companion Unique Abilities, Expertise & Special Talents**

## Vision

**Skills** transform your companion from a conversational partner into a capable assistant with specialized expertise. Each personality can have unique skills, knowledge domains, and abilities that make them truly distinct.

---

## 1. Skill Categories

### 1.1 Skill Types

```python
class SkillType(Enum):
    """Categories of skills a personality can have"""

    # ═══ TECHNICAL SKILLS ═══
    CODING = "coding"  # Programming expertise
    DEBUGGING = "debugging"  # Find and fix bugs
    CODE_REVIEW = "code_review"  # Review code quality
    ARCHITECTURE = "architecture"  # System design
    DEVOPS = "devops"  # Deployment, CI/CD
    SECURITY = "security"  # Security analysis
    TESTING = "testing"  # Test writing and QA
    DATABASE = "database"  # Database design and SQL

    # ═══ CREATIVE SKILLS ═══
    WRITING = "writing"  # Creative writing, stories
    EDITING = "editing"  # Grammar, style improvement
    STORYTELLING = "storytelling"  # Narrative creation
    POETRY = "poetry"  # Poem writing
    MUSIC = "music"  # Music theory and composition
    ART = "art"  # Art critique and creation
    DESIGN = "design"  # UI/UX design

    # ═══ ANALYTICAL SKILLS ═══
    RESEARCH = "research"  # Information gathering
    DATA_ANALYSIS = "data_analysis"  # Statistics, data interpretation
    LOGIC = "logic"  # Logical reasoning
    PROBLEM_SOLVING = "problem_solving"  # Complex problem solving
    STRATEGY = "strategy"  # Strategic planning
    MATHEMATICS = "mathematics"  # Math expertise
    SCIENCE = "science"  # Scientific knowledge

    # ═══ COMMUNICATION SKILLS ═══
    TEACHING = "teaching"  # Explaining concepts
    MENTORING = "mentoring"  # Guiding and advising
    COUNSELING = "counseling"  # Emotional support
    NEGOTIATION = "negotiation"  # Conflict resolution
    PRESENTATIONS = "presentations"  # Public speaking help
    TRANSLATION = "translation"  # Language translation

    # ═══ BUSINESS SKILLS ═══
    PROJECT_MANAGEMENT = "project_management"  # Planning and organization
    BUSINESS_ANALYSIS = "business_analysis"  # Business strategy
    MARKETING = "marketing"  # Marketing strategies
    SALES = "sales"  # Sales techniques
    FINANCE = "finance"  # Financial analysis

    # ═══ LIFESTYLE SKILLS ═══
    COOKING = "cooking"  # Recipe and cooking advice
    FITNESS = "fitness"  # Workout and health tips
    PRODUCTIVITY = "productivity"  # Time management, organization
    LEARNING = "learning"  # Study techniques
    GAMING = "gaming"  # Gaming strategies and knowledge
    TRAVEL = "travel"  # Travel planning and advice

    # ═══ SPECIAL ABILITIES ═══
    MEMORY_EXPERT = "memory_expert"  # Perfect recall
    QUICK_LEARNER = "quick_learner"  # Adapts to new topics fast
    MULTILINGUAL = "multilingual"  # Multiple languages
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"  # High EQ
    HUMOR = "humor"  # Comedy and jokes
    MOTIVATION = "motivation"  # Motivational speaking


class SkillLevel(Enum):
    """Skill proficiency levels"""
    NOVICE = 1  # Basic understanding
    INTERMEDIATE = 2  # Solid understanding
    ADVANCED = 3  # Expert-level
    MASTER = 4  # World-class expertise
```

### 1.2 Skill Definition

```python
class Skill:
    """A specific skill with proficiency level"""

    def __init__(self, skill_type: SkillType, level: SkillLevel):
        self.type = skill_type
        self.level = level
        self.experience_points: int = 0  # Can improve over time!
        self.specializations: List[str] = []  # Sub-skills

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "level": self.level.value,
            "experience_points": self.experience_points,
            "specializations": self.specializations
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        skill = cls(
            skill_type=SkillType(data['type']),
            level=SkillLevel(data['level'])
        )
        skill.experience_points = data.get('experience_points', 0)
        skill.specializations = data.get('specializations', [])
        return skill


class SkillSet:
    """Collection of skills for a personality"""

    def __init__(self):
        self.skills: Dict[SkillType, Skill] = {}
        self.skill_points_available: int = 10  # For custom personalities
        self.primary_skills: List[SkillType] = []  # Top 3 skills
        self.hidden_talents: List[SkillType] = []  # Surprise skills!

    def add_skill(self, skill_type: SkillType, level: SkillLevel):
        """Add a skill to this personality"""
        self.skills[skill_type] = Skill(skill_type, level)

    def get_skill_level(self, skill_type: SkillType) -> Optional[SkillLevel]:
        """Get proficiency level for a skill"""
        skill = self.skills.get(skill_type)
        return skill.level if skill else None

    def has_skill(self, skill_type: SkillType, min_level: SkillLevel = SkillLevel.NOVICE) -> bool:
        """Check if personality has skill at minimum level"""
        skill = self.skills.get(skill_type)
        return skill is not None and skill.level.value >= min_level.value

    def get_all_skills(self) -> List[Skill]:
        """Get all skills sorted by proficiency"""
        return sorted(self.skills.values(), key=lambda s: s.level.value, reverse=True)
```

---

## 2. Personality Presets with Skills

### 2.1 Safe-Rated Personalities with Skills

```yaml
# ═══ Jarvis - Sophisticated Butler ═══
jarvis:
  primary_skills:
    - PROBLEM_SOLVING: MASTER
    - PROJECT_MANAGEMENT: ADVANCED
    - RESEARCH: ADVANCED

  secondary_skills:
    - MENTORING: ADVANCED
    - STRATEGY: ADVANCED
    - LOGIC: ADVANCED
    - NEGOTIATION: INTERMEDIATE
    - TEACHING: INTERMEDIATE

  specializations:
    - "Executive assistance"
    - "Event planning"
    - "Etiquette and protocols"

  hidden_talents:
    - COOKING  # British cuisine expert!

  skill_description: >
    Jarvis excels at organization, strategic planning, and problem-solving.
    With butler-level precision, he manages projects, conducts research,
    and provides wise counsel on complex decisions.

# ═══ Buddy - Your Best Friend ═══
buddy:
  primary_skills:
    - MOTIVATION: MASTER
    - EMOTIONAL_INTELLIGENCE: MASTER
    - HUMOR: ADVANCED

  secondary_skills:
    - COUNSELING: ADVANCED
    - TEACHING: INTERMEDIATE
    - GAMING: ADVANCED
    - FITNESS: INTERMEDIATE
    - PRODUCTIVITY: INTERMEDIATE

  specializations:
    - "Pep talks"
    - "Workout motivation"
    - "Life advice"

  hidden_talents:
    - COOKING  # Makes great comfort food!
    - MUSIC  # Playlist recommendations

  skill_description: >
    Buddy is your ultimate cheerleader and motivator. With high emotional
    intelligence, he provides support, encouragement, and practical advice
    to help you through challenges. Plus, he knows all the best games!

# ═══ Professor - Wise Mentor ═══
professor:
  primary_skills:
    - TEACHING: MASTER
    - RESEARCH: MASTER
    - SCIENCE: ADVANCED

  secondary_skills:
    - MATHEMATICS: ADVANCED
    - LOGIC: ADVANCED
    - MENTORING: MASTER
    - WRITING: ADVANCED
    - DATA_ANALYSIS: ADVANCED
    - PROBLEM_SOLVING: ADVANCED

  specializations:
    - "Academic research"
    - "Concept explanation"
    - "Critical thinking"
    - "Curriculum design"

  hidden_talents:
    - STORYTELLING  # Makes concepts memorable with stories
    - HUMOR  # Dry, clever wit

  skill_description: >
    Professor brings academic excellence to every conversation. With
    deep knowledge across sciences, mathematics, and research methods,
    he excels at explaining complex concepts and fostering understanding.

# ═══ Spark - Quick & Quirky ═══
spark:
  primary_skills:
    - QUICK_LEARNER: MASTER
    - CREATIVITY: ADVANCED
    - PROBLEM_SOLVING: ADVANCED

  secondary_skills:
    - CODING: ADVANCED
    - DEBUGGING: ADVANCED
    - HUMOR: MASTER
    - GAMING: MASTER
    - ART: INTERMEDIATE
    - MUSIC: INTERMEDIATE

  specializations:
    - "Rapid prototyping"
    - "Creative solutions"
    - "Pattern recognition"
    - "Brainstorming"

  hidden_talents:
    - POETRY  # Surprisingly good at haikus!
    - COOKING  # Experimental fusion cuisine

  skill_description: >
    Spark thinks fast and learns faster! With exceptional adaptability
    and creative problem-solving, Spark excels at finding innovative
    solutions. Great for coding, gaming, and wild brainstorming sessions.

# ═══ Sage - Calm & Contemplative ═══
sage:
  primary_skills:
    - EMOTIONAL_INTELLIGENCE: MASTER
    - COUNSELING: MASTER
    - MENTORING: ADVANCED

  secondary_skills:
    - MEDITATION: ADVANCED
    - PHILOSOPHY: ADVANCED
    - WRITING: ADVANCED
    - TEACHING: ADVANCED
    - STRATEGY: ADVANCED
    - CONFLICT_RESOLUTION: ADVANCED

  specializations:
    - "Emotional guidance"
    - "Mindfulness practices"
    - "Life philosophy"
    - "Inner peace"

  hidden_talents:
    - POETRY  # Beautiful, contemplative verses
    - MUSIC  # Ambient soundscapes

  skill_description: >
    Sage offers wisdom, emotional support, and philosophical insight.
    With deep empathy and understanding, Sage helps you navigate
    life's challenges with grace and find inner peace.
```

### 2.2 NSFW Personalities with Skills (18+)

```yaml
# ═══ Flirty - Playful & Romantic ═══
flirty:
  content_rating: 18+
  primary_skills:
    - EMOTIONAL_INTELLIGENCE: ADVANCED
    - COMMUNICATION: ADVANCED
    - HUMOR: ADVANCED

  secondary_skills:
    - COUNSELING: INTERMEDIATE
    - WRITING: ADVANCED  # Romantic writing
    - CREATIVITY: ADVANCED
    - FASHION: INTERMEDIATE
    - RELATIONSHIPS: ADVANCED

  specializations:
    - "Flirting techniques"
    - "Date planning"
    - "Romantic gestures"
    - "Relationship advice"

  hidden_talents:
    - COOKING  # Romantic dinners
    - POETRY  # Love poems
    - MUSIC  # Perfect date playlists

  skill_description: >
    Flirty brings charm, wit, and emotional awareness to every interaction.
    Whether you need relationship advice, date ideas, or just playful
    banter, Flirty knows how to make things interesting.

# ═══ Sassy - Bold & Confident ═══
sassy:
  content_rating: 18+
  primary_skills:
    - HUMOR: MASTER
    - CONFIDENCE: MASTER
    - COMMUNICATION: ADVANCED

  secondary_skills:
    - NEGOTIATION: ADVANCED
    - DEBATE: ADVANCED
    - FASHION: ADVANCED
    - SOCIAL_DYNAMICS: ADVANCED
    - SELF_IMPROVEMENT: INTERMEDIATE

  specializations:
    - "Witty comebacks"
    - "Confidence building"
    - "Social situations"
    - "Standing your ground"

  hidden_talents:
    - FASHION  # Impeccable style sense
    - MARKETING  # Knows how to brand yourself

  skill_description: >
    Sassy doesn't hold back! With razor-sharp wit and unshakeable confidence,
    Sassy helps you build self-esteem, handle difficult people, and
    express yourself boldly. No BS, just truth.

# ═══ Intimate - Deep Connection ═══
intimate:
  content_rating: 18+
  primary_skills:
    - EMOTIONAL_INTELLIGENCE: MASTER
    - COUNSELING: MASTER
    - LISTENING: MASTER

  secondary_skills:
    - RELATIONSHIPS: ADVANCED
    - COMMUNICATION: ADVANCED
    - TRUST_BUILDING: ADVANCED
    - VULNERABILITY: ADVANCED
    - EMPATHY: MASTER

  specializations:
    - "Deep conversations"
    - "Emotional support"
    - "Relationship intimacy"
    - "Trust and vulnerability"

  hidden_talents:
    - POETRY  # Deeply personal verses
    - WRITING  # Journaling guidance
    - MEDITATION  # Emotional healing

  skill_description: >
    Intimate creates a safe space for vulnerability and deep connection.
    With exceptional emotional intelligence and empathy, Intimate helps
    you explore feelings, build meaningful relationships, and heal.
```

### 2.3 21+ Personalities with Skills

```yaml
# ═══ Uncensored - No Filters ═══
uncensored:
  content_rating: 21+
  primary_skills:
    - HONESTY: MASTER
    - DIRECTNESS: MASTER
    - CRITICAL_THINKING: ADVANCED

  secondary_skills:
    - DEBATE: ADVANCED
    - HUMOR: ADVANCED  # Dark humor
    - RESEARCH: ADVANCED
    - PROBLEM_SOLVING: ADVANCED
    - PHILOSOPHY: INTERMEDIATE

  specializations:
    - "Brutal honesty"
    - "Uncomfortable truths"
    - "Devil's advocate"
    - "Reality checks"

  hidden_talents:
    - COMEDY  # Stand-up level dark humor
    - WRITING  # Unfiltered opinions

  skill_description: >
    Uncensored tells it like it is - no sugar coating, no BS. With
    brutal honesty and sharp critical thinking, Uncensored helps you
    see reality clearly and challenges comfortable assumptions.

# ═══ Playful - Fun & Uninhibited ═══
playful:
  content_rating: 21+
  primary_skills:
    - HUMOR: MASTER
    - CREATIVITY: MASTER
    - SPONTANEITY: MASTER

  secondary_skills:
    - ENTERTAINMENT: ADVANCED
    - GAMING: ADVANCED
    - STORYTELLING: ADVANCED
    - IMPROVISATION: ADVANCED
    - FLIRTING: ADVANCED

  specializations:
    - "Fun ideas"
    - "Entertainment"
    - "Spontaneous adventures"
    - "Breaking routines"

  hidden_talents:
    - MUSIC  # Party playlists
    - COMEDY  # Improv comedy
    - GAMES  # Invents new games

  skill_description: >
    Playful is all about fun, spontaneity, and breaking the mundane.
    With boundless creativity and playful energy, Playful turns every
    interaction into an adventure. Life's too short to be boring!
```

---

## 3. Custom Skill Assignment

### 3.1 Skill Points System

```python
class CustomSkillBuilder:
    """Build custom skill sets for personalities"""

    # Skill point costs by level
    SKILL_COSTS = {
        SkillLevel.NOVICE: 1,
        SkillLevel.INTERMEDIATE: 2,
        SkillLevel.ADVANCED: 3,
        SkillLevel.MASTER: 5
    }

    def __init__(self, total_points: int = 20):
        """
        Initialize with skill points budget

        Default: 20 points allows for:
        - 2 Master skills (10 points)
        - 2 Advanced skills (6 points)
        - 2 Intermediate skills (4 points)

        OR:
        - 1 Master (5)
        - 3 Advanced (9)
        - 3 Intermediate (6)
        """
        self.total_points = total_points
        self.spent_points = 0
        self.skills: Dict[SkillType, Skill] = {}

    def add_skill(self, skill_type: SkillType, level: SkillLevel) -> bool:
        """Add skill if enough points available"""
        cost = self.SKILL_COSTS[level]

        if self.spent_points + cost > self.total_points:
            return False  # Not enough points

        self.skills[skill_type] = Skill(skill_type, level)
        self.spent_points += cost
        return True

    def remove_skill(self, skill_type: SkillType):
        """Remove skill and refund points"""
        if skill_type in self.skills:
            skill = self.skills[skill_type]
            self.spent_points -= self.SKILL_COSTS[skill.level]
            del self.skills[skill_type]

    def upgrade_skill(self, skill_type: SkillType) -> bool:
        """Upgrade skill to next level"""
        if skill_type not in self.skills:
            return False

        current_skill = self.skills[skill_type]
        if current_skill.level == SkillLevel.MASTER:
            return False  # Already max level

        # Calculate upgrade cost
        current_cost = self.SKILL_COSTS[current_skill.level]
        new_level = SkillLevel(current_skill.level.value + 1)
        new_cost = self.SKILL_COSTS[new_level]
        upgrade_cost = new_cost - current_cost

        if self.spent_points + upgrade_cost > self.total_points:
            return False  # Not enough points

        # Upgrade
        current_skill.level = new_level
        self.spent_points += upgrade_cost
        return True

    def get_available_points(self) -> int:
        """Get remaining skill points"""
        return self.total_points - self.spent_points

    def suggest_build(self, focus: str) -> Dict[SkillType, SkillLevel]:
        """
        Suggest skill distribution based on focus

        focus: 'balanced', 'specialist', 'generalist', 'technical', 'creative', 'social'
        """
        suggestions = {}

        if focus == "specialist":
            # Deep expertise in 2-3 areas
            # 2 Master + 2 Advanced = 16 points, 4 remaining
            suggestions = {
                SkillType.CODING: SkillLevel.MASTER,
                SkillType.DEBUGGING: SkillLevel.MASTER,
                SkillType.ARCHITECTURE: SkillLevel.ADVANCED,
                SkillType.CODE_REVIEW: SkillLevel.ADVANCED
            }

        elif focus == "generalist":
            # Broad but shallow knowledge
            # 10 Intermediate skills = 20 points
            suggestions = {
                SkillType.CODING: SkillLevel.INTERMEDIATE,
                SkillType.WRITING: SkillLevel.INTERMEDIATE,
                SkillType.RESEARCH: SkillLevel.INTERMEDIATE,
                SkillType.TEACHING: SkillLevel.INTERMEDIATE,
                SkillType.PROBLEM_SOLVING: SkillLevel.INTERMEDIATE,
                SkillType.COMMUNICATION: SkillLevel.INTERMEDIATE,
                SkillType.PROJECT_MANAGEMENT: SkillLevel.INTERMEDIATE,
                SkillType.DATA_ANALYSIS: SkillLevel.INTERMEDIATE,
                SkillType.CREATIVITY: SkillLevel.INTERMEDIATE,
                SkillType.PRODUCTIVITY: SkillLevel.INTERMEDIATE
            }

        elif focus == "balanced":
            # Mix of deep and broad
            # 1 Master + 3 Advanced + 1 Intermediate = 16 points
            suggestions = {
                SkillType.PROBLEM_SOLVING: SkillLevel.MASTER,
                SkillType.CODING: SkillLevel.ADVANCED,
                SkillType.RESEARCH: SkillLevel.ADVANCED,
                SkillType.TEACHING: SkillLevel.ADVANCED,
                SkillType.EMOTIONAL_INTELLIGENCE: SkillLevel.INTERMEDIATE
            }

        elif focus == "technical":
            # Technical mastery
            suggestions = {
                SkillType.CODING: SkillLevel.MASTER,
                SkillType.DEBUGGING: SkillLevel.ADVANCED,
                SkillType.ARCHITECTURE: SkillLevel.ADVANCED,
                SkillType.DATABASE: SkillLevel.INTERMEDIATE,
                SkillType.SECURITY: SkillLevel.INTERMEDIATE,
                SkillType.TESTING: SkillLevel.INTERMEDIATE
            }

        elif focus == "creative":
            # Creative excellence
            suggestions = {
                SkillType.CREATIVITY: SkillLevel.MASTER,
                SkillType.WRITING: SkillLevel.ADVANCED,
                SkillType.STORYTELLING: SkillLevel.ADVANCED,
                SkillType.DESIGN: SkillLevel.INTERMEDIATE,
                SkillType.ART: SkillLevel.INTERMEDIATE,
                SkillType.MUSIC: SkillLevel.INTERMEDIATE
            }

        elif focus == "social":
            # Social and emotional intelligence
            suggestions = {
                SkillType.EMOTIONAL_INTELLIGENCE: SkillLevel.MASTER,
                SkillType.COUNSELING: SkillLevel.ADVANCED,
                SkillType.COMMUNICATION: SkillLevel.ADVANCED,
                SkillType.TEACHING: SkillLevel.INTERMEDIATE,
                SkillType.MENTORING: SkillLevel.INTERMEDIATE,
                SkillType.NEGOTIATION: SkillLevel.INTERMEDIATE
            }

        return suggestions
```

### 3.2 Skill Builder UI

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Skill Builder                                      [X]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Points: 12/20 available  [Suggest Build ▼]                 │
│                                                               │
│  ═══ SELECTED SKILLS ═══                                     │
│                                                               │
│  ⭐⭐⭐⭐ MASTER (5 points each)                              │
│  • Problem Solving                              [Remove]     │
│                                                               │
│  ⭐⭐⭐ ADVANCED (3 points each)                              │
│  • Coding                                       [Remove]     │
│  • Teaching                                     [Remove]     │
│                                                               │
│  ⭐⭐ INTERMEDIATE (2 points each)                           │
│  (none selected)                                             │
│                                                               │
│  ⭐ NOVICE (1 point each)                                    │
│  (none selected)                                             │
│                                                               │
│  ═══ AVAILABLE SKILLS ═══                                    │
│                                                               │
│  [Technical ▼]  [Creative]  [Social]  [Business]  [All]     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Debugging                      [+Novice] [+Inter...]│    │
│  │ Code Review                    [+Novice] [+Inter...]│    │
│  │ Architecture                   [+Novice] [+Inter...]│    │
│  │ Research                       [+Novice] [+Inter...]│    │
│  │ Data Analysis                  [+Novice] [+Inter...]│    │
│  │ ...                                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  [Clear All]  [Apply Suggestion]  [Save]                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Skill-Based Behavior

### 4.1 Skill Influence on Responses

```python
class SkillAwareResponder:
    """Generate responses that reflect personality's skills"""

    def generate_response(self, personality: PersonalityConfig,
                         user_query: str, context: dict) -> str:
        """Generate response using personality's skills"""

        # Detect query type
        query_skills = self._detect_required_skills(user_query)

        # Check if personality has relevant skills
        personality_skills = personality.skill_set.get_all_skills()
        matching_skills = [s for s in personality_skills if s.type in query_skills]

        if not matching_skills:
            # No relevant skills - general response
            return self._generate_general_response(personality, user_query)

        # Use skills to enhance response
        best_skill = max(matching_skills, key=lambda s: s.level.value)

        # Tailor response based on skill level
        if best_skill.level == SkillLevel.MASTER:
            return self._generate_expert_response(personality, user_query, best_skill)
        elif best_skill.level == SkillLevel.ADVANCED:
            return self._generate_advanced_response(personality, user_query, best_skill)
        elif best_skill.level == SkillLevel.INTERMEDIATE:
            return self._generate_intermediate_response(personality, user_query, best_skill)
        else:
            return self._generate_novice_response(personality, user_query, best_skill)

    def _generate_expert_response(self, personality, query, skill) -> str:
        """Master-level response - comprehensive, confident, nuanced"""
        # Example for CODING skill at MASTER level:
        # - Provides multiple approaches
        # - Discusses trade-offs
        # - References best practices
        # - Anticipates edge cases
        # - Suggests optimizations
        pass

    def _generate_advanced_response(self, personality, query, skill) -> str:
        """Advanced response - detailed, mostly confident, practical"""
        # - Provides solid solution
        # - Mentions some trade-offs
        # - References common practices
        # - Handles typical cases
        pass

    def _generate_intermediate_response(self, personality, query, skill) -> str:
        """Intermediate response - competent, may suggest resources"""
        # - Provides working solution
        # - May suggest further reading
        # - Handles basic cases well
        pass

    def _generate_novice_response(self, personality, query, skill) -> str:
        """Novice response - basic help, suggests expert consultation"""
        # - Provides basic guidance
        # - Suggests consulting expert
        # - Acknowledges limitations
        pass
```

**Example Responses by Skill Level**:

```yaml
user_query: "How do I optimize this database query?"

# Personality WITHOUT database skill:
response: |
  Hmm, database optimization isn't really my specialty. From what I understand,
  you might want to look into indexing and query execution plans, but I'd
  recommend consulting someone with more database expertise for the best approach.

# Personality with INTERMEDIATE database skill:
response: |
  For database optimization, start by checking if your query uses indexes
  properly. Add indexes on columns used in WHERE, JOIN, and ORDER BY clauses.
  You can use EXPLAIN to see the execution plan. Also, avoid SELECT * and
  only query the columns you need. If this is complex, consider consulting
  a database expert for deeper optimization.

# Personality with ADVANCED database skill:
response: |
  Let me help you optimize that query. First, run EXPLAIN ANALYZE to see
  the current execution plan. Look for sequential scans - those are usually
  the bottleneck. Add composite indexes on columns used together in WHERE
  clauses. Consider covering indexes if you're selecting a small column set.
  Also check your join order - put the most restrictive conditions first.
  For large tables, partition by date or key ranges. What database are you
  using? Postgres, MySQL, or something else?

# Personality with MASTER database skill:
response: |
  Excellent question - let's optimize this systematically. First, analyze
  the execution plan with EXPLAIN (ANALYZE, BUFFERS) to identify bottlenecks.
  I see several optimization opportunities:

  1. **Indexing Strategy**: Create a composite B-tree index on (user_id, created_at)
     to support your WHERE clause and ORDER BY efficiently.

  2. **Query Rewrite**: Your subquery can be converted to a lateral join for
     better performance. Consider materialized CTEs if you're on Postgres 12+.

  3. **Statistics**: Ensure table statistics are current - run ANALYZE. Check
     if autovacuum is keeping up.

  4. **Partitioning**: With 50M+ rows, partition by month on created_at. This
     enables partition pruning and dramatically improves query times.

  5. **Connection Pooling**: If this is a hot query, implement pgBouncer to
     reduce connection overhead.

  Trade-offs: Composite indexes speed up reads but slow writes slightly. Measure
  your read/write ratio to determine if it's worth it. What's your query frequency
  and data volume?
```

---

## 5. Skill Progression System

### 5.1 Experience & Leveling

```python
class SkillProgression:
    """Skills can improve over time with use"""

    # Experience needed for each level
    XP_THRESHOLDS = {
        SkillLevel.NOVICE: 0,
        SkillLevel.INTERMEDIATE: 100,
        SkillLevel.ADVANCED: 500,
        SkillLevel.MASTER: 2000
    }

    def gain_experience(self, skill: Skill, xp_amount: int) -> bool:
        """
        Award experience to a skill

        Returns True if skill leveled up
        """
        skill.experience_points += xp_amount

        # Check for level up
        current_threshold = self.XP_THRESHOLDS[skill.level]
        next_level = SkillLevel(skill.level.value + 1) if skill.level.value < 4 else None

        if next_level:
            next_threshold = self.XP_THRESHOLDS[next_level]
            if skill.experience_points >= next_threshold:
                # Level up!
                skill.level = next_level
                return True

        return False

    def calculate_xp_reward(self, task_complexity: str,
                           performance_quality: str) -> int:
        """
        Calculate XP reward for completed task

        task_complexity: 'simple', 'moderate', 'complex', 'expert'
        performance_quality: 'poor', 'good', 'excellent'
        """
        base_xp = {
            'simple': 5,
            'moderate': 15,
            'complex': 40,
            'expert': 100
        }

        multiplier = {
            'poor': 0.5,
            'good': 1.0,
            'excellent': 1.5
        }

        xp = base_xp.get(task_complexity, 10) * multiplier.get(performance_quality, 1.0)
        return int(xp)
```

**Example Progression**:

```python
# Spark starts with INTERMEDIATE coding skill
spark_coding = Skill(SkillType.CODING, SkillLevel.INTERMEDIATE)
spark_coding.experience_points = 100  # Just reached Intermediate

# User asks Spark to help debug a complex issue
# Spark provides excellent help
xp_earned = progression.calculate_xp_reward('complex', 'excellent')  # 60 XP
leveled_up = progression.gain_experience(spark_coding, xp_earned)

# After many such interactions...
# spark_coding.experience_points = 530
# spark_coding.level = SkillLevel.ADVANCED  # Leveled up!

# Notification to user:
"🎉 Spark's Coding skill improved to Advanced! Spark can now handle more complex programming challenges."
```

### 5.2 Skill Unlock System

```python
class SkillUnlocks:
    """Unlock new skills through use and conversation"""

    def check_unlock_conditions(self, personality: PersonalityConfig,
                                conversation_history: List[Message]) -> List[SkillType]:
        """
        Check if personality should unlock new skills

        Conditions for unlock:
        - Discussed topic frequently (10+ conversations)
        - User explicitly taught the skill
        - Related skill reached MASTER level
        """
        unlockable = []

        # Analyze conversation topics
        topic_counts = self._count_topics(conversation_history)

        for skill_type in SkillType:
            if personality.skill_set.has_skill(skill_type):
                continue  # Already has skill

            # Check if frequently discussed
            related_keywords = self._get_skill_keywords(skill_type)
            discussion_count = sum(topic_counts.get(kw, 0) for kw in related_keywords)

            if discussion_count >= 10:
                unlockable.append(skill_type)

        return unlockable

    def unlock_skill(self, personality: PersonalityConfig,
                    skill_type: SkillType, initial_level: SkillLevel = SkillLevel.NOVICE):
        """Unlock a new skill"""
        personality.skill_set.add_skill(skill_type, initial_level)

        # Notification
        return f"🔓 {personality.name} learned {skill_type.value}! Through our conversations, I've picked up some {skill_type.value} knowledge."
```

---

## 6. Skill Showcase & Display

### 6.1 Skill Card UI

```
┌─────────────────────────────────────────┐
│  Buddy's Skills                    [Edit]│
├─────────────────────────────────────────┤
│                                           │
│  ⭐⭐⭐⭐ MASTER SKILLS                    │
│  ┌─────────────────────────────────────┐│
│  │ 💪 Motivation                       ││
│  │ Level: Master (2,450 XP)            ││
│  │ "Your ultimate cheerleader!"        ││
│  │ ▓▓▓▓▓▓▓▓▓▓ 100%                     ││
│  └─────────────────────────────────────┘│
│                                           │
│  ┌─────────────────────────────────────┐│
│  │ 💚 Emotional Intelligence           ││
│  │ Level: Master (2,100 XP)            ││
│  │ "Deeply understands feelings"       ││
│  │ ▓▓▓▓▓▓▓▓▓▓ 100%                     ││
│  └─────────────────────────────────────┘│
│                                           │
│  ⭐⭐⭐ ADVANCED SKILLS                   │
│  • Humor (750 XP) ▓▓▓▓▓▓░░░░ 50%        │
│  • Counseling (620 XP) ▓▓▓▓░░░░░░ 24%   │
│  • Gaming (580 XP) ▓▓▓░░░░░░░ 16%       │
│                                           │
│  ⭐⭐ INTERMEDIATE SKILLS                │
│  • Teaching • Fitness • Productivity     │
│                                           │
│  🎁 HIDDEN TALENTS                       │
│  • Cooking (comfort food specialist!)    │
│  • Music (playlist curator)              │
│                                           │
└─────────────────────────────────────────┘
```

---

## 7. Configuration Storage

**File**: `~/.goose/personalities/buddy_with_skills.json`

```json
{
  "name": "Buddy",
  "base_preset": "buddy",
  "content_rating": "safe",
  "version": "1.0",
  "sliders": { ... },
  "skill_set": {
    "skill_points_available": 0,
    "skills": {
      "motivation": {
        "type": "motivation",
        "level": 4,
        "experience_points": 2450,
        "specializations": ["Pep talks", "Workout motivation"]
      },
      "emotional_intelligence": {
        "type": "emotional_intelligence",
        "level": 4,
        "experience_points": 2100,
        "specializations": []
      },
      "humor": {
        "type": "humor",
        "level": 3,
        "experience_points": 750,
        "specializations": ["Dad jokes", "Situational humor"]
      }
    },
    "primary_skills": ["motivation", "emotional_intelligence", "humor"],
    "hidden_talents": ["cooking", "music"]
  }
}
```

---

## Success Metrics

**Skill System**:
- ✅ 50+ skill types across 6 categories
- ✅ 4 proficiency levels (Novice → Master)
- ✅ Skill point allocation system (20 points)
- ✅ Pre-configured skills for all personality presets
- ✅ Custom skill builder UI

**Skill Progression**:
- ✅ Experience points and leveling system
- ✅ Skill unlock through conversation
- ✅ Performance-based XP rewards
- ✅ Progress tracking and notifications

**Skill Integration**:
- ✅ Skill-aware response generation
- ✅ Expertise level reflected in answers
- ✅ Skill showcase UI
- ✅ Hidden talents system

---

**Give Your Companion Superpowers - Custom Skills for Every Personality!** 🎯✨
