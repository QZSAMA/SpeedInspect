from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional
from src.app.features.reports.models import Report
from src.app.features.reports.schemas import InspectionReportCreate, InspectionReport as InspectionReportSchema, ReportSummary
import structlog

logger = structlog.get_logger()


class ReportService:
    """报告服务类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, report_data: dict) -> InspectionReportSchema:
        """
        创建新报告
        """
        # 计算报告摘要
        if "problems" in report_data:
            summary = self._calculate_summary(report_data["problems"])
            report_data["summary"] = summary.dict()
        
        db_report = Report(**report_data)
        self.db_session.add(db_report)
        await self.db_session.commit()
        await self.db_session.refresh(db_report)
        
        logger.info(
            "report_created",
            report_id=str(db_report.id),
            user_id=str(db_report.user_id),
            problems_count=len(db_report.problems)
        )
        
        return InspectionReportSchema.from_orm(db_report)
    
    async def get_by_id(self, report_id: UUID, user_id: Optional[UUID] = None) -> Optional[InspectionReportSchema]:
        """
        根据ID获取报告
        """
        query = select(Report).where(Report.id == report_id)
        if user_id:
            query = query.where(Report.user_id == user_id)
        
        result = await self.db_session.execute(query)
        db_report = result.scalar_one_or_none()
        
        if not db_report:
            return None
        
        return InspectionReportSchema.from_orm(db_report)
    
    async def get_by_user_id(self, user_id: UUID, page: int = 1, page_size: int = 10) -> tuple[List[InspectionReportSchema], int]:
        """
        获取用户的报告列表
        """
        offset = (page - 1) * page_size
        
        # 查询报告列表
        query = select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db_session.execute(query)
        reports = result.scalars().all()
        
        # 查询总数
        count_query = select(Report).where(Report.user_id == user_id)
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar_one()
        
        return [InspectionReportSchema.from_orm(report) for report in reports], total
    
    async def update(self, report_id: UUID, report_data: dict, user_id: Optional[UUID] = None) -> Optional[InspectionReportSchema]:
        """
        更新报告
        """
        db_report = await self.get_by_id(report_id, user_id)
        if not db_report:
            return None
        
        for key, value in report_data.items():
            if key == "problems":
                # 重新计算摘要
                summary = self._calculate_summary(value)
                setattr(db_report, "summary", summary.dict())
            setattr(db_report, key, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(db_report)
        
        logger.info(
            "report_updated",
            report_id=str(report_id),
            user_id=str(user_id) if user_id else "system"
        )
        
        return InspectionReportSchema.from_orm(db_report)
    
    async def delete(self, report_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """
        删除报告
        """
        db_report = await self.get_by_id(report_id, user_id)
        if not db_report:
            return False
        
        await self.db_session.delete(db_report)
        await self.db_session.commit()
        
        logger.info(
            "report_deleted",
            report_id=str(report_id),
            user_id=str(user_id) if user_id else "system"
        )
        
        return True
    
    def _calculate_summary(self, problems: List[dict]) -> ReportSummary:
        """
        计算报告摘要
        """
        total = len(problems)
        critical = 0
        high = 0
        moderate = 0
        low = 0
        total_cost = 0
        
        for problem in problems:
            severity = problem.get("severity", 1)
            cost = problem.get("estimated_cost", 0)
            
            if severity == 5:  # CRITICAL
                critical += 1
            elif severity == 4:  # HIGH
                high += 1
            elif severity == 3:  # MODERATE
                moderate += 1
            else:  # LOW/MINOR
                low += 1
            
            total_cost += cost
        
        # 计算综合评分 (0-100)
        # 严重问题扣20分/个，高级扣10分/个，中等扣5分/个，轻微扣2分/个
        score = 100 - (critical * 20 + high * 10 + moderate * 5 + low * 2)
        score = max(0, min(100, score))
        
        return ReportSummary(
            total_problems=total,
            critical_count=critical,
            high_count=high,
            moderate_count=moderate,
            low_count=low,
            total_estimated_cost=total_cost,
            overall_score=score
        )
