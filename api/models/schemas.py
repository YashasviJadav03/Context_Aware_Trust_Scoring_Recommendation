"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class SearchMode(str, Enum):
    smart = "smart"
    product_id = "product_id"
    high_trust = "high_trust"
    category = "category"

# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductBase(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "B001234567",
                "product_name": "Premium Cotton T-Shirt",
                "category": "AMAZON_FASHION",
                "brand": "Nike"
            }
        }

class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass

class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)

class ProductResponse(ProductBase):
    """Schema for product response"""
    avg_rating: float = Field(..., ge=0, le=5)
    review_count: int = Field(..., ge=0)
    score_trust_weighted: float = Field(..., ge=0, le=5)
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "B001234567",
                "product_name": "Premium Cotton T-Shirt",
                "category": "AMAZON_FASHION",
                "brand": "Nike",
                "avg_rating": 4.5,
                "review_count": 150,
                "score_trust_weighted": 4.7,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

# ============================================================================
# REVIEW SCHEMAS
# ============================================================================

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review_text: str = Field(..., min_length=10, max_length=5000, description="Review text (10-5000 characters)")
    verified: bool = Field(default=False, description="Verified purchase")
    helpful_votes: int = Field(default=0, ge=0, description="Number of helpful votes")
    
    @validator('review_text')
    def validate_review_text(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Review text must be at least 10 characters')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "review_text": "Excellent product! Highly recommend for anyone looking for quality.",
                "verified": True,
                "helpful_votes": 10
            }
        }

class ReviewCreate(ReviewBase):
    """Schema for creating a new review"""
    product_id: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[str] = Field(None, max_length=100)

class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, min_length=10, max_length=5000)
    helpful_votes: Optional[int] = Field(None, ge=0)

class ReviewResponse(ReviewBase):
    """Schema for review response"""
    review_id: int
    product_id: str
    user_id: str
    trust_score: float = Field(..., ge=0, le=1)
    predicted_trust_score: float = Field(..., ge=0, le=1)
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "review_id": 12345,
                "product_id": "B001234567",
                "user_id": "USER_123",
                "rating": 5,
                "review_text": "Excellent product! Highly recommend.",
                "verified": True,
                "helpful_votes": 10,
                "trust_score": 0.85,
                "predicted_trust_score": 0.87,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

# ============================================================================
# SEARCH SCHEMAS
# ============================================================================

class SearchRequest(BaseModel):
    """Schema for search request"""
    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    mode: SearchMode = Field(default=SearchMode.smart, description="Search mode")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "cotton shirt",
                "mode": "smart",
                "limit": 20,
                "offset": 0
            }
        }

# ============================================================================
# ML INFERENCE SCHEMAS
# ============================================================================

class TrustScoreRequest(BaseModel):
    """Schema for trust score prediction request"""
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(..., min_length=10, max_length=5000)
    verified: bool = Field(default=False)
    helpful_votes: int = Field(default=0, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "review_text": "This is an excellent product with great quality and fast shipping.",
                "verified": True,
                "helpful_votes": 5
            }
        }

class TrustScoreResponse(BaseModel):
    """Schema for trust score prediction response"""
    trust_score: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    category: str = Field(..., description="Trust category: high, medium, low")
    
    class Config:
        json_schema_extra = {
            "example": {
                "trust_score": 0.85,
                "confidence": 0.92,
                "category": "high"
            }
        }

class BatchTrustScoreRequest(BaseModel):
    """Schema for batch trust score prediction"""
    reviews: List[TrustScoreRequest] = Field(..., max_length=1000, description="Up to 1000 reviews")
    
    @validator('reviews')
    def validate_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 reviews per batch')
        return v

# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=50, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.desc, description="Sort order")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 50,
                "sort_by": "trust_score",
                "sort_order": "desc"
            }
        }

# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class ProductStatistics(BaseModel):
    """Schema for product statistics"""
    product_id: str
    total_reviews: int
    avg_rating: float
    avg_trust_score: float
    high_trust_count: int
    low_trust_count: int
    verified_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "B001234567",
                "total_reviews": 150,
                "avg_rating": 4.5,
                "avg_trust_score": 0.75,
                "high_trust_count": 100,
                "low_trust_count": 10,
                "verified_count": 140
            }
        }

class SystemStatistics(BaseModel):
    """Schema for system-wide statistics"""
    total_products: int
    total_reviews: int
    avg_trust_score: float
    verified_percentage: float
    high_trust_percentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_products": 168281,
                "total_reviews": 10000,
                "avg_trust_score": 0.572,
                "verified_percentage": 93.5,
                "high_trust_percentage": 9.0
            }
        }
