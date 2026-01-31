"""Nexus AI - Security Utilities.

This module provides functions for sanitizing input data to protect against 
common web vulnerabilities such as XSS and injection attacks.
"""
import re
from typing import Any, Dict, List, Union

def sanitize_string(text: str) -> str:
    """Removes potentially dangerous characters and patterns from a string.
    
    This function strips HTML tags and escapes common injection symbols 
    to ensure that user-provided text is safe for processing.
    
    Args:
        text: The raw string to be sanitized.
        
    Returns:
        str: The cleaned and sanitized string.
    """
    if not text:
        return text
    
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Limit characters if needed, but for AI prompts we mostly want to block script-like injections
    # Escape common symbols used in injections
    text = text.replace('$', '\\$').replace('{', '\\{').replace('}', '\\}')
    
    return text.strip()

def sanitize_data(data: Union[Dict, List, str]) -> Any:
    """ Recursively sanitize data structures. """
    if isinstance(data, str):
        return sanitize_string(data)
    elif isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    return data
