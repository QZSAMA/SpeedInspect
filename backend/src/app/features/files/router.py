from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from src.app.dependencies import get_current_user
from src.app.shared.responses import ApiResponse

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """上传文件"""
    # TODO: 实现文件上传逻辑
    return ApiResponse.success(data={
        "file_name": file.filename,
        "file_size": file.size,
        "content_type": file.content_type,
        "url": f"/uploads/{file.filename}"
    })


@router.post("/upload-batch")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """批量上传文件"""
    # TODO: 实现批量上传逻辑
    result = []
    for file in files:
        result.append({
            "file_name": file.filename,
            "file_size": file.size,
            "content_type": file.content_type,
            "url": f"/uploads/{file.filename}"
        })
    return ApiResponse.success(data=result)


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user)
):
    """删除文件"""
    # TODO: 实现文件删除逻辑
    return ApiResponse.success(data={"file_id": file_id})
