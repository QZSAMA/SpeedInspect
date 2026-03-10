from fastapi import APIRouter, Depends
from src.app.dependencies import get_current_user
from src.app.shared.responses import ApiResponse

router = APIRouter()


@router.get("")
async def get_orders(
    page: int = 1,
    page_size: int = 10,
    current_user = Depends(get_current_user)
):
    """获取订单列表"""
    # TODO: 实现订单列表查询逻辑
    return ApiResponse.success(data={
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size
    })


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """获取订单详情"""
    # TODO: 实现订单详情查询逻辑
    return ApiResponse.success(data={
        "id": order_id,
        "order_no": "ORD202603090001",
        "amount": 49.0,
        "status": "paid",
        "created_at": "2026-03-09T14:00:00Z"
    })


@router.post("")
async def create_order(
    current_user = Depends(get_current_user)
):
    """创建订单"""
    # TODO: 实现订单创建逻辑
    return ApiResponse.success(data={
        "id": "order_123",
        "order_no": "ORD202603090001",
        "amount": 49.0,
        "status": "pending",
        "pay_url": "https://payment.example.com/pay/xxx"
    })


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """支付订单"""
    # TODO: 实现订单支付逻辑
    return ApiResponse.success(data={"status": "success"})
