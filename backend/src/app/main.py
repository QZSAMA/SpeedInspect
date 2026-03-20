from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from src.app.config import settings
from src.app.core.database import engine
from src.app.core.errors import app_error_handler, AppError
from src.app.middleware import RequestIDMiddleware, HTTPSProxyMiddleware
from src.app.features.auth.router import router as auth_router
from src.app.features.users.router import router as users_router
from src.app.features.files.router import router as files_router
from src.app.features.orders.router import router as orders_router
from src.app.features.reports.router import router as reports_router
from src.app.features.ai.router import router as ai_router
from src.app.features.health.router import router as health_router


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    
    yield
    
    # 关闭时执行
    await engine.dispose()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="SpeedInspect 房屋状态智能识别系统API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        terms_of_service=None,
        contact={
            "name": "QZ",
            "email": "KELVINCHAO1996@GMAIL.COM",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # 注册中间件（注意顺序，后注册的先执行）
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(HTTPSProxyMiddleware)
    
    # 直接在这里添加CORS中间件，确保配置生效
    # 使用配置文件中的CORS origins，支持credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )
    
    # 注册异常处理器
    app.add_exception_handler(AppError, app_error_handler)
    
    # 注册路由
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix="", tags=["health"])
    app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["auth"])
    app.include_router(users_router, prefix=f"{api_prefix}/users", tags=["users"])
    app.include_router(files_router, prefix=f"{api_prefix}/files", tags=["files"])
    app.include_router(orders_router, prefix=f"{api_prefix}", tags=["orders"])
    app.include_router(reports_router, prefix=f"{api_prefix}/reports", tags=["reports"])
    app.include_router(ai_router, prefix=f"{api_prefix}/ai", tags=["ai"])
    
    # 根路径
    @app.get("/", tags=["root"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs" if settings.DEBUG else None,
        }
    
    return app


app = create_app()
