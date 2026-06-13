from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook
from io import BytesIO
from ..database import get_db
from ..models import BulkImportJob, User
from ..middleware.rbac import get_current_user

router = APIRouter(prefix="/api/import", tags=["import"])
UPLOAD_DIR = Path("uploads")


@router.post("/upload")
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    UPLOAD_DIR.mkdir(exist_ok=True)
    path = UPLOAD_DIR / file.filename
    path.write_bytes(await file.read())
    job = BulkImportJob(uploaded_by=user.id, file_name=file.filename, file_path=str(path))
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return {"job_id": str(job.id), "status": job.status.value}


@router.get("/template")
async def template():
    wb = Workbook()
    ws = wb.active
    ws.append(["full_name", "birth_date", "sex", "guardian_name", "contact_number", "barangay_name", "purok_name", "latitude", "longitude", "measurement_date", "weight_kg", "height_cm", "muac_cm"])
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=child_import_template.xlsx"})


@router.get("/jobs")
async def jobs(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return list((await db.scalars(select(BulkImportJob).order_by(BulkImportJob.created_at.desc()))).all())


@router.get("/jobs/{job_id}")
async def job(job_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await db.get(BulkImportJob, job_id)
