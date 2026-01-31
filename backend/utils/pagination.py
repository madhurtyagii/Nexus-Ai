"""Nexus AI - Pagination Utilities.

This module provides helper functions and schemas for paginating 
API results consistently across different routers.
"""
from typing import List, Any, Dict, TypeVar, Generic, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for a paginated list of items.
    
    Attributes:
        items: The data payload for the current page.
        total: Total count of items available in the database.
        limit: Max number of items requested.
        offset: Starting index of the current page.
        has_more: Boolean indicating if another page is available.
    """

def paginate(query: Query, offset: int = 0, limit: int = 50) -> Dict[str, Any]:
    """Applies limit and offset to a SQLAlchemy query and returns metadata.
    
    Args:
        query: The SQLAlchemy query object to paginate.
        offset: The number of items to skip.
        limit: The maximum number of items to return.
        
    Returns:
        dict: A dictionary containing 'items', 'total', 'limit', 'offset', 
            and 'has_more'.
    """
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }
