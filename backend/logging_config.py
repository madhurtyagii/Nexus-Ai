"""
Nexus AI - Logging Configuration
Centralized logging setup with console and file handlers
"""

import logging
import os
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config import get_settings

settings = get_settings()

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
APP_LOG_FILE = os.path.join(LOGS_DIR, "app.log")
WORKER_LOG_FILE = os.path.join(LOGS_DIR, "worker.log")


def setup_logging(
    name: str = "nexus",
    level: int = logging.INFO,
    log_file: str = None
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional specific log file path
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Log format
    if settings.log_format == "json":
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_path = log_file or APP_LOG_FILE
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_app_logger() -> logging.Logger:
    """Get the main application logger."""
    return setup_logging("nexus.app", log_file=APP_LOG_FILE)


def get_worker_logger(worker_id: str = None) -> logging.Logger:
    """Get a worker-specific logger."""
    name = f"nexus.worker.{worker_id}" if worker_id else "nexus.worker"
    return setup_logging(name, log_file=WORKER_LOG_FILE)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger for any module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Configured logger
    """
    logger_name = f"nexus.{name}" if name else "nexus"
    return setup_logging(logger_name, log_file=APP_LOG_FILE)


def read_recent_logs(log_file: str = None, lines: int = 100) -> list:
    """
    Read the most recent log entries.
    
    Args:
        log_file: Path to log file (default: app.log)
        lines: Number of lines to read
        
    Returns:
        List of log lines
    """
    file_path = log_file or APP_LOG_FILE
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    except FileNotFoundError:
        return []
    except Exception as e:
        return [f"Error reading logs: {e}"]


# Global application logger
app_logger = get_app_logger()
