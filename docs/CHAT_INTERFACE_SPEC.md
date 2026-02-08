# 💬 Conscious - Chat Interface & History System

**Customizable UI + Persistent Cross-Project Memory**

## Vision

The chat interface should feel like *your personal workspace* - fully customizable appearance with persistent memory that follows you across all projects. Every conversation is saved, searchable, and tied to project context for seamless continuity.

## Core Principles

1. **Your Style, Your Way** - Complete control over colors, fonts, sizes, and layout
2. **Never Forget** - Every conversation saved with full context
3. **Cross-Project Intelligence** - Remember discussions from Project A when working on Project B
4. **Privacy First** - All history stored locally, easy to delete or export
5. **Fast & Searchable** - Find any past conversation instantly

---

## 1. Visual Customization System

### 1.1 Theme Engine

**Built-in Themes**:
```yaml
themes:
  - id: dark_default
    name: "Dark (Default)"
    colors:
      background: "#1e1e1e"
      surface: "#2d2d2d"
      primary: "#007acc"
      text: "#d4d4d4"
      text_secondary: "#858585"
      accent: "#4ec9b0"
      error: "#f48771"
      success: "#89d185"
      warning: "#dcdcaa"
      code_bg: "#1e1e1e"
      code_border: "#3e3e3e"

  - id: light_default
    name: "Light"
    colors:
      background: "#ffffff"
      surface: "#f3f3f3"
      primary: "#0066cc"
      text: "#333333"
      text_secondary: "#666666"
      accent: "#00a67e"
      error: "#e53935"
      success: "#43a047"
      warning: "#fb8c00"
      code_bg: "#f5f5f5"
      code_border: "#e0e0e0"

  - id: high_contrast
    name: "High Contrast"
    colors:
      background: "#000000"
      surface: "#1a1a1a"
      primary: "#ffff00"
      text: "#ffffff"
      text_secondary: "#cccccc"
      accent: "#00ffff"
      error: "#ff0000"
      success: "#00ff00"
      warning: "#ffaa00"
      code_bg: "#000000"
      code_border: "#ffffff"

  - id: solarized_dark
    name: "Solarized Dark"
    colors:
      background: "#002b36"
      surface: "#073642"
      primary: "#268bd2"
      text: "#839496"
      text_secondary: "#586e75"
      accent: "#2aa198"
      error: "#dc322f"
      success: "#859900"
      warning: "#b58900"
      code_bg: "#002b36"
      code_border: "#073642"

  - id: monokai
    name: "Monokai"
    colors:
      background: "#272822"
      surface: "#3e3d32"
      primary: "#66d9ef"
      text: "#f8f8f2"
      text_secondary: "#75715e"
      accent: "#a6e22e"
      error: "#f92672"
      success: "#a6e22e"
      warning: "#e6db74"
      code_bg: "#272822"
      code_border: "#49483e"

  - id: custom
    name: "Custom (User-Defined)"
    colors: {}  # User fills in
```

**Custom Theme Creation**:
```python
class ThemeEngine:
    """Manages visual themes with full customization"""

    def create_custom_theme(self, name: str, base_theme: str = "dark_default") -> Theme:
        """Create custom theme starting from a base"""
        base = self.get_theme(base_theme)
        custom = Theme(
            id=f"custom_{name.lower().replace(' ', '_')}",
            name=name,
            colors=base.colors.copy(),  # Start with base colors
            is_custom=True
        )
        return custom

    def update_color(self, theme_id: str, color_key: str, color_value: str):
        """Update a single color in theme"""
        theme = self.get_theme(theme_id)
        if not theme.is_custom:
            raise ValueError("Can only modify custom themes")

        # Validate color format (#RRGGBB or #RRGGBBAA)
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$', color_value):
            raise ValueError(f"Invalid color format: {color_value}")

        theme.colors[color_key] = color_value
        self._save_theme(theme)

    def export_theme(self, theme_id: str) -> str:
        """Export theme as JSON for sharing"""
        theme = self.get_theme(theme_id)
        return json.dumps(theme.to_dict(), indent=2)

    def import_theme(self, theme_json: str) -> Theme:
        """Import theme from JSON"""
        data = json.loads(theme_json)
        theme = Theme.from_dict(data)
        theme.is_custom = True
        self._save_theme(theme)
        return theme
```

