"""GripWise Backend — Auth router: register, login, refresh."""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.database import get_db
from backend.models import User
from backend.schemas import ApiResponse, RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from backend.auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

log = structlog.get_logger()
router = APIRouter()


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check uniqueness
    if body.email:
        result = await db.execute(select(User).where(User.email == body.email))
        if result.scalar_one_or_none():
            raise HTTPException(422, detail={"code": "VALIDATION_ERROR", "message": "Email already registered"})
    if body.mobile:
        result = await db.execute(select(User).where(User.mobile == body.mobile))
        if result.scalar_one_or_none():
            raise HTTPException(422, detail={"code": "VALIDATION_ERROR", "message": "Mobile already registered"})

    user = User(
        email=body.email,
        mobile=body.mobile,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
        role=body.role.value,
        workshop_name=body.workshop_name,
        workshop_city=body.workshop_city,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    log.info("user.registered", user_id=user.id, role=user.role)
    return ApiResponse.ok(TokenResponse(
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    ))


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            or_(User.email == body.credential, User.mobile == body.credential),
            User.is_active == True,
            User.deleted_at == None,
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, detail={"code": "UNAUTHORIZED", "message": "Invalid credentials"})

    log.info("user.login", user_id=user.id)
    return ApiResponse.ok(TokenResponse(
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    ))


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(401, detail={"code": "UNAUTHORIZED", "message": "Not a refresh token"})
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, detail={"code": "UNAUTHORIZED", "message": "User not found"})
    return ApiResponse.ok(TokenResponse(
        user_id=user.id,
        role=user.role,
        display_name=user.display_name,
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    ))
