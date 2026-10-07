import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db.models import Session, User
from app.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_NAME = "etal_session"
LOCAL_USER_EMAIL = "local@et-al.local"
_hasher = PasswordHasher()


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class UserOut(BaseModel):
    id: str
    email: str
    is_admin: bool
    budget_usd: float


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _start_session(db: AsyncSession, user: User, response: Response, settings: Settings) -> None:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=settings.session_ttl_days)
    db.add(Session(token_hash=_hash_token(token), user_id=user.id, expires_at=expires))
    await db.commit()
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.session_ttl_days * 86400,
    )


async def _local_user(db: AsyncSession, settings: Settings) -> User:
    user = await db.scalar(select(User).where(User.email == LOCAL_USER_EMAIL))
    if user is None:
        user = User(email=LOCAL_USER_EMAIL, password_hash="!", is_admin=True, budget_usd=settings.default_user_budget_usd)
        db.add(user)
        await db.commit()
    return user


async def current_user(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> User:
    if settings.auth_mode == "none":
        return await _local_user(db, settings)
    if not session_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    session = await db.get(Session, _hash_token(session_token))
    if session is None or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired")
    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Account disabled")
    return user


def _out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, is_admin=user.is_admin, budget_usd=user.budget_usd)


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    creds: Credentials,
    response: Response,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UserOut:
    if settings.auth_mode == "none":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Auth is disabled on this instance")
    is_first = (await db.scalar(select(func.count()).select_from(User))) == 0
    if not is_first and not settings.allow_signup:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Signup is disabled")
    email = creds.email.lower()
    if await db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=email,
        password_hash=_hasher.hash(creds.password),
        is_admin=is_first,
        budget_usd=settings.default_user_budget_usd,
    )
    db.add(user)
    await db.flush()
    await _start_session(db, user, response, settings)
    return _out(user)


@router.post("/login", response_model=UserOut)
async def login(
    creds: Credentials,
    response: Response,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UserOut:
    user = await db.scalar(select(User).where(User.email == creds.email.lower()))
    try:
        if user is None or not user.is_active:
            raise VerifyMismatchError
        _hasher.verify(user.password_hash, creds.password)
    except VerifyMismatchError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    await _start_session(db, user, response, settings)
    return _out(user)


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> None:
    if session_token:
        await db.execute(delete(Session).where(Session.token_hash == _hash_token(session_token)))
        await db.commit()
    response.delete_cookie(COOKIE_NAME)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)) -> UserOut:
    return _out(user)
