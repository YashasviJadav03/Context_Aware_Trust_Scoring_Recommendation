"""
Product Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_manager import DatabaseManager
from database.config import DatabaseConfig
from api.models.schemas import ProductResponse, ProductCreate, ProductUpdate, PaginationParams
from api.models.responses import success_response, error_response, paginated_response

router = APIRouter()

# Initialize database
db_config = DatabaseConfig.get_sqlite_config()
db = DatabaseManager(**db_config)

# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@router.get("/products", summary="List all products")
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_trust: Optional[float] = Query(None, ge=0, le=5, description="Minimum trust score")
):
    """
    Get a paginated list of products.
    
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 50, max: 100)
    - **category**: Filter by category (optional)
    - **min_trust**: Minimum trust score filter (optional)
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get products
        if category:
            products = db.get_products_by_category(category, limit=per_page, offset=offset)
        else:
            products = db.search_products("", limit=per_page, offset=offset)
        
        # Filter by trust score if specified
        if min_trust is not None:
            products = [p for p in products if p.get('score_trust_weighted', 0) >= min_trust]
        
        # Get total count
        stats = db.get_system_statistics()
        total = stats['total_products']
        
        return paginated_response(products, page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", summary="Get single product")
async def get_product(product_id: str):
    """
    Get detailed information about a specific product.
    
    - **product_id**: Unique product identifier
    """
    try:
        product = db.get_product(product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=error_response("NOT_FOUND", f"Product {product_id} not found")
            )
        
        return success_response(product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/top", summary="Get top products by trust score")
async def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return")
):
    """
    Get top products ranked by trust score.
    
    - **limit**: Number of products to return (default: 10, max: 100)
    """
    try:
        products = db.get_top_products(limit=limit)
        return success_response(products)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/category/{category}", summary="Get products by category")
async def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """
    Get products filtered by category.
    
    - **category**: Product category
    - **page**: Page number
    - **per_page**: Items per page
    """
    try:
        offset = (page - 1) * per_page
        products = db.get_products_by_category(category, limit=per_page, offset=offset)
        
        # Get total count for this category
        all_products = db.get_products_by_category(category, limit=10000)
        total = len(all_products)
        
        return paginated_response(products, page, per_page, total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products", summary="Create new product (Admin only)")
async def create_product(product: ProductCreate):
    """
    Create a new product (Admin only).
    
    - **product**: Product data
    """
    try:
        # Note: In production, add authentication and authorization
        product_data = product.dict()
        product_id = db.insert_product(product_data)
        
        if product_id:
            return success_response({"product_id": product_id, "message": "Product created successfully"})
        else:
            raise HTTPException(status_code=400, detail="Failed to create product")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}", summary="Update product (Admin only)")
async def update_product(product_id: str, product: ProductUpdate):
    """
    Update an existing product (Admin only).
    
    - **product_id**: Product identifier
    - **product**: Updated product data
    """
    try:
        # Note: In production, add authentication and authorization
        # Check if product exists
        existing = db.get_product(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        # Update product
        update_data = {k: v for k, v in product.dict().items() if v is not None}
        success = db.update_product(product_id, update_data)
        
        if success:
            return success_response({"message": "Product updated successfully"})
        else:
            raise HTTPException(status_code=400, detail="Failed to update product")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
