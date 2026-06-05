from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, users, hives, inspections, apiaries

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(apiaries.router, prefix="/api/apiaries", tags=["Apiaries"])
app.include_router(hives.router, prefix="/api/hives", tags=["Hives"])
app.include_router(inspections.router, prefix="/api/hives/{hive_id}/inspections", tags=["Inspections"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
