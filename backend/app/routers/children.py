from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..middleware.rbac import assert_barangay_scope, get_current_user, scoped_barangay_filter
from ..models import Alert, Child, Measurement, User
from ..models.entities import Sex
from ..schemas.common import ChildCreate
from ..services.audit import log_activity

router = APIRouter(prefix="/api/children", tags=["children"])


def age_months(birth_date: date, on_date: date | None = None) -> int:
    on_date = on_date or date.today()
    return max(0, (on_date.year - birth_date.year) * 12 + on_date.month - birth_date.month - (1 if on_date.day < birth_date.day else 0))


def child_payload(child: Child) -> dict:
    latest = sorted(child.measurements, key=lambda m: m.measurement_date, reverse=True)[0] if child.measurements else None
    return {
        "id": str(child.id),
        "full_name": child.full_name,
        "birth_date": child.birth_date,
        "age_months": age_months(child.birth_date),
        "sex": child.sex.value,
        "guardian_name": child.guardian_name,
        "contact_number": child.contact_number,
        "purok_id": str(child.purok_id),
        "barangay_id": str(child.barangay_id),
        "latitude": child.latitude,
        "longitude": child.longitude,
        "is_active": child.is_active,
        "latest_measurement": None if not latest else {"id": str(latest.id), "date": latest.measurement_date, "overall_status": latest.overall_status.value, "waz": latest.waz, "haz": latest.haz, "whz": latest.whz},
    }


@router.get("")
async def list_children(search: str | None = None, barangay_id: UUID | None = None, purok_id: UUID | None = None, sex: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    assert_barangay_scope(user, barangay_id)
    stmt = select(Child).options(selectinload(Child.measurements)).where(Child.is_active.is_(True)).order_by(Child.full_name)
    stmt = scoped_barangay_filter(stmt, Child, user)
    if barangay_id:
        stmt = stmt.where(Child.barangay_id == barangay_id)
    if purok_id:
        stmt = stmt.where(Child.purok_id == purok_id)
    if sex:
        stmt = stmt.where(Child.sex == Sex(sex))
    if search:
        stmt = stmt.where(or_(Child.full_name.ilike(f"%{search}%"), Child.guardian_name.ilike(f"%{search}%")))
    return [child_payload(c) for c in (await db.scalars(stmt)).all()]


@router.post("")
async def create_child(body: ChildCreate, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    assert_barangay_scope(user, body.barangay_id)
    child = Child(**body.model_dump())
    db.add(child)
    await db.flush()
    await log_activity(db, user.id, "CREATE_CHILD", "children", str(child.id), body.model_dump(mode="json"), request.client.host if request.client else None)
    await db.commit()
    await db.refresh(child)
    return child_payload(child)


@router.get("/{child_id}")
async def get_child(child_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    child = await db.scalar(select(Child).options(selectinload(Child.measurements)).where(Child.id == child_id))
    if not child:
        raise HTTPException(404, "Child not found")
    assert_barangay_scope(user, child.barangay_id)
    alerts = (await db.scalars(select(Alert).where(Alert.child_id == child_id, Alert.is_resolved.is_(False)))).all()
    payload = child_payload(child)
    payload["measurements"] = [m for m in sorted(child.measurements, key=lambda x: x.measurement_date, reverse=True)]
    payload["active_alerts"] = [{"id": str(a.id), "severity": a.severity.value, "message": a.message} for a in alerts]
    return payload


@router.put("/{child_id}")
async def update_child(child_id: UUID, body: ChildCreate, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    child = await db.get(Child, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    assert_barangay_scope(user, child.barangay_id)
    for key, value in body.model_dump().items():
        setattr(child, key, value)
    await log_activity(db, user.id, "UPDATE_CHILD", "children", str(child.id), {}, request.client.host if request.client else None)
    await db.commit()
    await db.refresh(child)
    return child_payload(child)


@router.delete("/{child_id}")
async def delete_child(child_id: UUID, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    child = await db.get(Child, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    assert_barangay_scope(user, child.barangay_id)
    child.is_active = False
    await log_activity(db, user.id, "DELETE_CHILD", "children", str(child.id), {}, request.client.host if request.client else None)
    await db.commit()
    return {"ok": True}


@router.get("/{child_id}/measurements")
async def child_measurements(child_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    child = await db.get(Child, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    assert_barangay_scope(user, child.barangay_id)
    return list((await db.scalars(select(Measurement).where(Measurement.child_id == child_id).order_by(Measurement.measurement_date.desc()))).all())


@router.get("/{child_id}/growth-chart-data")
async def growth_chart_data(child_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await child_measurements(child_id, db, user)
    return {"measurements": rows, "reference_lines": [{"age_months": i, "sd3neg": -3, "sd2neg": -2, "sd0": 0, "sd2pos": 2, "sd3pos": 3} for i in range(0, 61)]}
