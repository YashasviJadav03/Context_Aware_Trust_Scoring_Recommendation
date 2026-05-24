"""
Analytics Endpoints
"""

from fastapi import APIRouter, HTTPException
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_manager import DatabaseManager
from database.config import DatabaseConfig
from api.models.responses import success_response

router = APIRouter()

db_config = DatabaseConfig.get_sqlite_config()
db = DatabaseManager(**db_config)

@router.get("/analytics/product/{product_id}", summary="Product statistics")
async def get_product_analytics(product_id: str):
    """Get detailed statistics for a product"""
    try:
        stats = db.get_product_statistics(product_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        return success_response(stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/system", summary="System-wide statistics")
async def get_system_analytics():
    """Get system-wide statistics"""
    try:
        stats = db.get_system_statistics()
        return success_response(stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/trends", summary="Trust score trends")
async def get_trends():
    """Get trust score trends over time"""
    try:
        # Simplified - in production, calculate actual trends
        stats = db.get_system_statistics()
        
        trends = {
            "current_avg_trust": stats['avg_trust_score'],
            "trend": "stable",
            "high_trust_percentage": (stats['high_trust_reviews'] / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0,
            "verified_percentage": (stats['verified_reviews'] / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
        }
        
        return success_response(trends)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
