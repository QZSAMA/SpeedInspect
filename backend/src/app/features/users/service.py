from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from uuid import UUID
from typing import Optional, Tuple

from src.app.core.errors import NotFoundError, ConflictError, AuthenticationError
from src.app.core.security import get_password_hash, verify_password
from src.app.features.users.models import User
from src.app.features.users.schemas import UserCreate, UserUpdate


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        result = await self.db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_account(self, account: str) -> Optional[User]:
        """根据账号（手机号/邮箱）获取用户"""
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.phone == account,
                    User.email == account
                ),
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_in: UserCreate) -> User:
        """创建用户"""
        # 检查手机号是否已存在
        if user_in.phone and await self.get_by_phone(user_in.phone):
            raise ConflictError("Phone number already registered", field="phone")
        
        # 检查邮箱是否已存在
        if user_in.email and await self.get_by_email(user_in.email):
            raise ConflictError("Email already registered", field="email")
        
        # 创建用户
        db_user = User(
            phone=user_in.phone,
            email=user_in.email,
            nickname=user_in.nickname,
            avatar_url=user_in.avatar_url,
            password_hash=get_password_hash(user_in.password) if user_in.password else None,
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def update(self, user_id: UUID, user_in: UserUpdate) -> User:
        """更新用户信息"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise NotFoundError("User", str(user_id))
        
        # 检查手机号是否已被其他用户使用
        if user_in.phone and user_in.phone != db_user.phone:
            if await self.get_by_phone(user_in.phone):
                raise ConflictError("Phone number already registered", field="phone")
            db_user.phone = user_in.phone
        
        # 检查邮箱是否已被其他用户使用
        if user_in.email and user_in.email != db_user.email:
            if await self.get_by_email(user_in.email):
                raise ConflictError("Email already registered", field="email")
            db_user.email = user_in.email
        
        # 更新其他字段
        if user_in.nickname:
            db_user.nickname = user_in.nickname
        if user_in.avatar_url:
            db_user.avatar_url = user_in.avatar_url
        if user_in.password:
            db_user.password_hash = get_password_hash(user_in.password)
        
        await self.db.commit()
        await self.db.refresh(db_user)
        
        return db_user
    
    async def authenticate(self, account: str, password: str) -> Tuple[Optional[User], str]:
        """用户认证"""
        user = await self.get_by_account(account)
        
        if not user:
            return None, "User not found"
        
        if not user.password_hash or not verify_password(password, user.password_hash):
            return None, "Invalid password"
        
        if user.status != "active":
            return None, "User account is disabled"
        
        return user, "success"
    
    async def delete(self, user_id: UUID) -> None:
        """删除用户（软删除）"""
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise NotFoundError("User", str(user_id))
        
        db_user.is_deleted = True
        await self.db.commit()
