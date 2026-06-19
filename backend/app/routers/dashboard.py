from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user, require_super_admin
from ..models import Barangay, Child, Measurement, User
from ..services.analytics import latest_measurements, summary_for_barangay
from ..utils.who_zscore import calculate_prevalence, classify_risk_level

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def summary(barangay_id: UUID | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == "admin":
        barangay_id = user.barangay_id
    return await summary_for_barangay(db, barangay_id)


@router.get("/prevalence-trend")
async def prevalence_trend(barangay_id: UUID | None = None, months: int = 12, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == "admin":
        barangay_id = user.barangay_id
    rows = await latest_measurements(db, barangay_id)
    today = date.today()
    return [{"month": f"{((today.month - i - 1) % 12) + 1:02d}", "wasting": calculate_prevalence(rows)["wasting_rate"], "stunting": calculate_prevalence(rows)["stunting_rate"], "underweight": calculate_prevalence(rows)["underweight_rate"]} for i in reversed(range(months))]


@router.get("/age-distribution")
async def age_distribution(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Child).where(Child.is_active.is_(True))
    if user.role.value == "admin":
        stmt = stmt.where(Child.barangay_id == user.barangay_id)
    buckets = {"0-6m": 0, "6-12m": 0, "12-24m": 0, "24-36m": 0, "36-48m": 0, "48-60m": 0}
    for child in (await db.scalars(stmt)).all():
        months = (date.today().year - child.birth_date.year) * 12 + date.today().month - child.birth_date.month
        key = "0-6m" if months < 6 else "6-12m" if months < 12 else "12-24m" if months < 24 else "24-36m" if months < 36 else "36-48m" if months < 48 else "48-60m"
        buckets[key] += 1
    return [{"bracket": k, "count": v} for k, v in buckets.items()]


@router.get("/barangay-comparison")
async def barangay_comparison(db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    rows = []
    for barangay in (await db.scalars(select(Barangay).order_by(Barangay.name))).all():
        measurements = await latest_measurements(db, barangay.id)
        prevalence = calculate_prevalence(measurements)
        rows.append({"barangay_id": str(barangay.id), "barangay": barangay.name, **prevalence, "risk_level": classify_risk_level(prevalence)})
    return sorted(rows, key=lambda x: x["wasting_rate"], reverse=True)


@router.get("/sex-breakdown")
async def sex_breakdown(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await latest_measurements(db, user.barangay_id if user.role.value == "admin" else None)
    data = {"male": {"wasting": 0, "stunting": 0, "underweight": 0}, "female": {"wasting": 0, "stunting": 0, "underweight": 0}}
    for m in rows:
        sex = m.child.sex.value
        data[sex]["wasting"] += int(m.whz_status.value in {"wasted", "severely_wasted"})
        data[sex]["stunting"] += int(m.haz_status.value in {"stunted", "severely_stunted"})
        data[sex]["underweight"] += int(m.waz_status.value in {"underweight", "severely_underweight"})
    return data
