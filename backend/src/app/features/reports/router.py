from fastapi import APIRouter, Depends
from src.app.dependencies import get_current_user
from src.app.shared.responses import ApiResponse

router = APIRouter()


@router.get("")
async def get_reports(
    page: int = 1,
    page_size: int = 10,
    current_user = Depends(get_current_user)
):
    """获取报告列表"""
    # TODO: 实现报告列表查询逻辑
    return ApiResponse.success(data={
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    })


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user = Depends(get_current_user)
):
    """获取报告详情"""
    # TODO: 实现报告详情查询逻辑
    return ApiResponse.success(data={
        "id": report_id,
        "property_type": "apartment",
        "property_address": "武汉市洪山区XX小区",
        "overall_score": 85,
        "status": "finished",
        "created_at": "2026-03-09T14:00:00Z",
        "problems": []
    })


@router.post("")
async def create_report(
    current_user = Depends(get_current_user)
):
    """创建报告"""
    # TODO: 实现报告创建逻辑
    return ApiResponse.success(data={
        "id": "report_123",
        "status": "generating"
    })


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user = Depends(get_current_user)
):
    """下载报告"""
    # TODO: 实现报告下载逻辑
    return ApiResponse.success(data={
        "download_url": f"/reports/{report_id}/download.pdf"
    })


@router.post("/{report_id}/share")
async def share_report(
    report_id: str,
    current_user = Depends(get_current_user)
):
    """分享报告"""
    # TODO: 实现报告分享逻辑
    return ApiResponse.success(data={
        "share_url": f"/share/{report_id}",
        "share_token": "token_123",
        "expire_time": "2026-03-16T14:00:00Z"
    })
