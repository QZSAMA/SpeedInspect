from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.app.core.database import get_db
from src.app.core.security import get_user_id_from_token
from src.app.core.errors import AuthenticationError, AuthorizationError
from src.app.features.users.service import UserService
from src.app.features.users.models import User


# Bearer token 认证
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前登录用户依赖"""
    if not credentials:
        raise AuthenticationError("Authorization token is required")
    
    try:
        user_id = get_user_id_from_token(credentials.credentials)
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        
        if not user or user.is_deleted:
            raise AuthenticationError("User not found or disabled")
        
        return user
    except Exception as e:
        raise AuthenticationError(str(e)) from e


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户依赖"""
    if current_user.status != "active":
        raise AuthorizationError("User account is disabled")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """获取当前管理员用户依赖"""
    if current_user.role not in ["admin", "superadmin"]:
        raise AuthorizationError("Admin privileges required")
    return current_user


async def get_current_enterprise_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """获取当前企业用户依赖"""
    if current_user.role not in ["enterprise", "admin", "superadmin"]:
        raise AuthorizationError("Enterprise privileges required")
    return current_user


def require_role(*roles: str):
    """角色权限校验依赖工厂"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise AuthorizationError(f"Requires one of roles: {', '.join(roles)}")
        return current_user
    
    return role_checker
