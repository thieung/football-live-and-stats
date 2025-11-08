"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from api.core.database import get_postgres_session
from api.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user
)
from api.models.postgres import User
from api.schemas.user import UserCreate, UserLogin, UserResponse, Token

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Register a new user
    """
    # Check if email exists
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password)
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info("user_registered", user_id=str(new_user.id), username=new_user.username)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Login with username and password
    """
    # Get user by username
    result = await session.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning("login_failed", username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info("user_logged_in", user_id=str(user.id), username=user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (client should discard tokens)
    """
    logger.info("user_logged_out", user_id=str(current_user.id))
    return {"message": "Successfully logged out"}
