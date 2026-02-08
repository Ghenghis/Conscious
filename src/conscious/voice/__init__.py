"""Voice engine package — Moshi integration, agentic client, and audio streaming.

Components:
    MoshiEngine         — Direct model wrapper (in-process inference)
    MoshiAgent          — Autonomous WebSocket client to Moshi server
    MoshiServerManager  — Server lifecycle management (start/stop/health/restart)
    MoshiAgentAPI       — HTTP/WS API for Super-Goose integration
    AudioStream         — System audio I/O via sounddevice (legacy)
"""

from .moshi_agent import MoshiAgent, AgentConfig, AgentState
from .server_manager import MoshiServerManager, ServerManagerConfig, ServerStatus
from .agent_api import MoshiAgentAPI

__all__ = [
    "MoshiAgent", "AgentConfig", "AgentState",
    "MoshiServerManager", "ServerManagerConfig", "ServerStatus",
    "MoshiAgentAPI",
]