### 1.2 Font Customization

**Font Options**:
```python
class FontSettings:
    """Font customization options"""

    AVAILABLE_FAMILIES = {
        "monospace": {
            "Fira Code": "Fira Code, monospace",
            "JetBrains Mono": "JetBrains Mono, monospace",
            "Cascadia Code": "Cascadia Code, monospace",
            "Source Code Pro": "Source Code Pro, monospace",
            "Consolas": "Consolas, monospace",
            "Courier New": "Courier New, monospace",
        },
        "sans_serif": {
            "Inter": "Inter, sans-serif",
            "Roboto": "Roboto, sans-serif",
            "Open Sans": "Open Sans, sans-serif",
            "Segoe UI": "Segoe UI, sans-serif",
            "Arial": "Arial, sans-serif",
            "Helvetica": "Helvetica, sans-serif",
        },
        "serif": {
            "Merriweather": "Merriweather, serif",
            "Georgia": "Georgia, serif",
            "Times New Roman": "Times New Roman, serif",
        }
    }

    def __init__(self):
        self.chat_font_family: str = "Inter"  # Main text
        self.chat_font_size: int = 14  # px (10-24)
        self.chat_font_weight: str = "normal"  # normal, medium, bold
        self.chat_font_style: str = "normal"  # normal, italic
        self.chat_line_height: float = 1.5  # Line spacing (1.0-2.0)

        self.code_font_family: str = "Fira Code"  # Code blocks
        self.code_font_size: int = 13  # px (10-24)
        self.code_font_ligatures: bool = True  # Enable font ligatures

        self.message_spacing: str = "comfortable"  # compact, comfortable, spacious

    def get_css(self) -> str:
        """Generate CSS for current font settings"""
        spacing_map = {
            "compact": "8px",
            "comfortable": "16px",
            "spacious": "24px"
        }

        return f"""
        .chat-message {{
            font-family: {self.AVAILABLE_FAMILIES['sans_serif'][self.chat_font_family]};
            font-size: {self.chat_font_size}px;
            font-weight: {self.chat_font_weight};
            font-style: {self.chat_font_style};
            line-height: {self.chat_line_height};
            margin-bottom: {spacing_map[self.message_spacing]};
        }}

        .code-block, pre, code {{
            font-family: {self.AVAILABLE_FAMILIES['monospace'][self.code_font_family]};
            font-size: {self.code_font_size}px;
            font-variant-ligatures: {'normal' if self.code_font_ligatures else 'none'};
        }}
        """
```

### 1.3 Layout Customization

```python
class LayoutSettings:
    """Chat layout and appearance options"""

    def __init__(self):
        # Message bubble style
        self.message_style: str = "bubbles"  # bubbles, compact, terminal, cards

        # Sidebar
        self.show_sidebar: bool = True
        self.sidebar_width: int = 280  # px (200-400)

        # Chat width
        self.chat_max_width: int = 900  # px (600-1400), 0 = full width

        # Timestamps
        self.show_timestamps: bool = True
        self.timestamp_format: str = "relative"  # relative, absolute, both

        # Code blocks
        self.code_theme: str = "github-dark"  # Syntax highlighting theme
        self.show_line_numbers: bool = True
        self.enable_copy_button: bool = True

        # Markdown rendering
        self.render_markdown: bool = True
        self.render_latex: bool = True

        # Animations
        self.enable_animations: bool = True
        self.animation_speed: str = "normal"  # slow, normal, fast, none
```

### 1.4 User Preferences Storage

**File**: `~/.conscious/ui_preferences.json`

```json
{
  "version": "1.0",
  "theme": {
    "active_theme_id": "dark_default",
    "custom_themes": []
  },
  "fonts": {
    "chat_font_family": "Inter",
    "chat_font_size": 14,
    "chat_font_weight": "normal",
    "chat_font_style": "normal",
    "chat_line_height": 1.5,
    "code_font_family": "Fira Code",
    "code_font_size": 13,
    "code_font_ligatures": true,
    "message_spacing": "comfortable"
  },
  "layout": {
    "message_style": "bubbles",
    "show_sidebar": true,
    "sidebar_width": 280,
    "chat_max_width": 900,
    "show_timestamps": true,
    "timestamp_format": "relative",
    "code_theme": "github-dark",
    "show_line_numbers": true,
    "enable_copy_button": true,
    "render_markdown": true,
    "render_latex": true,
    "enable_animations": true,
    "animation_speed": "normal"
  },
  "accessibility": {
    "high_contrast": false,
    "reduce_motion": false,
    "increase_click_targets": false,
    "screen_reader_optimized": false
  }
}
```

