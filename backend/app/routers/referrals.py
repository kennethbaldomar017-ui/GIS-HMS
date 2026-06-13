from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user
from ..models import Child, Referral, User
from ..models.entities import Priority, ReferralStatus
from ..schemas.common import ReferralCreate
from ..services.audit import log_activity

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


@router.get("")
async def list_referrals(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Referral).join(Child, Child.id == Referral.child_id).order_by(Referral.referred_at.desc())
    if user.role.value == "admin":
        stmt = stmt.where(Child.barangay_id == user.barangay_id)
    return list((await db.scalars(stmt)).all())


@router.post("")
async def create_referral(body: ReferralCreate, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    referral = Referral(child_id=body.child_id, referred_by=user.id, referred_to=body.referred_to, reason=body.reason, priority=Priority(body.priority), notes=body.notes)
    db.add(referral)
    await db.flush()
    await log_activity(db, user.id, "CREATE_REFERRAL", "referrals", str(referral.id), {}, request.client.host if request.client else None)
    await db.commit()
    await db.refresh(referral)
    return referral


@router.get("/pending-count")
async def pending_count(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await list_referrals(db, user)
    return {"count": sum(1 for r in rows if r.status.value == "pending")}


@router.get("/{referral_id}")
async def get_referral(referral_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await db.get(Referral, referral_id)


@router.put("/{referral_id}/status")
async def update_status(referral_id: UUID, status: str, notes: str | None = None, request: Request = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    referral = await db.get(Referral, referral_id)
    referral.status = ReferralStatus(status)
    referral.notes = notes or referral.notes
    await log_activity(db, user.id, "UPDATE_REFERRAL_STATUS", "referrals", str(referral.id), {"status": status}, request.client.host if request and request.client else None)
    await db.commit()
    return referral
