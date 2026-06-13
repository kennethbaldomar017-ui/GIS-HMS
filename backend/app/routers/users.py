from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..middleware.rbac import require_super_admin
from ..models import User
from ..models.entities import UserRole
from ..schemas.common import UserCreate, UserRead
from ..utils.security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    return list((await db.scalars(select(User).order_by(User.username))).all())


@router.post("", response_model=UserRead)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    user = User(username=body.username, email=body.email, password_hash=hash_password(body.password), role=UserRole(body.role), barangay_id=body.barangay_id)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, body: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.username, user.email, user.role, user.barangay_id = body.username, body.email, UserRole(body.role), body.barangay_id
    if body.password:
        user.password_hash = hash_password(body.password)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = False
    await db.commit()
    return {"ok": True}


@router.post("/{user_id}/reset-password")
async def reset_password(user_id: UUID, password: str = "Admin@123", db: AsyncSession = Depends(get_db), _=Depends(require_super_admin)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.password_hash = hash_password(password)
    await db.commit()
    return {"temporary_password": password}
