from sqlalchemy import Column, String, JSON, DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from src.app.core.database import Base
from src.app.features.orders.schemas import OrderStatus, OrderType


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    order_number = Column(String(32), unique=True, nullable=False, index=True)
    type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    items = Column(JSON, default=list, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0, nullable=False)
    payment_method = Column(String(50), nullable=True)
    property_address = Column(String, nullable=True)
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    notes = Column(String, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Order {self.order_number}>"
