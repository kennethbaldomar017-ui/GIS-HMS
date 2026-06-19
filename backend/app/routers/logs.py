from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import require_super_admin
from ..models import ActivityLog

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
async def logs(
    action: str | None = None,
    log_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_super_admin),
):
    stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    if action:
        stmt = stmt.where(ActivityLog.action == action)
    if log_date:
        stmt = stmt.where(func.date(ActivityLog.created_at) == log_date)
    return list((await db.scalars(stmt)).all())


@router.get("/actions")
async def log_actions(db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    rows = await db.execute(select(ActivityLog.action).distinct().order_by(ActivityLog.action))
    return [row[0] for row in rows.all()]
