"""
Search Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_manager import DatabaseManager
from database.config import DatabaseConfig
from api.models.schemas import SearchRequest, SearchMode
from api.models.responses import success_response, paginated_response

router = APIRouter()

db_config = DatabaseConfig.get_sqlite_config()
db = DatabaseManager(**db_config)

@router.get("/search/products", summary="Search products")
async def search_products(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    mode: SearchMode = Query(SearchMode.smart, description="Search mode"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Search products by query"""
    try:
        offset = (page - 1) * per_page
        
        if mode == SearchMode.product_id:
            product = db.get_product(q)
            results = [product] if product else []
        elif mode == SearchMode.high_trust:
            all_results = db.search_products(q, limit=1000)
            results = [p for p in all_results if p.get('score_trust_weighted', 0) >= 4.5]
        elif mode == SearchMode.category:
            results = db.get_products_by_category(q, limit=per_page, offset=offset)
        else:  # smart search
            results = db.search_products(q, limit=per_page, offset=offset)
        
        total = len(results)
        return paginated_response(results[offset:offset+per_page], page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/reviews", summary="Search reviews")
async def search_reviews(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Search reviews by text"""
    try:
        # Simplified search - in production, use full-text search
        offset = (page - 1) * per_page
        all_reviews = db.get_all_reviews(limit=1000)
        results = [r for r in all_reviews if q.lower() in str(r.get('review_text', '')).lower()]
        
        total = len(results)
        return paginated_response(results[offset:offset+per_page], page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/autocomplete", summary="Autocomplete suggestions")
async def autocomplete(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50)
):
    """Get autocomplete suggestions"""
    try:
        # Simplified - in production, use proper autocomplete index
        products = db.search_products(q, limit=limit)
        suggestions = [p['product_name'] for p in products]
        
        return success_response(suggestions)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
