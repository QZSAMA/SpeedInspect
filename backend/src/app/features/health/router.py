from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.app.core.database import get_db
from src.app.shared.responses import ApiResponse

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check() -> ApiResponse:
    """健康检查接口，用于监控服务是否正常运行"""
    return ApiResponse.success(
        data={
            "status": "healthy",
            "service": "SpeedInspect Backend",
        },
        message="Service is running",
    )


@router.get("/ready", summary="就绪检查")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> ApiResponse:
    """就绪检查接口，检查所有依赖是否正常"""
    checks = {}
    
    # 检查数据库连接
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        return ApiResponse.error(
            code=503,
            message="Service is not ready",
            details={"checks": checks},
        )
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return ApiResponse.success(
        data={
            "status": "ready" if all_ok else "degraded",
            "checks": checks,
        },
        message="Service is ready" if all_ok else "Service is degraded",
    )