---

## 2. Chat History System

### 2.1 Conversation Storage Architecture

**Database Schema** (SQLite: `~/.conscious/history/conversations.db`):

```sql
-- Conversations table
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,  -- UUID
    project_id TEXT,  -- Project identifier (Git repo, folder path)
    project_name TEXT,
    started_at DATETIME NOT NULL,
    last_message_at DATETIME NOT NULL,
    message_count INTEGER DEFAULT 0,
    tags TEXT,  -- JSON array of tags
    archived BOOLEAN DEFAULT FALSE,
    metadata TEXT  -- JSON object with extra data
);

-- Messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,  -- UUID
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'text',  -- text, code, image, audio
    timestamp DATETIME NOT NULL,
    tokens INTEGER,
    emotion TEXT,  -- Detected emotion (if available)
    metadata TEXT,  -- JSON object
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Project context table (links conversations across projects)
CREATE TABLE project_context (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    context_type TEXT NOT NULL,  -- 'memory', 'decision', 'pattern', 'preference'
    context_key TEXT NOT NULL,
    context_value TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    referenced_conversations TEXT,  -- JSON array of conversation IDs
    UNIQUE(project_id, context_type, context_key)
);

-- Full-text search index
CREATE VIRTUAL TABLE messages_fts USING fts5(
    message_id UNINDEXED,
    conversation_id UNINDEXED,
    role,
    content,
    timestamp UNINDEXED
);

-- Indexes for performance
CREATE INDEX idx_conversations_project ON conversations(project_id);
CREATE INDEX idx_conversations_time ON conversations(last_message_at DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_project_context_project ON project_context(project_id);
```

### 2.2 Conversation Manager

```python
class ConversationHistory:
    """Manages persistent chat history with cross-project memory"""

    def __init__(self, db_path: str = "~/.conscious/history/conversations.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._initialize_schema()

    async def create_conversation(self, project_id: str, project_name: str) -> str:
        """Start a new conversation"""
        conv_id = str(uuid.uuid4())
        now = datetime.utcnow()

        self.conn.execute("""
            INSERT INTO conversations (id, project_id, project_name, started_at, last_message_at)
            VALUES (?, ?, ?, ?, ?)
        """, (conv_id, project_id, project_name, now, now))
        self.conn.commit()

        return conv_id

    async def add_message(self, conversation_id: str, role: str,
                         content: str, emotion: Optional[str] = None,
                         metadata: Optional[dict] = None) -> str:
        """Add a message to conversation"""
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Insert message
        self.conn.execute("""
            INSERT INTO messages (id, conversation_id, role, content, timestamp, emotion, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, conversation_id, role, content, now, emotion,
              json.dumps(metadata) if metadata else None))

        # Update conversation last_message_at
        self.conn.execute("""
            UPDATE conversations
            SET last_message_at = ?, message_count = message_count + 1
            WHERE id = ?
        """, (now, conversation_id))

        # Add to full-text search index
        self.conn.execute("""
            INSERT INTO messages_fts (message_id, conversation_id, role, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (msg_id, conversation_id, role, content, now))

        self.conn.commit()
        return msg_id

    async def get_conversation(self, conversation_id: str,
                               limit: Optional[int] = None) -> List[Message]:
        """Retrieve conversation messages"""
        query = """
            SELECT id, role, content, timestamp, emotion, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor = self.conn.execute(query, (conversation_id,))
        return [Message.from_row(row) for row in cursor.fetchall()]

    async def search_messages(self, query: str, project_id: Optional[str] = None,
                             limit: int = 50) -> List[SearchResult]:
        """Full-text search across all messages"""
        sql = """
            SELECT m.id, m.conversation_id, m.role, m.content, m.timestamp,
                   c.project_name, c.project_id,
                   snippet(messages_fts, 3, '**', '**', '...', 32) as snippet
            FROM messages_fts
            JOIN messages m ON messages_fts.message_id = m.id
            JOIN conversations c ON m.conversation_id = c.id
            WHERE messages_fts MATCH ?
        """

        params = [query]
        if project_id:
            sql += " AND c.project_id = ?"
            params.append(project_id)

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        return [SearchResult.from_row(row) for row in cursor.fetchall()]

    async def get_recent_conversations(self, limit: int = 20,
                                      project_id: Optional[str] = None) -> List[ConversationSummary]:
        """Get recent conversations"""
        sql = """
            SELECT id, project_id, project_name, started_at, last_message_at,
                   message_count, tags, archived
            FROM conversations
            WHERE archived = FALSE
        """

        params = []
        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)

        sql += " ORDER BY last_message_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        return [ConversationSummary.from_row(row) for row in cursor.fetchall()]
```

