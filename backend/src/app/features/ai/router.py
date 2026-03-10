from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db
from src.app.dependencies import get_current_user
from src.app.shared.responses import ApiResponse
from src.app.features.ai.schemas import AnalyzeVideoRequest, AnalyzeVideoResponse, AnalysisStatusResponse
from src.app.features.ai.service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze", response_model=AnalyzeVideoResponse, summary="分析视频")
async def analyze_video(
    request: AnalyzeVideoRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交视频分析任务
    """
    ai_service = AIService(db)
    result = await ai_service.analyze_video(
        file_id=request.file_id,
        user_id=str(current_user.id),
        options=request.options
    )
    
    return ApiResponse.success(
        data=result,
        message="视频分析任务已提交"
    )


@router.get("/analysis/{task_id}/status", response_model=AnalysisStatusResponse, summary="获取分析状态")
async def get_analysis_status(
    task_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    查询视频分析任务状态
    """
    ai_service = AIService(db)
    status = await ai_service.get_analysis_status(task_id, str(current_user.id))
    
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分析任务不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data=status,
        message="获取分析状态成功"
    )
