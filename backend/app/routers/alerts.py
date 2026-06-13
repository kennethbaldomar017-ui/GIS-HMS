from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user
from ..models import Alert, Child, User
from ..services.audit import log_activity

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(severity: str | None = None, is_resolved: bool | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Alert).join(Child, Child.id == Alert.child_id).order_by(Alert.created_at.desc())
    if user.role.value == "admin":
        stmt = stmt.where(Child.barangay_id == user.barangay_id)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
    if is_resolved is not None:
        stmt = stmt.where(Alert.is_resolved == is_resolved)
    return list((await db.scalars(stmt)).all())


@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: UUID, request: Request, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    alert = await db.get(Alert, alert_id)
    alert.is_resolved = True
    alert.resolved_by = user.id
    alert.resolved_at = datetime.now(timezone.utc)
    await log_activity(db, user.id, "RESOLVE_ALERT", "alerts", str(alert.id), {}, request.client.host if request.client else None)
    await db.commit()
    return {"ok": True}


@router.post("/generate-batch")
async def generate_batch():
    return {"ok": True, "message": "Measurements already generate alerts automatically."}


@router.get("/unread-count")
async def unread_count(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    rows = await list_alerts(is_resolved=False, db=db, user=user)
    return {"count": sum(1 for a in rows if a.severity.value in {"critical", "high"})}
