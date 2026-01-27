"""
Nexus AI - Message Broker
Handles inter-agent communication via Redis pub/sub
"""

import json
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from enum import Enum
import threading
import redis

from config import get_settings


settings = get_settings()


class MessageType(Enum):
    """Types of messages that can be sent between agents."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    AGENT_STATUS = "agent_status"
    COLLABORATION_REQUEST = "collaboration_request"
    DATA_SHARE = "data_share"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class AgentMessage:
    """Represents a message between agents."""
    
    def __init__(
        self,
        message_type: MessageType,
        sender: str,
        recipient: str,
        payload: Dict[str, Any],
        correlation_id: str = None,
        priority: int = 1
    ):
        self.message_type = message_type
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.correlation_id = correlation_id or self._generate_id()
        self.priority = priority
        self.timestamp = datetime.utcnow().isoformat()
    
    def _generate_id(self) -> str:
        """Generate a unique correlation ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "priority": self.priority,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary."""
        return cls(
            message_type=MessageType(data["message_type"]),
            sender=data["sender"],
            recipient=data["recipient"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", 1)
        )
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Create message from JSON string."""
        return cls.from_dict(json.loads(json_str))


class MessageBroker:
    """
    Redis-based message broker for inter-agent communication.
    
    Features:
    - Pub/sub for real-time messaging
    - Message persistence in Redis lists
    - Priority queuing
    - Async message handling
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
        self._redis_client = None
        self._pubsub = None
        self._subscribers: Dict[str, List[Callable]] = {}
        self._running = False
        self._listener_thread = None
        
        # Channel prefixes
        self.AGENT_CHANNEL_PREFIX = "nexus:agent:"
        self.BROADCAST_CHANNEL = "nexus:broadcast"
        self.TASK_CHANNEL_PREFIX = "nexus:task:"
        
    def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
        return self._redis_client
    
    def _get_pubsub(self) -> redis.client.PubSub:
        """Get or create Redis pubsub connection."""
        if self._pubsub is None:
            self._pubsub = self._get_redis().pubsub()
        return self._pubsub
    
    def publish(self, channel: str, message: AgentMessage) -> bool:
        """
        Publish a message to a channel.
        
        Args:
            channel: Channel name (agent name or broadcast)
            message: AgentMessage to publish
            
        Returns:
            True if published successfully
        """
        try:
            r = self._get_redis()
            full_channel = f"{self.AGENT_CHANNEL_PREFIX}{channel}"
            
            # Publish to pub/sub
            r.publish(full_channel, message.to_json())
            
            # Also store in list for persistence (last 100 messages)
            list_key = f"{full_channel}:history"
            r.lpush(list_key, message.to_json())
            r.ltrim(list_key, 0, 99)
            
            print(f"📤 Message published: {message.sender} -> {channel}")
            return True
            
        except Exception as e:
            print(f"❌ Publish error: {e}")
            return False
    
    def send_to_agent(
        self,
        sender: str,
        recipient: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: str = None
    ) -> bool:
        """
        Send a message to a specific agent.
        
        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            message_type: Type of message
            payload: Message payload
            correlation_id: Optional correlation ID for request/response tracking
            
        Returns:
            True if sent successfully
        """
        message = AgentMessage(
            message_type=message_type,
            sender=sender,
            recipient=recipient,
            payload=payload,
            correlation_id=correlation_id
        )
        return self.publish(recipient, message)
    
    def broadcast(
        self,
        sender: str,
        message_type: MessageType,
        payload: Dict[str, Any]
    ) -> bool:
        """
        Broadcast a message to all agents.
        
        Args:
            sender: Sender agent name
            message_type: Type of message
            payload: Message payload
            
        Returns:
            True if broadcast successfully
        """
        message = AgentMessage(
            message_type=message_type,
            sender=sender,
            recipient="*",
            payload=payload
        )
        
        try:
            r = self._get_redis()
            r.publish(self.BROADCAST_CHANNEL, message.to_json())
            print(f"📢 Broadcast from {sender}: {message_type.value}")
            return True
        except Exception as e:
            print(f"❌ Broadcast error: {e}")
            return False
    
    def subscribe(self, agent_name: str, callback: Callable[[AgentMessage], None]):
        """
        Subscribe an agent to its channel.
        
        Args:
            agent_name: Agent name to subscribe
            callback: Callback function for received messages
        """
        channel = f"{self.AGENT_CHANNEL_PREFIX}{agent_name}"
        
        if channel not in self._subscribers:
            self._subscribers[channel] = []
            
            # Subscribe to Redis channel
            pubsub = self._get_pubsub()
            pubsub.subscribe(channel)
            pubsub.subscribe(self.BROADCAST_CHANNEL)
            
        self._subscribers[channel].append(callback)
        print(f"✅ Agent '{agent_name}' subscribed to messages")
    
    def unsubscribe(self, agent_name: str):
        """
        Unsubscribe an agent from its channel.
        
        Args:
            agent_name: Agent name to unsubscribe
        """
        channel = f"{self.AGENT_CHANNEL_PREFIX}{agent_name}"
        
        if channel in self._subscribers:
            del self._subscribers[channel]
            pubsub = self._get_pubsub()
            pubsub.unsubscribe(channel)
            print(f"🔇 Agent '{agent_name}' unsubscribed")
    
    def start_listening(self):
        """Start the message listener in a background thread."""
        if self._running:
            return
            
        self._running = True
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()
        print("🎧 Message broker listener started")
    
    def stop_listening(self):
        """Stop the message listener."""
        self._running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=2)
            print("🛑 Message broker listener stopped")
    
    def _listen_loop(self):
        """Background loop for listening to messages."""
        pubsub = self._get_pubsub()
        
        while self._running:
            try:
                message = pubsub.get_message(timeout=1)
                
                if message and message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]
                    
                    # Parse message
                    try:
                        agent_message = AgentMessage.from_json(data)
                        
                        # Notify subscribers
                        if channel in self._subscribers:
                            for callback in self._subscribers[channel]:
                                try:
                                    callback(agent_message)
                                except Exception as e:
                                    print(f"❌ Callback error: {e}")
                                    
                        # Also check broadcast subscribers
                        if channel == self.BROADCAST_CHANNEL:
                            for callbacks in self._subscribers.values():
                                for callback in callbacks:
                                    try:
                                        callback(agent_message)
                                    except Exception as e:
                                        print(f"❌ Broadcast callback error: {e}")
                                        
                    except json.JSONDecodeError:
                        pass  # Skip invalid messages
                        
            except Exception as e:
                print(f"❌ Listen loop error: {e}")
                asyncio.sleep(1)
    
    def get_pending_messages(self, agent_name: str, limit: int = 10) -> List[AgentMessage]:
        """
        Get pending messages for an agent from history.
        
        Args:
            agent_name: Agent name
            limit: Max messages to retrieve
            
        Returns:
            List of pending messages
        """
        try:
            r = self._get_redis()
            list_key = f"{self.AGENT_CHANNEL_PREFIX}{agent_name}:history"
            
            messages = []
            raw_messages = r.lrange(list_key, 0, limit - 1)
            
            for raw in raw_messages:
                try:
                    messages.append(AgentMessage.from_json(raw))
                except:
                    pass
                    
            return messages
            
        except Exception as e:
            print(f"❌ Get pending messages error: {e}")
            return []
    
    def clear_agent_history(self, agent_name: str):
        """Clear message history for an agent."""
        try:
            r = self._get_redis()
            list_key = f"{self.AGENT_CHANNEL_PREFIX}{agent_name}:history"
            r.delete(list_key)
        except Exception as e:
            print(f"❌ Clear history error: {e}")
    
    def request_collaboration(
        self,
        requester: str,
        collaborators: List[str],
        task_description: str,
        task_data: Dict[str, Any] = None
    ) -> str:
        """
        Request collaboration from multiple agents.
        
        Args:
            requester: Requesting agent name
            collaborators: List of agent names to collaborate
            task_description: Description of the collaborative task
            task_data: Optional data to share
            
        Returns:
            Correlation ID for tracking responses
        """
        import uuid
        correlation_id = str(uuid.uuid4())[:8]
        
        for agent in collaborators:
            self.send_to_agent(
                sender=requester,
                recipient=agent,
                message_type=MessageType.COLLABORATION_REQUEST,
                payload={
                    "task_description": task_description,
                    "data": task_data or {},
                    "collaborators": collaborators
                },
                correlation_id=correlation_id
            )
        
        return correlation_id
    
    def send_data_share(
        self,
        sender: str,
        recipient: str,
        data_type: str,
        data: Any,
        correlation_id: str = None
    ) -> bool:
        """
        Share data between agents.
        
        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            data_type: Type of data being shared
            data: The data to share
            correlation_id: Optional correlation ID
            
        Returns:
            True if sent successfully
        """
        return self.send_to_agent(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.DATA_SHARE,
            payload={
                "data_type": data_type,
                "data": data
            },
            correlation_id=correlation_id
        )


# Global instance
message_broker = MessageBroker()
