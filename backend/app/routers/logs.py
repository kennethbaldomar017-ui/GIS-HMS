from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import require_super_admin
from ..models import ActivityLog

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("")
async def logs(action: str | None = None, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    stmt = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    if action:
        stmt = stmt.where(ActivityLog.action == action)
    return list((await db.scalars(stmt)).all())