### 2.3 Cross-Project Memory

```python
class ProjectContextManager:
    """Manages context and memory across projects"""

    async def remember_context(self, project_id: str, context_type: str,
                               key: str, value: str,
                               conversation_id: Optional[str] = None):
        """Store cross-project context"""
        now = datetime.utcnow()

        # Check if context exists
        existing = self.conn.execute("""
            SELECT referenced_conversations FROM project_context
            WHERE project_id = ? AND context_type = ? AND context_key = ?
        """, (project_id, context_type, key)).fetchone()

        if existing:
            # Update existing context
            refs = json.loads(existing[0]) if existing[0] else []
            if conversation_id and conversation_id not in refs:
                refs.append(conversation_id)

            self.conn.execute("""
                UPDATE project_context
                SET context_value = ?, updated_at = ?, referenced_conversations = ?
                WHERE project_id = ? AND context_type = ? AND context_key = ?
            """, (value, now, json.dumps(refs), project_id, context_type, key))
        else:
            # Insert new context
            refs = [conversation_id] if conversation_id else []
            self.conn.execute("""
                INSERT INTO project_context
                (id, project_id, context_type, context_key, context_value,
                 created_at, updated_at, referenced_conversations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), project_id, context_type, key, value,
                  now, now, json.dumps(refs)))

        self.conn.commit()

    async def recall_context(self, project_id: str, context_type: Optional[str] = None) -> List[ProjectContext]:
        """Retrieve project context"""
        sql = """
            SELECT id, project_id, context_type, context_key, context_value,
                   created_at, updated_at, referenced_conversations
            FROM project_context
            WHERE project_id = ?
        """

        params = [project_id]
        if context_type:
            sql += " AND context_type = ?"
            params.append(context_type)

        sql += " ORDER BY updated_at DESC"

        cursor = self.conn.execute(sql, params)
        return [ProjectContext.from_row(row) for row in cursor.fetchall()]

    async def find_related_conversations(self, current_project_id: str,
                                        topic: str) -> List[str]:
        """Find conversations from other projects discussing similar topics"""
        # Search across all projects
        results = await self.history.search_messages(topic, project_id=None, limit=100)

        # Group by project and filter out current project
        related = {}
        for result in results:
            if result.project_id != current_project_id:
                if result.project_id not in related:
                    related[result.project_id] = []
                if result.conversation_id not in related[result.project_id]:
                    related[result.project_id].append(result.conversation_id)

        return related
```

### 2.4 History Browser UI

**Features**:
- Timeline view of all conversations
- Filter by project, date range, tags
- Full-text search with snippet highlights
- Export conversations (JSON, Markdown, HTML)
- Delete or archive conversations
- Tag and organize conversations

