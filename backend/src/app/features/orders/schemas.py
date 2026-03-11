from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = 'pending'
    PAID = 'paid'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'


class OrderType(str, Enum):
    """订单类型"""
    STANDARD_INSPECTION = 'standard_inspection'
    PREMIUM_INSPECTION = 'premium_inspection'
    ENTERPRISE_INSPECTION = 'enterprise_inspection'


class OrderItem(BaseModel):
    """订单项"""
    name: str = Field(..., description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    quantity: int = Field(1, ge=1, description="数量")
    unit_price: float = Field(..., ge=0, description="单价")
    report_id: Optional[UUID] = Field(None, description="关联报告ID")


class OrderBase(BaseModel):
    """订单基础信息"""
    type: OrderType = Field(..., description="订单类型")
    items: List[OrderItem] = Field(..., description="订单项列表")
    property_address: Optional[str] = Field(None, description="房屋地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    notes: Optional[str] = Field(None, description="备注信息")


class OrderCreate(OrderBase):
    """创建订单请求"""
    pass


class Order(OrderBase):
    """订单响应"""
    id: UUID = Field(..., description="订单ID")
    user_id: UUID = Field(..., description="用户ID")
    order_number: str = Field(..., description="订单号")
    status: OrderStatus = Field(..., description="订单状态")
    total_amount: float = Field(..., description="总金额")
    paid_amount: float = Field(0, description="已支付金额")
    payment_method: Optional[str] = Field(None, description="支付方式")
    paid_at: Optional[datetime] = Field(None, description="支付时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    cancelled_at: Optional[datetime] = Field(None, description="取消时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """支付请求"""
    payment_method: str = Field(..., description="支付方式: wechat/alipay/card")
    return_url: Optional[str] = Field(None, description="支付完成后跳转地址")


class PaymentResponse(BaseModel):
    """支付响应"""
    order_id: UUID = Field(..., description="订单ID")
    payment_url: Optional[str] = Field(None, description="支付跳转地址")
    qr_code: Optional[str] = Field(None, description="二维码内容（base64）")
    status: str = Field(..., description="支付状态")
