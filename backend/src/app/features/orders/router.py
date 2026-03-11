from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.app.core.database import get_db
from src.app.dependencies import get_current_user, require_role
from src.app.shared.responses import ApiResponse, PaginatedResponse
from src.app.features.orders.schemas import OrderCreate, Order, PaymentRequest, PaymentResponse, OrderStatus
from src.app.features.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=PaginatedResponse[Order], summary="获取订单列表")
async def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的订单列表"""
    order_service = OrderService(db)
    orders, total = await order_service.get_by_user_id(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return PaginatedResponse(
        data=orders,
        total=total,
        page=page,
        page_size=page_size,
        message="获取订单列表成功"
    )


@router.get("/{order_id}", response_model=ApiResponse[Order], summary="获取订单详情")
async def get_order(
    order_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    order_service = OrderService(db)
    order = await order_service.get_by_id(order_id, user_id=current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data=order,
        message="获取订单详情成功"
    )


@router.get("/number/{order_number}", response_model=ApiResponse[Order], summary="根据订单号获取订单")
async def get_order_by_number(
    order_number: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """根据订单号获取订单详情"""
    order_service = OrderService(db)
    order = await order_service.get_by_order_number(order_number, user_id=current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或无权限访问"
        )
    
    return ApiResponse.success(
        data=order,
        message="获取订单详情成功"
    )


@router.post("", response_model=ApiResponse[Order], summary="创建订单", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新订单"""
    order_service = OrderService(db)
    order = await order_service.create(order_data, user_id=current_user.id)
    
    return ApiResponse.success(
        data=order,
        message="订单创建成功"
    )


@router.post("/{order_id}/pay", response_model=ApiResponse[PaymentResponse], summary="支付订单")
async def pay_order(
    order_id: UUID,
    payment_data: PaymentRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """支付订单"""
    order_service = OrderService(db)
    order = await order_service.get_by_id(order_id, user_id=current_user.id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或无权限访问"
        )
    
    if order.status == OrderStatus.PAID:
        return ApiResponse.success(
            data=PaymentResponse(
                order_id=order_id,
                status="already_paid"
            ),
            message="订单已支付"
        )
    
    if order.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已取消或已退款，无法支付"
        )
    
    # 处理支付
    success, message = await order_service.process_payment(
        order_id=order_id,
        payment_method=payment_data.payment_method,
        amount=order.total_amount
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ApiResponse.success(
        data=PaymentResponse(
            order_id=order_id,
            status="success",
            payment_url=None  # 实际支付网关会返回支付地址
        ),
        message="支付成功"
    )


@router.post("/{order_id}/cancel", response_model=ApiResponse, summary="取消订单")
async def cancel_order(
    order_id: UUID,
    reason: str = "",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """取消订单"""
    order_service = OrderService(db)
    success = await order_service.cancel(order_id, user_id=current_user.id, reason=reason)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单取消失败，可能状态不允许取消或订单不存在"
        )
    
    return ApiResponse.success(
        message="订单取消成功"
    )


@router.put("/{order_id}/status", response_model=ApiResponse[Order], summary="更新订单状态", dependencies=[Depends(require_role("admin", "superadmin"))])
async def update_order_status(
    order_id: UUID,
    status: OrderStatus,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新订单状态（管理员权限）"""
    order_service = OrderService(db)
    order = await order_service.update_status(order_id, status)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return ApiResponse.success(
        data=order,
        message="订单状态更新成功"
    )