```python
class HistoryBrowser:
    """UI for browsing and managing chat history"""

    async def render_timeline(self, filters: Optional[dict] = None) -> str:
        """Render conversation timeline"""
        conversations = await self.history.get_recent_conversations(
            limit=100,
            project_id=filters.get('project_id') if filters else None
        )

        timeline_html = ['<div class="timeline">']

        # Group by date
        grouped = self._group_by_date(conversations)

        for date, convs in grouped.items():
            timeline_html.append(f'<div class="timeline-date">{date}</div>')

            for conv in convs:
                timeline_html.append(f"""
                <div class="timeline-item" data-conversation-id="{conv.id}">
                    <div class="timeline-time">{conv.last_message_at.strftime('%H:%M')}</div>
                    <div class="timeline-content">
                        <div class="timeline-project">{conv.project_name}</div>
                        <div class="timeline-summary">{conv.message_count} messages</div>
                        {self._render_tags(conv.tags)}
                    </div>
                </div>
                """)

        timeline_html.append('</div>')
        return ''.join(timeline_html)

    async def export_conversation(self, conversation_id: str,
                                  format: str = "markdown") -> str:
        """Export conversation in specified format"""
        messages = await self.history.get_conversation(conversation_id)
        conv = await self.history.get_conversation_info(conversation_id)

        if format == "markdown":
            return self._export_markdown(conv, messages)
        elif format == "json":
            return json.dumps({
                'conversation': conv.to_dict(),
                'messages': [m.to_dict() for m in messages]
            }, indent=2)
        elif format == "html":
            return self._export_html(conv, messages)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown(self, conv: ConversationSummary,
                        messages: List[Message]) -> str:
        """Export as Markdown"""
        lines = [
            f"# {conv.project_name}",
            f"",
            f"**Started**: {conv.started_at.strftime('%Y-%m-%d %H:%M')}  ",
            f"**Last Message**: {conv.last_message_at.strftime('%Y-%m-%d %H:%M')}  ",
            f"**Messages**: {conv.message_count}",
            f"",
            "---",
            ""
        ]

        for msg in messages:
            role_icon = "👤" if msg.role == "user" else "🤖"
            timestamp = msg.timestamp.strftime('%H:%M:%S')

            lines.append(f"## {role_icon} {msg.role.capitalize()} - {timestamp}")
            lines.append("")
            lines.append(msg.content)
            lines.append("")

            if msg.emotion:
                lines.append(f"*[Emotion: {msg.emotion}]*")
                lines.append("")

        return '\n'.join(lines)
```

---

## 3. Integration with Mem0

### 3.1 Unified Memory System

```python
class UnifiedMemorySystem:
    """Combines chat history with Mem0 semantic memory"""

    def __init__(self, user_id: str):
        self.history = ConversationHistory()
        self.project_context = ProjectContextManager(self.history)
        self.mem0 = Memory.from_config({
            "version": "v1.1",
            "user_id": user_id,
            "vector_store": {"provider": "qdrant"},
            "graph_store": {"provider": "neo4j"},
        })

    async def process_conversation_turn(self, conversation_id: str,
                                       user_message: str,
                                       assistant_response: str,
                                       emotion: Optional[str] = None):
        """Process a conversation turn with both systems"""
        # 1. Store in chat history
        await self.history.add_message(conversation_id, "user", user_message)
        await self.history.add_message(conversation_id, "assistant",
                                      assistant_response, emotion=emotion)

        # 2. Extract and store memories with Mem0
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ]
        mem_results = await self.mem0.add(messages=messages, user_id=self.user_id)

        # 3. Store important context for cross-project recall
        conv_info = await self.history.get_conversation_info(conversation_id)
        if self._is_important_context(user_message, assistant_response):
            await self.project_context.remember_context(
                project_id=conv_info.project_id,
                context_type="decision",
                key=self._extract_topic(user_message),
                value=assistant_response[:500],  # Store summary
                conversation_id=conversation_id
            )

        return mem_results

    async def get_relevant_history(self, current_project_id: str,
                                   query: str, limit: int = 5) -> List[HistoryContext]:
        """Get relevant history from current AND other projects"""
        results = []

        # 1. Search current project history
        current_results = await self.history.search_messages(
            query, project_id=current_project_id, limit=limit
        )
        results.extend(current_results)

        # 2. Search Mem0 for semantic matches
        mem_results = await self.mem0.search(query=query, limit=limit)

        # 3. Find related conversations from other projects
        related_convs = await self.project_context.find_related_conversations(
            current_project_id, query
        )

        # 4. Combine and rank results
        combined = self._rank_and_combine(current_results, mem_results, related_convs)
        return combined[:limit]
```

---

## 4. Voice Conversation History

### 4.1 Audio Transcript Storage

