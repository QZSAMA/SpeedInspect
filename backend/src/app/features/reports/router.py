from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.app.core.database import get_db
from src.app.dependencies import get_current_user, require_role
from src.app.shared.responses import ApiResponse, PaginatedResponse
from src.app.features.reports.schemas import InspectionReportCreate, InspectionReport
from src.app.features.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=PaginatedResponse[InspectionReport], summary="获取报告列表")
async def get_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的检查报告列表"""
    report_service = ReportService(db)
    reports, total = await report_service.get_by_user_id(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return PaginatedResponse(
        data=reports,
        total=total,
        page=page,
        page_size=page_size,
        message="获取报告列表成功"
    )


@router.get("/{report_id}", response_model=ApiResponse[InspectionReport], summary="获取报告详情")
async def get_report(
    report_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取报告详情"""
    report_service = ReportService(db)
    report = await report_service.get_by_id(report_id, user_id=current_user.id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data=report,
        message="获取报告详情成功"
    )


@router.post("", response_model=ApiResponse[InspectionReport], summary="创建报告", status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: InspectionReportCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新的检查报告"""
    report_service = ReportService(db)
    report = await report_service.create({
        **report_data.dict(),
        "user_id": current_user.id
    })
    
    return ApiResponse.success(
        data=report,
        message="报告创建成功"
    )


@router.put("/{report_id}", response_model=ApiResponse[InspectionReport], summary="更新报告")
async def update_report(
    report_id: UUID,
    report_data: InspectionReportCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新报告信息"""
    report_service = ReportService(db)
    report = await report_service.update(
        report_id=report_id,
        report_data=report_data.dict(),
        user_id=current_user.id
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data=report,
        message="报告更新成功"
    )


@router.delete("/{report_id}", response_model=ApiResponse, summary="删除报告")
async def delete_report(
    report_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除报告"""
    report_service = ReportService(db)
    success = await report_service.delete(report_id, user_id=current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权限访问"
        )
    
    return ApiResponse.success(
        message="报告删除成功"
    )


@router.get("/{report_id}/download", summary="下载报告")
async def download_report(
    report_id: UUID,
    format: str = Query("pdf", description="下载格式: pdf/html/json"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """下载报告"""
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from src.app.features.reports.service import ReportGenerator
    
    report_service = ReportService(db)
    report = await report_service.get_by_id(report_id, user_id=current_user.id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权限访问"
        )
    
    if format == "json":
        return JSONResponse(content=report.dict())
    elif format == "html":
        html_content = ReportGenerator.generate_html(report)
        return HTMLResponse(content=html_content)
    elif format == "pdf":
        # TODO: 实现PDF生成
        html_content = ReportGenerator.generate_html(report)
        # 临时返回HTML，PDF生成需要安装weasyprint
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的下载格式"
        )


@router.get("/{report_id}/share", response_model=ApiResponse, summary="生成报告分享链接")
async def share_report(
    report_id: UUID,
    expire_days: int = Query(7, ge=1, le=30, description="过期天数"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """生成报告分享链接"""
    # TODO: 实现分享功能
    report_service = ReportService(db)
    report = await report_service.get_by_id(report_id, user_id=current_user.id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权限访问"
        )
    
    # 生成随机分享码
    import random
    import string
    share_code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # TODO: 存储分享码到数据库
    
    share_url = f"/share/{share_code}"
    
    return ApiResponse.success(
        data={
            "share_url": share_url,
            "expire_days": expire_days,
            "report_id": str(report_id)
        },
        message="分享链接生成成功"
    )
