from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import get_current_user, require_super_admin
from ..models import Report, User
from ..models.entities import ReportStatus, ReportType
from ..schemas.common import ReportGenerate
from ..services.analytics import summary_for_barangay

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
async def list_reports(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Report).order_by(Report.generated_at.desc())
    if user.role.value == "admin":
        stmt = stmt.where(Report.generated_by == user.id)
    return list((await db.scalars(stmt)).all())


@router.post("/generate")
async def generate_report(body: ReportGenerate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    barangay_id = user.barangay_id if user.role.value == "admin" else body.barangay_id
    data = await summary_for_barangay(db, barangay_id)
    report = Report(title=body.title, report_type=ReportType(body.report_type), barangay_id=barangay_id, generated_by=user.id, period_start=body.period_start, period_end=body.period_end, data=data)
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/{report_id}")
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await db.get(Report, report_id)


@router.put("/{report_id}/submit")
async def submit_report(report_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    report = await db.get(Report, report_id)
    report.status = ReportStatus.submitted
    await db.commit()
    return report


@router.put("/{report_id}/approve")
async def approve_report(report_id: UUID, review_notes: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(require_super_admin)):
    report = await db.get(Report, report_id)
    report.status = ReportStatus.approved
    report.review_notes = review_notes
    report.reviewed_by = user.id
    report.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return report


@router.put("/{report_id}/reject")
async def reject_report(report_id: UUID, review_notes: str | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(require_super_admin)):
    report = await db.get(Report, report_id)
    report.status = ReportStatus.rejected
    report.review_notes = review_notes
    report.reviewed_by = user.id
    report.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return report


@router.get("/{report_id}/export")
async def export_report(report_id: UUID):
    return {"message": "Excel export placeholder", "report_id": str(report_id)}
