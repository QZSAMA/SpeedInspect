from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Annotated
from sqlalchemy import func
from uuid import UUID, uuid4

from src.app.config import settings


# 数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL.get_secret_value(),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# 会话工厂
SessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 基础模型类
class Base(DeclarativeBase):
    """基础ORM模型类"""
    __abstract__ = True
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)


# 时间戳Mixin
class TimestampMixin:
    """时间戳Mixin，给需要额外时间字段的模型使用"""
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)


# 数据库依赖
async def get_db() -> AsyncSession:
    """获取数据库会话依赖"""
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
