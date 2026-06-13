from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import get_settings
from ..database import get_db
from ..middleware.rbac import bearer, get_current_user
from ..models import User
from ..schemas.common import LoginRequest, TokenResponse, UserRead
from ..utils.security import create_access_token, create_refresh_token, decode_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_payload(user: User) -> dict:
    return {"id": str(user.id), "username": user.username, "email": user.email, "role": user.role.value, "barangay_id": str(user.barangay_id) if user.barangay_id else None}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.username == body.username))
    if not user or not verify_password(body.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    extra = {"role": user.role.value, "barangay_id": str(user.barangay_id) if user.barangay_id else None}
    return TokenResponse(access_token=create_access_token(str(user.id), extra), refresh_token=create_refresh_token(str(user.id), extra), user=user_payload(user))


@router.post("/refresh")
async def refresh(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.get(User, UUID(payload["sub"]))
    except (JWTError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return {"access_token": create_access_token(str(user.id), {"role": user.role.value}), "token_type": "bearer"}


@router.post("/logout")
async def logout():
    return {"ok": True}


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user
