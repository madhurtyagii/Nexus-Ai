from datetime import datetime
from typing import Optional, Any, Dict

class NexusBaseException(Exception):
    """Base exception for all Nexus AI related errors."""
    def __init__(
        self, 
        message: str, 
        error_code: str = "SYS_000", 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat() + "Z"

class TaskExecutionError(NexusBaseException):
    """When task execution fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TASK_001", details)

class AgentError(NexusBaseException):
    """When agent encounters error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AGENT_001", details)

class ToolExecutionError(NexusBaseException):
    """When tool fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TOOL_001", details)

class ValidationError(NexusBaseException):
    """Input validation failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VAL_001", details)

class AuthenticationError(NexusBaseException):
    """Auth issues."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_001", details)

class MemoryError(NexusBaseException):
    """ChromaDB/memory issues."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "MEM_001", details)

class FileProcessingError(NexusBaseException):
    """File upload/processing errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FILE_001", details)

class WorkflowError(NexusBaseException):
    """Workflow execution failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "WFLOW_001", details)

class QuotaExceededError(NexusBaseException):
    """Rate limiting, storage limits."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "QUOTA_001", details)

class DatabaseError(NexusBaseException):
    """Database operation failures."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DB_001", details)
