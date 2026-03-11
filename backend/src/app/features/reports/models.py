from sqlalchemy import Column, String, JSON, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.app.core.database import Base


class Report(Base):
    """检查报告模型"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    property_type = Column(String, nullable=False)
    address = Column(String, nullable=True)
    problems = Column(JSON, default=list, nullable=False)
    summary = Column(JSON, default=dict, nullable=False)
    video_file_id = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String, default="completed", nullable=False)  # draft/completed/archived
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    # user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report {self.id}>"
