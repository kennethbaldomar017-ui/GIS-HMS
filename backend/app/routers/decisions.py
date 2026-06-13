from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user
from ..models import Child, Measurement, Referral, User
from ..services.analytics import latest_measurements
from ..utils.who_zscore import calculate_prevalence

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.get("/recommendations")
async def recommendations(barangay_id: UUID | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role.value == "admin":
        barangay_id = user.barangay_id
    prevalence = calculate_prevalence(await latest_measurements(db, barangay_id))
    recs = []
    if prevalence["wasting_rate"] >= 15:
        recs.append({"title": "Activate Therapeutic Feeding Program", "description": "Wasting prevalence has crossed the emergency threshold.", "priority": "critical", "evidence": prevalence})
    if prevalence["stunting_rate"] >= 40:
        recs.append({"title": "Nutrition-Sensitive Agriculture intervention", "description": "Stunting prevalence indicates chronic nutrition stress.", "priority": "high", "evidence": prevalence})
    if not recs:
        recs.append({"title": "Maintain routine monitoring", "description": "Current prevalence does not trigger emergency thresholds.", "priority": "routine", "evidence": prevalence})
    return recs


@router.get("/high-risk-children")
async def high_risk_children(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await latest_measurements(db, user.barangay_id if user.role.value == "admin" else None)
    return [{"child_id": str(m.child_id), "name": m.child.full_name, "overall_status": m.overall_status.value, "whz": m.whz, "waz": m.waz, "haz": m.haz} for m in rows if m.overall_status.value != "normal"]
