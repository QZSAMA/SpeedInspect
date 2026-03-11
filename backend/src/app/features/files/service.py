from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from typing import Optional
from src.app.config import settings
import structlog
import os
from datetime import datetime

logger = structlog.get_logger()


class FileService:
    """文件服务类"""
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.local_path = Path(settings.STORAGE_LOCAL_PATH)
        self.local_path.mkdir(exist_ok=True, parents=True)
    
    async def upload_file(self, file: UploadFile, user_id: str) -> dict:
        """
        上传文件
        """
        if self.storage_type == "local":
            return await self._upload_local(file, user_id)
        else:
            # TODO: 实现其他存储方式（S3/OSS等）
            raise NotImplementedError(f"Storage type {self.storage_type} not implemented")
    
    async def _upload_local(self, file: UploadFile, user_id: str) -> dict:
        """
        本地上传文件
        """
        # 生成文件名
        file_extension = Path(file.filename).suffix if file.filename else ""
        file_id = str(uuid4())
        stored_filename = f"{file_id}{file_extension}"
        
        # 创建用户目录
        user_dir = self.local_path / user_id
        user_dir.mkdir(exist_ok=True)
        
        file_path = user_dir / stored_filename
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        logger.info(
            "file_uploaded",
            file_id=file_id,
            original_name=file.filename,
            size=file_size,
            user_id=user_id,
            content_type=file.content_type
        )
        
        return {
            "id": file_id,
            "filename": stored_filename,
            "original_name": file.filename,
            "size": file_size,
            "mime_type": file.content_type,
            "url": f"/uploads/{user_id}/{stored_filename}",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def get_file_path(self, file_id: str, user_id: Optional[str] = None) -> Optional[Path]:
        """
        获取文件路径
        """
        if self.storage_type == "local":
            if user_id:
                # 先查找用户目录
                user_dir = self.local_path / user_id
                for file_path in user_dir.glob(f"{file_id}.*"):
                    if file_path.exists():
                        return file_path
            
            # 全局查找
            for file_path in self.local_path.rglob(f"{file_id}.*"):
                if file_path.exists():
                    return file_path
        
        return None
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """
        删除文件
        """
        file_path = await self.get_file_path(file_id, user_id)
        if file_path and file_path.exists():
            file_path.unlink()
            logger.info(
                "file_deleted",
                file_id=file_id,
                user_id=user_id
            )
            return True
        
        return False
