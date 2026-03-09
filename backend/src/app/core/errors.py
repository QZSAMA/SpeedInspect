from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Optional, Dict


class AppError(Exception):
    """应用基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    """资源不存在异常"""
    
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictError(AppError):
    """资源冲突异常"""
    
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details={"field": field} if field else {},
        )


class AuthenticationError(AppError):
    """认证失败异常"""
    
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(AppError):
    """权限不足异常"""
    
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(AppError):
    """参数校验异常"""
    
    def __init__(self, message: str, errors: Optional[list[Dict[str, Any]]] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors or []},
        )


class RateLimitError(AppError):
    """限流异常"""
    
    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            message="Rate limit exceeded",
            code="RATE_LIMITED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """全局异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
            "details": exc.details,
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            "timestamp": int(request.state.timestamp) if hasattr(request.state, "timestamp") else None,
        },
    )


# 错误码与异常类映射
ERROR_CODE_MAP = {
    "NOT_FOUND": NotFoundError,
    "CONFLICT": ConflictError,
    "UNAUTHORIZED": AuthenticationError,
    "FORBIDDEN": AuthorizationError,
    "VALIDATION_ERROR": ValidationError,
    "RATE_LIMITED": RateLimitError,
}
