from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from src.app.core.database import get_db
from src.app.core.security import create_access_token, create_refresh_token
from src.app.core.errors import AuthenticationError
from src.app.features.users.service import UserService
from src.app.features.users.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from src.app.shared.responses import ApiResponse
from src.app.config import settings

router = APIRouter()


@router.post("/register", summary="用户注册", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """新用户注册"""
    user_service = UserService(db)
    user = await user_service.create(user_in)
    
    return ApiResponse.success(
        data=UserResponse.model_validate(user),
        message="User registered successfully",
    )


@router.post("/login", summary="用户登录")
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """用户登录，返回访问令牌和刷新令牌"""
    user_service = UserService(db)
    user, message = await user_service.authenticate(credentials.account, credentials.password)
    
    if not user:
        raise AuthenticationError(message)
    
    # 生成令牌
    access_token, access_expire = create_access_token(
        user.id,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    refresh_token, refresh_expire = create_refresh_token(
        user.id,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    
    return ApiResponse.success(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_expire,
            user=UserResponse.model_validate(user),
        ),
        message="Login successful",
    )


@router.post("/refresh-token", summary="刷新访问令牌")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """使用刷新令牌获取新的访问令牌"""
    from src.app.core.security import get_user_id_from_token
    
    try:
        user_id = get_user_id_from_token(refresh_token, token_type="refresh")
    except AuthenticationError:
        raise AuthenticationError("Invalid or expired refresh token")
    
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user or user.is_deleted or user.status != "active":
        raise AuthenticationError("User not found or disabled")
    
    # 生成新的令牌
    new_access_token, access_expire = create_access_token(user.id)
    new_refresh_token, refresh_expire = create_refresh_token(user.id)
    
    return ApiResponse.success(
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_at=access_expire,
            user=UserResponse.model_validate(user),
        ),
        message="Token refreshed successfully",
    )
