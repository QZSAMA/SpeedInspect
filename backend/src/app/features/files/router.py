from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from typing import List
from src.app.dependencies import get_current_user
from src.app.shared.responses import ApiResponse
from src.app.features.files.service import FileService

router = APIRouter()
file_service = FileService()


@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """上传单个文件"""
    result = await file_service.upload_file(file, str(current_user.id))
    return ApiResponse.success(
        data=result,
        message="文件上传成功"
    )


@router.post("/upload-batch", summary="批量上传文件")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """批量上传文件"""
    results = []
    for file in files:
        result = await file_service.upload_file(file, str(current_user.id))
        results.append(result)
    
    return ApiResponse.success(
        data=results,
        message="文件批量上传成功"
    )


@router.get("/{file_id}", summary="获取文件信息")
async def get_file_info(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """获取文件信息"""
    file_path = await file_service.get_file_path(file_id, str(current_user.id))
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权限访问"
        )
    
    return ApiResponse.success(data={
        "id": file_id,
        "filename": file_path.name,
        "size": file_path.stat().st_size,
        "mime_type": "application/octet-stream",  # TODO: 正确识别MIME类型
        "url": f"/api/v1/files/{file_id}/download",
        "created_at": file_path.stat().st_ctime
    })


@router.get("/{file_id}/download", summary="下载文件")
async def download_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """下载文件"""
    file_path = await file_service.get_file_path(file_id, str(current_user.id))
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权限访问"
        )
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream"
    )


@router.delete("/{file_id}", summary="删除文件")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """删除文件"""
    success = await file_service.delete_file(file_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data={"file_id": file_id},
        message="文件删除成功"
    )
