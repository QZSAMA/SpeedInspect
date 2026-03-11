from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from src.app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(50))
    avatar_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/locked/disabled
    role: Mapped[str] = mapped_column(String(20), default="user")  # user/admin/enterprise/superadmin
    password_hash: Mapped[str | None] = mapped_column(String(255))
