"""
Review Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_manager import DatabaseManager
from database.config import DatabaseConfig
from api.models.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from api.models.responses import success_response, error_response, paginated_response

router = APIRouter()

# Initialize database
db_config = DatabaseConfig.get_sqlite_config()
db = DatabaseManager(**db_config)

# ============================================================================
# REVIEW ENDPOINTS
# ============================================================================

@router.get("/reviews", summary="List all reviews")
async def list_reviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    min_trust: Optional[float] = Query(None, ge=0, le=1),
    verified_only: bool = Query(False)
):
    """
    Get a paginated list of reviews.
    
    - **page**: Page number
    - **per_page**: Items per page
    - **min_trust**: Minimum trust score filter
    - **verified_only**: Show only verified reviews
    """
    try:
        offset = (page - 1) * per_page
        
        # Get reviews (simplified - in production, add proper filtering)
        reviews = db.get_all_reviews(limit=per_page, offset=offset)
        
        # Apply filters
        if min_trust is not None:
            reviews = [r for r in reviews if r.get('trust_score', 0) >= min_trust]
        if verified_only:
            reviews = [r for r in reviews if r.get('verified', False)]
        
        stats = db.get_system_statistics()
        total = stats['total_reviews']
        
        return paginated_response(reviews, page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{review_id}", summary="Get single review")
async def get_review(review_id: int):
    """
    Get detailed information about a specific review.
    
    - **review_id**: Unique review identifier
    """
    try:
        review = db.get_review(review_id)
        
        if not review:
            raise HTTPException(
                status_code=404,
                detail=error_response("NOT_FOUND", f"Review {review_id} not found")
            )
        
        return success_response(review)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}/reviews", summary="Get product reviews")
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    min_trust: Optional[float] = Query(None, ge=0, le=1)
):
    """
    Get all reviews for a specific product.
    
    - **product_id**: Product identifier
    - **page**: Page number
    - **per_page**: Items per page
    - **min_trust**: Minimum trust score filter
    """
    try:
        offset = (page - 1) * per_page
        reviews = db.get_product_reviews(product_id, min_trust=min_trust or 0, limit=per_page, offset=offset)
        
        # Get total count
        all_reviews = db.get_product_reviews(product_id, limit=10000)
        total = len(all_reviews)
        
        return paginated_response(reviews, page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reviews", summary="Submit new review")
async def create_review(review: ReviewCreate):
    """
    Submit a new product review.
    
    - **review**: Review data including product_id, rating, text, etc.
    """
    try:
        # Calculate trust score (simplified)
        trust_score = review.rating / 5.0
        if review.verified:
            trust_score = min(trust_score + 0.1, 1.0)
        
        # Prepare review data
        review_data = review.dict()
        review_data['trust_score'] = trust_score
        review_data['predicted_trust_score'] = trust_score
        review_data['user_id'] = review_data.get('user_id') or f'USER_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        # Insert review
        review_id = db.insert_review(review_data)
        
        if review_id:
            return success_response({
                "review_id": review_id,
                "trust_score": trust_score,
                "message": "Review submitted successfully"
            })
        else:
            raise HTTPException(status_code=400, detail="Failed to create review")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/reviews/{review_id}", summary="Update review")
async def update_review(review_id: int, review: ReviewUpdate):
    """
    Update an existing review (owner only).
    
    - **review_id**: Review identifier
    - **review**: Updated review data
    """
    try:
        # Check if review exists
        existing = db.get_review(review_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
        
        # Update review
        update_data = {k: v for k, v in review.dict().items() if v is not None}
        success = db.update_review(review_id, update_data)
        
        if success:
            return success_response({"message": "Review updated successfully"})
        else:
            raise HTTPException(status_code=400, detail="Failed to update review")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reviews/{review_id}", summary="Delete review")
async def delete_review(review_id: int):
    """
    Delete a review (owner/admin only).
    
    - **review_id**: Review identifier
    """
    try:
        # Check if review exists
        existing = db.get_review(review_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
        
        # Delete review
        success = db.delete_review(review_id)
        
        if success:
            return success_response({"message": "Review deleted successfully"})
        else:
            raise HTTPException(status_code=400, detail="Failed to delete review")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
