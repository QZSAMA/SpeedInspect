from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from src.app.features.reports.schemas import HouseProblem


class AnalyzeVideoRequest(BaseModel):
    """分析视频请求"""
    file_id: str = Field(..., description="上传的视频文件ID")
    options: Optional[dict] = Field(None, description="分析选项")


class AnalyzeVideoResponse(BaseModel):
    """分析视频响应"""
    task_id: str = Field(..., description="分析任务ID")
    status: str = Field(..., description="任务状态: pending/processing/completed/failed")
    progress: int = Field(0, description="分析进度 0-100")
    estimated_time_remaining: Optional[int] = Field(None, description="预估剩余时间(秒)")
    problems: Optional[List[HouseProblem]] = Field(None, description="检测到的问题列表(分析完成时返回)")
    report_id: Optional[UUID] = Field(None, description="生成的报告ID(分析完成时返回)")


class AnalysisStatusResponse(BaseModel):
    """分析状态响应"""
    task_id: str = Field(..., description="分析任务ID")
    status: str = Field(..., description="任务状态: pending/processing/completed/failed")
    progress: int = Field(0, description="分析进度 0-100")
    current_step: Optional[str] = Field(None, description="当前处理步骤")
    problems_found: int = Field(0, description="已检测到的问题数量")
    estimated_time_remaining: Optional[int] = Field(None, description="预估剩余时间(秒)")
    error: Optional[str] = Field(None, description="错误信息(失败时返回)")
    problems: Optional[List[HouseProblem]] = Field(None, description="检测到的问题列表(分析完成时返回)")
    report_id: Optional[UUID] = Field(None, description="生成的报告ID(分析完成时返回)")
