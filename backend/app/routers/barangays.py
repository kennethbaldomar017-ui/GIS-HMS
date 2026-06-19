from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Barangay, Purok
from ..services.analytics import latest_measurements, summary_for_barangay
from ..utils.who_zscore import calculate_prevalence, classify_risk_level

router = APIRouter(tags=["barangays"])


def feature(obj, props: dict):
    geometry = obj.geometry
    return {"type": "Feature", "geometry": geometry, "properties": {"id": str(obj.id), **props}}


@router.get("/api/barangays")
async def list_barangays(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Barangay).order_by(Barangay.name))).all()
    return [{"id": str(b.id), "name": b.name, "code": b.code, "population_count": b.population_count} for b in rows]


@router.get("/api/barangays/geojson")
async def barangays_geojson(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(Barangay).order_by(Barangay.name))).all()
    return {"type": "FeatureCollection", "features": [feature(b, {"name": b.name, "code": b.code}) for b in rows]}


@router.get("/api/barangays/{barangay_id}")
async def barangay_detail(barangay_id: UUID, db: AsyncSession = Depends(get_db)):
    barangay = await db.get(Barangay, barangay_id)
    if not barangay:
        raise HTTPException(404, "Barangay not found")
    puroks = (await db.scalars(select(Purok).where(Purok.barangay_id == barangay_id).order_by(Purok.name))).all()
    return {"id": str(barangay.id), "name": barangay.name, "code": barangay.code, "puroks": [{"id": str(p.id), "name": p.name, "code": p.code} for p in puroks]}


@router.get("/api/barangays/{barangay_id}/stats")
async def barangay_stats(barangay_id: UUID, db: AsyncSession = Depends(get_db)):
    return await summary_for_barangay(db, barangay_id)


@router.get("/api/puroks")
async def list_puroks(barangay_id: UUID | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Purok).order_by(Purok.name)
    if barangay_id:
        stmt = stmt.where(Purok.barangay_id == barangay_id)
    rows = (await db.scalars(stmt)).all()
    return [{"id": str(p.id), "name": p.name, "code": p.code, "barangay_id": str(p.barangay_id)} for p in rows]


@router.get("/api/puroks/{purok_id}/stats")
async def purok_stats(purok_id: UUID, db: AsyncSession = Depends(get_db)):
    measurements = await latest_measurements(db)
    measurements = [m for m in measurements if m.child and m.child.purok_id == purok_id]
    prevalence = calculate_prevalence(measurements)
    return {"prevalence": prevalence, "risk_level": classify_risk_level(prevalence)}
