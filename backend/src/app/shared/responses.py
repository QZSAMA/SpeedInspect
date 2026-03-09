from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API返回格式"""
    code: int = Field(0, description="响应码，0表示成功，非0表示失败")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    details: Optional[dict[str, Any]] = Field(None, description="详细信息，错误时返回")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="请求ID")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="时间戳")

    @classmethod
    def success(
        cls,
        data: Optional[T] = None,
        message: str = "success",
        request_id: Optional[str] = None,
    ) -> "ApiResponse[T]":
        """成功响应"""
        return cls(
            code=0,
            message=message,
            data=data,
            request_id=request_id or str(uuid.uuid4()),
        )

    @classmethod
    def error(
        cls,
        code: int,
        message: str,
        details: Optional[dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> "ApiResponse[T]":
        """错误响应"""
        return cls(
            code=code,
            message=message,
            details=details,
            request_id=request_id or str(uuid.uuid4()),
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    has_next: bool = Field(..., description="是否有下一页")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页条数")

    @property
    def offset(self) -> int:
        """偏移量"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """查询条数"""
        return self.page_size

    def has_next_page(self, total: int) -> bool:
        """是否有下一页"""
        return (self.offset + self.page_size) < total
