"""
榜单相关API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

try:
    from ...merchant_service import merchant_service
except ImportError:
    from merchant_service import merchant_service

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/hot")
async def get_hot_rankings(
    category: Optional[str] = None, 
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    limit: int = 50
):
    """获取热门商家榜单"""
    try:
        amount_range = None
        if amount_min is not None or amount_max is not None:
            amount_range = (amount_min or 0.0, amount_max or float('inf'))
        
        rankings = merchant_service.get_hot_rankings(
            category=category,
            amount_range=amount_range,
            limit=limit
        )
        
        return {
            "success": True,
            "data": rankings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门榜单失败: {str(e)}")


@router.get("/sponsor")
async def get_sponsor_rankings(page: int = 1, page_size: int = 10):
    """获取赞助商家榜单"""
    try:
        limit = page_size * 4  # 获取更多数据用于分页
        sponsors = merchant_service.get_sponsor_rankings(limit=limit)
        
        # 分页处理
        start = (page - 1) * page_size
        end = start + page_size
        page_data = sponsors[start:end]
        
        return {
            "success": True,
            "data": page_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(sponsors),
                "total_pages": (len(sponsors) + page_size - 1) // page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取赞助榜单失败: {str(e)}")


@router.post("/update")
async def update_rankings_task(period_days: int = 30):
    """手动触发榜单更新（定时任务调用）"""
    try:
        result = merchant_service.update_rankings(period_days=period_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新榜单失败: {str(e)}")

