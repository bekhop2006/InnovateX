"""
Main FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import create_tables

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="InnovateX Backend API",
    version="1.0.0",
    description="Flexible backend API built with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads/avatars", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting InnovateX Backend...")
    
    # Create database tables
    create_tables()
    print("✅ Database tables created/verified")
    
    print("✅ Server is ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down InnovateX Backend...")


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "InnovateX Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": os.getenv("APP_ENV", "development")
    }


# Import and include routers
try:
    from services.auth.router import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
except ImportError:
    print("⚠️  Auth router not found")

try:
    from services.account.router import router as account_router
    app.include_router(account_router, prefix="/api", tags=["Accounts"])
except ImportError:
    print("⚠️  Account router not found")

try:
    from services.transaction.router import router as transaction_router
    app.include_router(transaction_router, prefix="/api", tags=["Transactions"])
except ImportError:
    print("⚠️  Transaction router not found")

try:
    from services.product.router import router as product_router
    app.include_router(product_router, prefix="/api", tags=["Products"])
except ImportError:
    print("⚠️  Product router not found")

try:
    from services.cart.router import router as cart_router
    app.include_router(cart_router, prefix="/api", tags=["Cart"])
except ImportError:
    print("⚠️  Cart router not found")

try:
    from services.document_inspector.router import router as document_inspector_router
    app.include_router(document_inspector_router, prefix="/api/document-inspector", tags=["Document Inspector"])
except ImportError:
    print("⚠️  Document Inspector router not found")

try:
    from services.document_inspector.process_router import router as process_document_router
    app.include_router(process_document_router, prefix="/api", tags=["Document Processing"])
except ImportError:
    print("⚠️  Process Document router not found")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("APP_ENV") == "development"
    )

