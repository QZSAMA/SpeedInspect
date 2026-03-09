from pydantic import BaseModel, Field, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """用户基础Schema"""
    phone: Optional[str] = Field(None, description="手机号", pattern=r"^1[3-9]\d{9}$")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, description="昵称", min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(None, description="头像URL")


class UserCreate(UserBase):
    """创建用户Schema"""
    password: str = Field(..., description="密码", min_length=8, max_length=128)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码复杂度"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(UserBase):
    """更新用户Schema"""
    password: Optional[str] = Field(None, description="新密码", min_length=8, max_length=128)


class UserLogin(BaseModel):
    """用户登录Schema"""
    account: str = Field(..., description="账号（手机号/邮箱）")
    password: str = Field(..., description="密码", min_length=8, max_length=128)


class UserResponse(UserBase):
    """用户返回Schema"""
    id: UUID
    status: str
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录令牌返回Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
