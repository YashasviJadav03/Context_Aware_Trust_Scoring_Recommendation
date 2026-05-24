"""
Standardized API Response Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

# ============================================================================
# BASE RESPONSE
# ============================================================================

class APIResponse(BaseModel):
    """Base API response model"""
    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "meta": {"page": 1, "per_page": 50},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

# ============================================================================
# PAGINATED RESPONSE
# ============================================================================

class PaginatedResponse(APIResponse):
    """Paginated API response"""
    meta: Dict[str, Any] = Field(..., description="Pagination metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [{"id": 1}, {"id": 2}],
                "meta": {
                    "page": 1,
                    "per_page": 50,
                    "total": 168281,
                    "total_pages": 3366
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

# ============================================================================
# ERROR RESPONSE
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "rating", "error": "Must be between 1 and 5"}
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False, description="Always false for errors")
    error: ErrorDetail = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Product not found",
                    "details": None
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def success_response(
    data: Any,
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a success response"""
    return {
        "success": True,
        "data": data,
        "meta": meta,
        "timestamp": datetime.utcnow().isoformat()
    }

def error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """Create an error response"""
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def paginated_response(
    data: List[Any],
    page: int,
    per_page: int,
    total: int
) -> Dict[str, Any]:
    """Create a paginated response"""
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "success": True,
        "data": data,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "timestamp": datetime.utcnow().isoformat()
    }
