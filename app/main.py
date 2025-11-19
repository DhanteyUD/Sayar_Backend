from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .core.database import engine, get_db
from .models import user, merchant, product, order, payment, shipping
from .api.v1.api import api_router  # Import the API router

# Create tables
user.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sayar WhatsApp Commerce API",
    description="A complete WhatsApp commerce solution for merchants",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Sayar WhatsApp Commerce API",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connection and API status
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )


@app.get("/api/status")
async def api_status():
    """
    API status and information endpoint
    """
    return {
        "service": "Sayar WhatsApp Commerce API",
        "status": "operational",
        "version": "1.0.0",
        "supported_endpoints": [
            "/api/v1/auth/*",
            "/api/v1/merchants/*",
            "/api/v1/products/*",
            "/api/v1/orders/*",
            "/api/v1/payments/*",
            "/api/v1/admin/*"
        ]
    }
