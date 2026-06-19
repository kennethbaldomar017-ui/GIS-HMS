from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import init_db
from .routers import alerts, auth, barangays, children, dashboard, decisions, imports, logs, maps, measurements, referrals, reports, users

settings = get_settings()
app = FastAPI(title="GIS-Based Child Malnutrition Monitoring System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


for router in [auth.router, users.router, barangays.router, children.router, measurements.router, dashboard.router, maps.router, alerts.router, referrals.router, reports.router, imports.router, logs.router, decisions.router]:
    app.include_router(router)
