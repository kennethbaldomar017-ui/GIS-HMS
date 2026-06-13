from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user
from ..models import Alert, Barangay, Child, Measurement, Purok, User
from ..routers.barangays import feature
from ..services.analytics import latest_measurements
from ..utils.who_zscore import calculate_prevalence, classify_risk_level

router = APIRouter(prefix="/api/maps", tags=["maps"])


@router.get("/heatmap-points")
async def heatmap_points(barangay_id: UUID | None = None, indicator: str = "wasting", db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == "admin":
        barangay_id = user.barangay_id
    rows = await latest_measurements(db, barangay_id)
    points = []
    for m in rows:
        status = {"wasting": m.whz_status.value, "stunting": m.haz_status.value, "underweight": m.waz_status.value}.get(indicator, m.whz_status.value)
        intensity = 1.0 if status.startswith("severely") else 0.6 if status in {"wasted", "stunted", "underweight"} else 0
        points.append({"lat": m.child.latitude, "lng": m.child.longitude, "intensity": intensity})
    return points


@router.get("/barangay-choropleth")
async def barangay_choropleth(db: AsyncSession = Depends(get_db)):
    features = []
    for b in (await db.scalars(select(Barangay).order_by(Barangay.name))).all():
        measurements = await latest_measurements(db, b.id)
        prevalence = calculate_prevalence(measurements)
        alert_count = await db.scalar(select(Alert).join(Child, Child.id == Alert.child_id).where(Child.barangay_id == b.id, Alert.is_resolved.is_(False)).count()) if False else 0
        features.append(feature(b, {"name": b.name, "risk_level": classify_risk_level(prevalence), "prevalence_rate": prevalence["wasting_rate"], "total_children": prevalence["sample_size"], "alert_count": alert_count}))
    return {"type": "FeatureCollection", "features": features}


@router.get("/child-markers")
async def child_markers(barangay_id: UUID | None = None, status_filter: str | None = None, show_sam_only: bool = False, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == "admin":
        barangay_id = user.barangay_id
    rows = await latest_measurements(db, barangay_id)
    out = []
    for m in rows:
        status = m.overall_status.value
        if show_sam_only and status != "severe_acute_malnutrition":
            continue
        if status_filter and status != status_filter:
            continue
        out.append({"id": str(m.child.id), "name": m.child.full_name, "lat": m.child.latitude, "lng": m.child.longitude, "overall_status": status, "age_months": m.age_in_months, "last_measured": m.measurement_date})
    return out


@router.get("/cluster-summary")
async def cluster_summary(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Purok)
    if user.role.value == "admin":
        stmt = stmt.where(Purok.barangay_id == user.barangay_id)
    rows = []
    measurements = await latest_measurements(db, user.barangay_id if user.role.value == "admin" else None)
    for p in (await db.scalars(stmt)).all():
        subset = [m for m in measurements if m.child.purok_id == p.id]
        prevalence = calculate_prevalence(subset)
        rows.append({"purok_id": str(p.id), "name": p.name, "centroid_lat": 9.1833, "centroid_lng": 125.5333, "child_count": len(subset), "malnutrition_count": sum(1 for m in subset if m.overall_status.value != "normal"), "prevalence_rate": prevalence["wasting_rate"], "risk_level": classify_risk_level(prevalence)})
    return rows
