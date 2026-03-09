from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import uuid
import time
import structlog
from typing import Callable

from src.app.config import settings

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件，为每个请求生成唯一ID，方便链路追踪"""
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        # 绑定上下文变量
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )
        
        # 注入到request.state
        request.state.request_id = request_id
        request.state.timestamp = start_time
        
        try:
            response = await call_next(request)
            
            # 计算耗时
            duration = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            # 记录访问日志
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration=duration,
                user_agent=request.headers.get("User-Agent"),
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                duration=duration,
                exc_info=True,
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()


# CORS中间件配置
cors_middleware = CORSMiddleware, {
    "allow_origins": settings.CORS_ORIGINS,
    "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID", "X-Response-Time"],
}
