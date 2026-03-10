from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class ProblemCategory(str, Enum):
    """问题类别"""
    WALL_DAMAGE = 'wall_damage'
    FURNITURE_WEAR = 'furniture_wear'
    PLUMBING_ELECTRIC = 'plumbing_electric'
    FLOORING = 'flooring'
    CEILING = 'ceiling'
    WINDOW_DOOR = 'window_door'
    BATHROOM = 'bathroom'
    KITCHEN = 'kitchen'
    LIGHTING = 'lighting'
    PAINTING = 'painting'
    MOLD = 'mold'
    WATER_DAMAGE = 'water_damage'
    PEST_INFESTATION = 'pest_infestation'
    SAFETY_HAZARD = 'safety_hazard'
    OTHER = 'other'


class SeverityLevel(int, Enum):
    """问题严重程度"""
    MINOR = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


class BoundingBox(BaseModel):
    """边界框"""
    x: float = Field(..., description="X坐标")
    y: float = Field(..., description="Y坐标")
    width: float = Field(..., description="宽度")
    height: float = Field(..., description="高度")


class HouseProblem(BaseModel):
    """房屋问题"""
    id: str = Field(..., description="问题ID")
    category: ProblemCategory = Field(..., description="问题类别")
    description: str = Field(..., description="问题描述")
    severity: SeverityLevel = Field(..., description="严重程度")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    location: str = Field(..., description="位置描述")
    frame_timestamp: Optional[float] = Field(None, description="视频帧时间戳")
    bounding_box: Optional[BoundingBox] = Field(None, description="边界框")
    repair_suggestion: str = Field(..., description="修复建议")
    estimated_cost: float = Field(..., ge=0, description="预估修复费用")
    image_url: Optional[str] = Field(None, description="问题图片URL")


class ReportSummary(BaseModel):
    """报告摘要"""
    total_problems: int = Field(..., description="总问题数")
    critical_count: int = Field(..., description="严重问题数")
    high_count: int = Field(..., description="高级问题数")
    moderate_count: int = Field(..., description="中等问题数")
    low_count: int = Field(..., description="轻微问题数")
    total_estimated_cost: float = Field(..., description="总预估费用")
    overall_score: int = Field(..., ge=0, le=100, description="综合评分")


class PropertyType(str, Enum):
    """房屋类型"""
    APARTMENT = 'apartment'
    HOUSE = 'house'
    VILLA = 'villa'
    OFFICE = 'office'
    COMMERCIAL = 'commercial'


class InspectionReportBase(BaseModel):
    """检查报告基础信息"""
    property_type: PropertyType = Field(..., description="房屋类型")
    address: Optional[str] = Field(None, description="房屋地址")
    problems: List[HouseProblem] = Field(default_factory=list, description="问题列表")
    summary: Optional[ReportSummary] = Field(None, description="报告摘要")
    video_file_id: Optional[str] = Field(None, description="视频文件ID")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")


class InspectionReportCreate(InspectionReportBase):
    """创建报告请求"""
    user_id: UUID = Field(..., description="用户ID")


class InspectionReport(InspectionReportBase):
    """检查报告响应"""
    id: UUID = Field(..., description="报告ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    user_id: UUID = Field(..., description="用户ID")
    status: str = Field(..., description="报告状态: draft/completed/archived")

    class Config:
        from_attributes = True
