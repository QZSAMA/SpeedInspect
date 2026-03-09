from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.core.database import get_db
from src.app.dependencies import get_current_active_user, require_role
from src.app.features.users.service import UserService
from src.app.features.users.schemas import UserResponse, UserUpdate
from src.app.shared.responses import ApiResponse, PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/profile", summary="获取当前用户信息")
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_active_user),
) -> ApiResponse[UserResponse]:
    """获取当前登录用户的信息"""
    return ApiResponse.success(
        data=UserResponse.model_validate(current_user),
        message="Get user profile success",
    )


@router.put("/profile", summary="更新当前用户信息")
async def update_current_user_profile(
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """更新当前登录用户的信息"""
    user_service = UserService(db)
    updated_user = await user_service.update(current_user.id, user_in)
    return ApiResponse.success(
        data=UserResponse.model_validate(updated_user),
        message="Update user profile success",
    )


@router.get("/{user_id}", summary="获取用户信息（管理员）", dependencies=[Depends(require_role("admin", "superadmin"))])
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """根据用户ID获取用户信息，需要管理员权限"""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        return ApiResponse.error(
            code=status.HTTP_404_NOT_FOUND,
            message="User not found",
        )
    
    return ApiResponse.success(
        data=UserResponse.model_validate(user),
        message="Get user success",
    )


@router.delete("/{user_id}", summary="删除用户（管理员）", dependencies=[Depends(require_role("superadmin"))])
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """删除用户，需要超级管理员权限"""
    user_service = UserService(db)
    await user_service.delete(user_id)
    
    return ApiResponse.success(
        message="Delete user success",
    )
