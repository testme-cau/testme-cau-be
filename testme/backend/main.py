"""
FastAPI application entry point
"""
import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up test.me API...")
    
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': settings.firebase_storage_bucket
            })
            logger.info('Firebase Admin SDK initialized successfully')
        except Exception as e:
            logger.warning(f'Firebase initialization failed: {e}')
            logger.warning('Some features may not work without Firebase credentials')
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down test.me API...")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description="AI-powered exam generation and grading platform",
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files (for admin interface)
    try:
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    
    # Register routers
    from app.routes import main as main_routes
    from app.routes import subject as subject_routes
    from app.routes import pdf as pdf_routes
    from app.routes import exam as exam_routes
    # from app.routes import admin as admin_routes
    
    app.include_router(main_routes.router)
    app.include_router(subject_routes.router, prefix="/api/subjects")
    app.include_router(pdf_routes.router, prefix="/api")
    app.include_router(exam_routes.router, prefix="/api")
    # app.include_router(admin_routes.router, prefix="/admin", tags=["admin"])
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

