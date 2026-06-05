from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, users, hives, inspections, apiaries, dashboard, harvests, photos, queens, reports, tasks, treatments

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
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(treatments.router, prefix="/api/treatments", tags=["Treatments"])
app.include_router(harvests.router, prefix="/api/harvests", tags=["Harvests"])
app.include_router(queens.router, prefix="/api/queens", tags=["Queens"])
app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


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
