"""
FastAPI Main Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import products, reviews, search, analytics, ml_inference
from api.middleware.logging import LoggingMiddleware
from api.middleware.rate_limit import limiter

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Trust-Based Product Recommendation API",
    description="REST API for trust scoring and product recommendations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS - Allow all origins (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# ============================================================================
# ROUTES
# ============================================================================

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(reviews.router, prefix="/api/v1", tags=["Reviews"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(ml_inference.router, prefix="/api/v1", tags=["ML Inference"])

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Trust-Based Product Recommendation API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs",
        "endpoints": {
            "products": "/api/v1/products",
            "reviews": "/api/v1/reviews",
            "search": "/api/v1/search",
            "analytics": "/api/v1/analytics",
            "ml_inference": "/api/v1/predict"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if os.getenv("DEBUG") else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("🚀 API Server starting...")
    print("📚 Documentation available at /api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    print("👋 API Server shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
