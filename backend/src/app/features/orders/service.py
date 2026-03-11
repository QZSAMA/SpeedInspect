from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List, Optional
from datetime import datetime
import random
import string
from src.app.features.orders.models import Order
from src.app.features.orders.schemas import OrderCreate, Order as OrderSchema, OrderStatus
import structlog

logger = structlog.get_logger()


class OrderService:
    """订单服务类"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    def _generate_order_number(self) -> str:
        """生成订单号：SI + 年月日时分秒 + 4位随机数"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"SI{timestamp}{random_str}"
    
    def _calculate_total_amount(self, items: list) -> float:
        """计算订单总金额"""
        total = 0.0
        for item in items:
            total += item.get("quantity", 1) * item.get("unit_price", 0)
        return total
    
    async def create(self, order_data: OrderCreate, user_id: UUID) -> OrderSchema:
        """
        创建新订单
        """
        # 生成订单号
        order_number = self._generate_order_number()
        
        # 计算总金额
        total_amount = self._calculate_total_amount([item.dict() for item in order_data.items])
        
        db_order = Order(
            user_id=user_id,
            order_number=order_number,
            type=order_data.type,
            items=[item.dict() for item in order_data.items],
            total_amount=total_amount,
            property_address=order_data.property_address,
            contact_name=order_data.contact_name,
            contact_phone=order_data.contact_phone,
            notes=order_data.notes,
            status=OrderStatus.PENDING
        )
        
        self.db_session.add(db_order)
        await self.db_session.commit()
        await self.db_session.refresh(db_order)
        
        logger.info(
            "order_created",
            order_id=str(db_order.id),
            order_number=order_number,
            user_id=str(user_id),
            total_amount=total_amount
        )
        
        return OrderSchema.from_orm(db_order)
    
    async def get_by_id(self, order_id: UUID, user_id: Optional[UUID] = None) -> Optional[OrderSchema]:
        """
        根据ID获取订单
        """
        query = select(Order).where(Order.id == order_id)
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        result = await self.db_session.execute(query)
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            return None
        
        return OrderSchema.from_orm(db_order)
    
    async def get_by_order_number(self, order_number: str, user_id: Optional[UUID] = None) -> Optional[OrderSchema]:
        """
        根据订单号获取订单
        """
        query = select(Order).where(Order.order_number == order_number)
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        result = await self.db_session.execute(query)
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            return None
        
        return OrderSchema.from_orm(db_order)
    
    async def get_by_user_id(self, user_id: UUID, page: int = 1, page_size: int = 10) -> tuple[List[OrderSchema], int]:
        """
        获取用户的订单列表
        """
        offset = (page - 1) * page_size
        
        # 查询订单列表
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db_session.execute(query)
        orders = result.scalars().all()
        
        # 查询总数
        count_query = select(Order).where(Order.user_id == user_id)
        count_result = await self.db_session.execute(count_query)
        total = count_result.scalar_one()
        
        return [OrderSchema.from_orm(order) for order in orders], total
    
    async def update_status(self, order_id: UUID, status: OrderStatus, user_id: Optional[UUID] = None) -> Optional[OrderSchema]:
        """
        更新订单状态
        """
        db_order = await self.get_by_id(order_id, user_id)
        if not db_order:
            return None
        
        db_order.status = status
        
        if status == OrderStatus.PAID:
            db_order.paid_at = datetime.utcnow()
            db_order.paid_amount = db_order.total_amount
        elif status == OrderStatus.COMPLETED:
            db_order.completed_at = datetime.utcnow()
        elif status == OrderStatus.CANCELLED:
            db_order.cancelled_at = datetime.utcnow()
        
        await self.db_session.commit()
        await self.db_session.refresh(db_order)
        
        logger.info(
            "order_status_updated",
            order_id=str(order_id),
            status=status.value,
            user_id=str(user_id) if user_id else "system"
        )
        
        return OrderSchema.from_orm(db_order)
    
    async def process_payment(self, order_id: UUID, payment_method: str, amount: float) -> tuple[bool, str]:
        """
        处理支付
        """
        db_order = await self.get_by_id(order_id)
        if not db_order:
            return False, "订单不存在"
        
        if db_order.status == OrderStatus.PAID:
            return True, "订单已支付"
        
        if amount < db_order.total_amount:
            return False, "支付金额不足"
        
        # TODO: 实际调用支付网关
        # 这里模拟支付成功
        await self.update_status(order_id, OrderStatus.PAID)
        db_order.payment_method = payment_method
        
        await self.db_session.commit()
        
        logger.info(
            "payment_successful",
            order_id=str(order_id),
            payment_method=payment_method,
            amount=amount
        )
        
        return True, "支付成功"
    
    async def cancel(self, order_id: UUID, user_id: Optional[UUID] = None, reason: str = "") -> bool:
        """
        取消订单
        """
        db_order = await self.get_by_id(order_id, user_id)
        if not db_order:
            return False
        
        if db_order.status in [OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.COMPLETED]:
            return False
        
        await self.update_status(order_id, OrderStatus.CANCELLED, user_id)
        
        logger.info(
            "order_cancelled",
            order_id=str(order_id),
            user_id=str(user_id) if user_id else "system",
            reason=reason
        )
        
        return True