```python
class VoiceConversationHistory:
    """Extends chat history with voice-specific features"""

    async def add_voice_message(self, conversation_id: str, role: str,
                               transcript: str, audio_path: Optional[str] = None,
                               emotion: Optional[str] = None,
                               prosody: Optional[dict] = None):
        """Add voice message with transcript and metadata"""
        metadata = {
            "content_type": "voice",
            "audio_path": audio_path,
            "prosody": prosody,  # pitch, intensity, speaking_rate
            "voice_detected": True
        }

        msg_id = await self.history.add_message(
            conversation_id=conversation_id,
            role=role,
            content=transcript,
            emotion=emotion,
            metadata=metadata
        )

        return msg_id

    async def get_voice_statistics(self, conversation_id: str) -> dict:
        """Get voice conversation statistics"""
        messages = await self.history.get_conversation(conversation_id)
        voice_messages = [m for m in messages if m.metadata.get('content_type') == 'voice']

        emotions = [m.emotion for m in voice_messages if m.emotion]

        return {
            "total_messages": len(messages),
            "voice_messages": len(voice_messages),
            "text_messages": len(messages) - len(voice_messages),
            "emotions_detected": len(emotions),
            "emotion_distribution": dict(Counter(emotions)),
            "average_message_length": sum(len(m.content) for m in messages) / len(messages)
        }
```

---

## 5. Privacy & Data Management

### 5.1 Privacy Controls

```python
class PrivacyManager:
    """Manages privacy settings for chat history"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load privacy settings"""
        settings_path = self.db_path.parent / "privacy_settings.json"
        if settings_path.exists():
            return json.loads(settings_path.read_text())

        # Defaults
        return {
            "store_history": True,
            "store_voice_audio": False,  # Only store transcripts by default
            "auto_delete_after_days": None,  # None = keep forever
            "exclude_patterns": [],  # Regex patterns to exclude from storage
            "encrypt_sensitive": True,  # Encrypt detected sensitive data
            "share_telemetry": False
        }

    async def delete_conversation(self, conversation_id: str, secure: bool = True):
        """Delete conversation with optional secure deletion"""
        if secure:
            # Overwrite data before deletion (paranoid mode)
            messages = await self.history.get_conversation(conversation_id)
            for msg in messages:
                await self.conn.execute(
                    "UPDATE messages SET content = ? WHERE id = ?",
                    ("X" * len(msg.content), msg.id)
                )
            self.conn.commit()

        # Delete from all tables
        self.conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        self.conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self.conn.execute("DELETE FROM messages_fts WHERE conversation_id = ?", (conversation_id,))
        self.conn.commit()

    async def export_all_data(self, output_path: Path):
        """Export all user data (GDPR compliance)"""
        output_path.mkdir(parents=True, exist_ok=True)

        # Export conversations
        conversations = await self.history.get_recent_conversations(limit=10000)
        for conv in conversations:
            messages = await self.history.get_conversation(conv.id)

            # Export as markdown
            md_content = self.browser._export_markdown(conv, messages)
            md_file = output_path / f"conversation_{conv.id}.md"
            md_file.write_text(md_content)

        # Export project context
        # Export Mem0 data
        # Export preferences

        # Create index
        index = {
            "export_date": datetime.utcnow().isoformat(),
            "total_conversations": len(conversations),
            "files": list(output_path.glob("*"))
        }
        (output_path / "index.json").write_text(json.dumps(index, indent=2))
```

---

## 6. Implementation Plan

### Phase 1: Theme & Font System (Week 1)
- [ ] Implement `ThemeEngine` with 5 built-in themes
- [ ] Create `FontSettings` with font customization
- [ ] Build preferences storage system
- [ ] Create UI for theme/font selection
- [ ] Test on multiple platforms (Windows, macOS, Linux)

### Phase 2: Chat History Database (Week 2)
- [ ] Set up SQLite database schema
- [ ] Implement `ConversationHistory` class
- [ ] Add full-text search with FTS5
- [ ] Create indexes for performance
- [ ] Write tests for all database operations

### Phase 3: Project Context System (Week 3)
- [ ] Implement `ProjectContextManager`
- [ ] Add cross-project memory linking
- [ ] Create context extraction logic
- [ ] Build search and retrieval system
- [ ] Test with multiple projects

