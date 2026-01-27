# Nexus AI - Messaging Package
# Handles inter-agent communication and real-time updates

"""
Core Components:
- MessageBroker: Redis pub/sub for inter-agent messaging
- WebSocketManager: Real-time updates to frontend
- MessageRouter: Route messages between agents
"""

from .message_broker import (
    MessageBroker,
    MessageType,
    AgentMessage,
    message_broker
)

from .websocket_manager import (
    WebSocketManager,
    WebSocketEventType,
    WebSocketEvent,
    ConnectionManager,
    ws_manager,
    emit_task_event_sync,
    emit_agent_progress_sync
)

__all__ = [
    # Message Broker
    "MessageBroker",
    "MessageType",
    "AgentMessage",
    "message_broker",
    
    # WebSocket Manager
    "WebSocketManager",
    "WebSocketEventType",
    "WebSocketEvent",
    "ConnectionManager",
    "ws_manager",
    "emit_task_event_sync",
    "emit_agent_progress_sync"
]
