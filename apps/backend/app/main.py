from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import apiaries, auth, batches, cashbook, content, dashboard, feed_calculator, feedings, google_calendar, harvests, hive_selection, hives, honey_price_calculator, honeybook, inspection_criteria, inspections, inventory, map as map_api, office, photos, push_notifications, queens, reports, sales, tasks, traceability, treatments, users, varroa_checks, breeding_selection, zuchtreihen
from app.services.scheduler import start_scheduler, stop_scheduler

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
app.include_router(inspection_criteria.router, prefix="/api/inspection-criteria", tags=["Inspection Criteria"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(google_calendar.router, prefix="/api/google-calendar", tags=["Google Calendar"])
app.include_router(treatments.router, prefix="/api/treatments", tags=["Treatments"])
app.include_router(harvests.router, prefix="/api/harvests", tags=["Harvests"])
app.include_router(batches.router, prefix="/api/batches", tags=["Batches"])
app.include_router(feedings.router, prefix="/api/feedings", tags=["Feedings"])
app.include_router(inventory.articles_router, prefix="/api/articles", tags=["Articles"])
app.include_router(inventory.items_router, prefix="/api/inventory-items", tags=["Inventory"])
app.include_router(queens.router, prefix="/api/queens", tags=["Queens"])
app.include_router(varroa_checks.router, prefix="/api/varroa-checks", tags=["Varroa Checks"])
app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(content.admin_router, prefix="/api/admin/content", tags=["Content Admin"])
app.include_router(cashbook.router, prefix="/api/cashbook", tags=["Cashbook"])
app.include_router(office.router, prefix="/api/office", tags=["Office"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(honeybook.router, prefix="/api/honeybook", tags=["Honeybook"])
app.include_router(traceability.router, prefix="/api/traceability", tags=["Traceability"])
app.include_router(zuchtreihen.router, prefix="/api/zuchtreihen", tags=["Zuchtreihen"])
app.include_router(breeding_selection.router, prefix="/api/breeding-selection", tags=["Zucht-Selektion"])
app.include_router(hive_selection.router, prefix="/api/hive-selection", tags=["Bienenvolk-Selektion"])
app.include_router(push_notifications.router, prefix="/api/push", tags=["Push Notifications"])
app.include_router(map_api.router, prefix="/api/map", tags=["Map"])
app.include_router(feed_calculator.router, prefix="/api/feed-calculator", tags=["Futtermengen-Rechner"])
app.include_router(honey_price_calculator.router, prefix="/api/honey-price-calculator", tags=["Honigpreis-Rechner"])


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


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