### Phase 4: History Browser UI (Week 4)
- [ ] Design timeline view
- [ ] Implement search interface
- [ ] Add export functionality (Markdown, JSON, HTML)
- [ ] Create filtering and tagging system
- [ ] Build archive/delete functionality

### Phase 5: Mem0 Integration (Week 5)
- [ ] Implement `UnifiedMemorySystem`
- [ ] Combine chat history with Mem0 semantic memory
- [ ] Add automatic context extraction
- [ ] Test cross-project recall
- [ ] Optimize query performance

### Phase 6: Voice History (Week 6)
- [ ] Extend history system for voice messages
- [ ] Add audio file management
- [ ] Implement emotion/prosody tracking
- [ ] Create voice statistics
- [ ] Test with Moshi integration

### Phase 7: Privacy & Export (Week 7)
- [ ] Implement `PrivacyManager`
- [ ] Add secure deletion
- [ ] Create data export (GDPR compliance)
- [ ] Build privacy controls UI
- [ ] Write privacy documentation

---

## 7. Configuration Files

### 7.1 Default UI Preferences

**File**: `config/default_ui_preferences.json`

```json
{
  "version": "1.0",
  "theme": {
    "active_theme_id": "dark_default"
  },
  "fonts": {
    "chat_font_family": "Inter",
    "chat_font_size": 14,
    "chat_font_weight": "normal",
    "chat_line_height": 1.5,
    "code_font_family": "Fira Code",
    "code_font_size": 13,
    "message_spacing": "comfortable"
  },
  "layout": {
    "message_style": "bubbles",
    "show_sidebar": true,
    "sidebar_width": 280,
    "chat_max_width": 900,
    "show_timestamps": true,
    "code_theme": "github-dark"
  }
}
```

### 7.2 Privacy Settings

**File**: `~/.conscious/history/privacy_settings.json`

```json
{
  "store_history": true,
  "store_voice_audio": false,
  "auto_delete_after_days": null,
  "encrypt_sensitive": true,
  "share_telemetry": false
}
```

---

## Success Metrics

**UI Customization**:
- ✅ 5+ built-in themes
- ✅ Full font customization (family, size, weight, style)
- ✅ Layout control (spacing, width, style)
- ✅ Export/import custom themes
- ✅ Real-time preview of changes

**Chat History**:
- ✅ Persistent storage (SQLite)
- ✅ Full-text search (<100ms response time)
- ✅ Cross-project memory linking
- ✅ Export in multiple formats
- ✅ Privacy controls (delete, archive, export)

**Performance**:
- ✅ Search results in <100ms for 10,000+ messages
- ✅ Timeline loads <500ms for 1 year of history
- ✅ Theme switching instant (<50ms)
- ✅ Database size <1GB for 100,000 messages

---

## Example User Flows

### Flow 1: Customize Appearance
1. User opens Settings → Appearance
2. Selects "Monokai" theme
3. Changes chat font to "JetBrains Mono" at 15px
4. Sets message spacing to "spacious"
5. Sees live preview of changes
6. Clicks "Save" → preferences stored in `~/.conscious/ui_preferences.json`

### Flow 2: Search Past Conversations
1. User asks: "What did we discuss about authentication last week?"
2. Conscious searches chat history with query "authentication"
3. Finds 3 relevant messages from 5 days ago in different project
4. Displays snippets with context: "You asked about JWT tokens and I explained..."
5. User clicks message → full conversation opens
6. Context from that discussion used to inform current answer

### Flow 3: Cross-Project Recall
1. User starts new project "mobile-app"
2. Asks: "How should I structure the API?"
3. Conscious searches project context and finds:
   - Previous discussion in "web-app" project about REST API design
   - Decision to use /api/v1 pattern
   - Preference for JSON over XML
4. Conscious: "Based on our discussion in the web-app project 2 months ago, you preferred REST with /api/v1 pattern. Should we follow the same approach?"
5. User: "Yes, use that pattern"
6. Context stored for mobile-app project

### Flow 4: Export Conversation
1. User completes project milestone
2. Right-clicks conversation in history
3. Selects "Export → Markdown"
4. Receives `conversation_<id>.md` with full transcript
5. Adds to project documentation
6. Team members can read exact discussion that led to decisions

---

**Your Chat Interface, Your Rules - Fully Customizable with Perfect Memory** 🎨💾
