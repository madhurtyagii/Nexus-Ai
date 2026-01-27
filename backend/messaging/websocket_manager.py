"""
Nexus AI - WebSocket Manager
Handles real-time updates to frontend clients
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

from config import get_settings


settings = get_settings()


class WebSocketEventType(Enum):
    """Types of events sent to clients."""
    # Task events
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Agent events
    AGENT_STARTED = "agent_started"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    AGENT_MESSAGE = "agent_message"
    
    # System events
    CONNECTION_ESTABLISHED = "connection_established"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class WebSocketEvent:
    """Represents an event to send to clients."""
    
    def __init__(
        self,
        event_type: WebSocketEventType,
        data: Dict[str, Any],
        task_id: int = None,
        user_id: int = None
    ):
        self.event_type = event_type
        self.data = data
        self.task_id = task_id
        self.user_id = user_id
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "data": self.data,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class ConnectionManager:
    """Manages WebSocket connections for clients."""
    
    def __init__(self):
        # All active connections
        self.active_connections: Dict[int, List[WebSocket]] = {}  # user_id -> connections
        
        # Task subscriptions: task_id -> set of user_ids watching this task
        self.task_subscriptions: Dict[int, Set[int]] = {}
        
        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> bool:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID for this connection
            
        Returns:
            True if connected successfully
        """
        try:
            await websocket.accept()
            
            # Add to active connections
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            
            # Store connection metadata
            self.connection_info[websocket] = {
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "subscribed_tasks": set()
            }
            
            # Send welcome event
            await self.send_personal(
                user_id,
                WebSocketEvent(
                    event_type=WebSocketEventType.CONNECTION_ESTABLISHED,
                    data={"message": "Connected to Nexus AI real-time updates"},
                    user_id=user_id
                )
            )
            
            print(f"🔌 WebSocket connected: user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Handle WebSocket disconnection.
        
        Args:
            websocket: WebSocket to disconnect
            user_id: User ID for this connection
        """
        # Remove from active connections
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove from task subscriptions
        if websocket in self.connection_info:
            subscribed_tasks = self.connection_info[websocket].get("subscribed_tasks", set())
            for task_id in subscribed_tasks:
                if task_id in self.task_subscriptions:
                    self.task_subscriptions[task_id].discard(user_id)
                    if not self.task_subscriptions[task_id]:
                        del self.task_subscriptions[task_id]
            
            del self.connection_info[websocket]
        
        print(f"🔌 WebSocket disconnected: user {user_id}")
    
    def subscribe_to_task(self, websocket: WebSocket, user_id: int, task_id: int):
        """
        Subscribe a connection to task updates.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            task_id: Task ID to subscribe to
        """
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = set()
        self.task_subscriptions[task_id].add(user_id)
        
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscribed_tasks"].add(task_id)
        
        print(f"👁️ User {user_id} subscribed to task {task_id}")
    
    def unsubscribe_from_task(self, user_id: int, task_id: int):
        """Unsubscribe from task updates."""
        if task_id in self.task_subscriptions:
            self.task_subscriptions[task_id].discard(user_id)
    
    async def send_personal(self, user_id: int, event: WebSocketEvent):
        """
        Send an event to a specific user's connections.
        
        Args:
            user_id: Target user ID
            event: WebSocketEvent to send
        """
        if user_id not in self.active_connections:
            return
            
        disconnected = []
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(event.to_json())
            except Exception:
                disconnected.append(websocket)
        
        # Cleanup disconnected
        for ws in disconnected:
            self.disconnect(ws, user_id)
    
    async def send_to_task_subscribers(self, task_id: int, event: WebSocketEvent):
        """
        Send an event to all users subscribed to a task.
        
        Args:
            task_id: Task ID
            event: WebSocketEvent to send
        """
        if task_id not in self.task_subscriptions:
            return
            
        event.task_id = task_id
        
        for user_id in list(self.task_subscriptions[task_id]):
            await self.send_personal(user_id, event)
    
    async def broadcast(self, event: WebSocketEvent):
        """
        Broadcast an event to all connected users.
        
        Args:
            event: WebSocketEvent to broadcast
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_personal(user_id, event)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_user_count(self) -> int:
        """Get number of unique connected users."""
        return len(self.active_connections)


class WebSocketManager:
    """
    Main WebSocket manager for Nexus AI.
    
    Integrates with Redis for distributed event handling.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.connection_manager = ConnectionManager()
        self._redis_client = None
        self._pubsub = None
        self._listener_task = None
        
        # Redis channel for WebSocket events
        self.WS_CHANNEL = "nexus:websocket_events"
    
    async def _get_redis(self) -> aioredis.Redis:
        """Get or create async Redis connection."""
        if self._redis_client is None:
            self._redis_client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True
            )
        return self._redis_client
    
    async def start(self):
        """Start the WebSocket manager and Redis listener."""
        redis = await self._get_redis()
        self._pubsub = redis.pubsub()
        await self._pubsub.subscribe(self.WS_CHANNEL)
        
        # Start listener task
        self._listener_task = asyncio.create_task(self._listen_for_events())
        print("🚀 WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager."""
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.unsubscribe(self.WS_CHANNEL)
        
        if self._redis_client:
            await self._redis_client.close()
            
        print("🛑 WebSocket manager stopped")
    
    async def _listen_for_events(self):
        """Listen for events from Redis and distribute to clients."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    try:
                        event_data = json.loads(message["data"])
                        event = WebSocketEvent(
                            event_type=WebSocketEventType(event_data["event_type"]),
                            data=event_data["data"],
                            task_id=event_data.get("task_id"),
                            user_id=event_data.get("user_id")
                        )
                        
                        # Route event
                        if event.task_id:
                            await self.connection_manager.send_to_task_subscribers(
                                event.task_id, event
                            )
                        elif event.user_id:
                            await self.connection_manager.send_personal(
                                event.user_id, event
                            )
                        else:
                            await self.connection_manager.broadcast(event)
                            
                    except Exception as e:
                        print(f"❌ Event processing error: {e}")
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Redis listener error: {e}")
    
    async def handle_connection(self, websocket: WebSocket, user_id: int):
        """
        Handle a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID from authentication
        """
        connected = await self.connection_manager.connect(websocket, user_id)
        
        if not connected:
            return
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                    await self._handle_client_message(websocket, user_id, message)
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "event_type": "error",
                        "data": {"message": "Invalid JSON"}
                    }))
                    
        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket, user_id)
    
    async def _handle_client_message(
        self,
        websocket: WebSocket,
        user_id: int,
        message: Dict[str, Any]
    ):
        """Handle a message from a WebSocket client."""
        action = message.get("action")
        
        if action == "subscribe_task":
            task_id = message.get("task_id")
            if task_id:
                self.connection_manager.subscribe_to_task(websocket, user_id, task_id)
                await websocket.send_text(json.dumps({
                    "event_type": "subscribed",
                    "data": {"task_id": task_id}
                }))
                
        elif action == "unsubscribe_task":
            task_id = message.get("task_id")
            if task_id:
                self.connection_manager.unsubscribe_from_task(user_id, task_id)
                
        elif action == "ping":
            await websocket.send_text(json.dumps({
                "event_type": "pong",
                "data": {"timestamp": datetime.utcnow().isoformat()}
            }))
    
    async def emit_task_event(
        self,
        event_type: WebSocketEventType,
        task_id: int,
        data: Dict[str, Any]
    ):
        """
        Emit a task-related event via Redis.
        
        Args:
            event_type: Type of event
            task_id: Task ID
            data: Event data
        """
        redis = await self._get_redis()
        
        event = WebSocketEvent(
            event_type=event_type,
            data=data,
            task_id=task_id
        )
        
        await redis.publish(self.WS_CHANNEL, event.to_json())
    
    async def emit_user_event(
        self,
        event_type: WebSocketEventType,
        user_id: int,
        data: Dict[str, Any]
    ):
        """
        Emit a user-specific event via Redis.
        
        Args:
            event_type: Type of event
            user_id: Target user ID
            data: Event data
        """
        redis = await self._get_redis()
        
        event = WebSocketEvent(
            event_type=event_type,
            data=data,
            user_id=user_id
        )
        
        await redis.publish(self.WS_CHANNEL, event.to_json())


# Sync wrapper functions for use in non-async code (like worker.py)
def emit_task_event_sync(
    event_type: WebSocketEventType,
    task_id: int,
    data: Dict[str, Any]
):
    """Synchronous helper to emit task events from worker."""
    import redis
    
    try:
        r = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
        
        event = WebSocketEvent(
            event_type=event_type,
            data=data,
            task_id=task_id
        )
        
        r.publish("nexus:websocket_events", event.to_json())
        
    except Exception as e:
        print(f"❌ Sync emit error: {e}")


def emit_agent_progress_sync(
    task_id: int,
    agent_name: str,
    progress: int,
    status: str,
    message: str = None
):
    """Emit agent progress update from worker."""
    emit_task_event_sync(
        WebSocketEventType.AGENT_PROGRESS,
        task_id,
        {
            "agent_name": agent_name,
            "progress": progress,
            "status": status,
            "message": message
        }
    )


# Global instance
ws_manager = WebSocketManager()
