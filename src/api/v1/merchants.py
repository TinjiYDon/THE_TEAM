"""
商家管理相关API路由
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
try:
    from ...utils.exceptions import (
        MerchantNotFoundException, 
        MerchantAlreadyExistsException,
        ValidationException
    )
    from ...merchant_service import merchant_service
    from ...analytics_service import analytics_service
    from ...config import DATABASE_PATH, RANKING_CONFIG
except ImportError:
    from utils.exceptions import (
        MerchantNotFoundException, 
        MerchantAlreadyExistsException,
        ValidationException
    )
    from merchant_service import merchant_service
    from analytics_service import analytics_service
    from config import DATABASE_PATH, RANKING_CONFIG
import sqlite3

router = APIRouter(prefix="/merchants", tags=["merchants"])


class MerchantVerificationRequest(BaseModel):
    merchant_name: str
    business_license: str
    category: str
    license_image_path: Optional[str] = None


@router.post("/verify")
async def verify_merchant(request: MerchantVerificationRequest, user_id: int = 1):
    """商家认证申请"""
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        
        # 检查用户是否已认证商家
        cursor.execute("SELECT id FROM merchants WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            raise MerchantAlreadyExistsException()
        
        # 创建商家认证记录
        cursor.execute("""
            INSERT INTO merchants (user_id, merchant_name, business_license, license_image_path, category, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (user_id, request.merchant_name, request.business_license, 
              request.license_image_path, request.category))
        
        merchant_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "商家认证申请已提交，等待审核",
            "merchant_id": merchant_id
        }
    except MerchantAlreadyExistsException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"商家认证失败: {str(e)}")


@router.get("/my")
async def get_my_merchant(user_id: int = 1):
    """获取我的商家信息"""
    try:
        import sqlite3
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, mi.*
            FROM merchants m
            LEFT JOIN merchant_info mi ON m.id = mi.merchant_id
            WHERE m.user_id = ?
        """, (user_id,))
        
        merchant = cursor.fetchone()
        conn.close()
        
        if not merchant:
            return {"success": False, "message": "未认证商家"}
        
        return {
            "success": True,
            "data": {
                "merchant_id": merchant['id'],
                "merchant_name": merchant['merchant_name'],
                "category": merchant['category'],
                "status": merchant['status'],
                "description": merchant.get('description'),
                "address": merchant.get('address'),
                "phone": merchant.get('phone')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商家信息失败: {str(e)}")


@router.get("/{merchant_id}")
async def get_merchant_detail(merchant_id: int):
    """获取商家详情"""
    try:
        detail = merchant_service.get_merchant_detail(merchant_id)
        if not detail:
            raise MerchantNotFoundException(merchant_id)
        
        return {
            "success": True,
            "data": detail
        }
    except MerchantNotFoundException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商家详情失败: {str(e)}")


@router.post("/{merchant_id}/click")
async def track_merchant_click(
    merchant_id: int, 
    click_type: str = "view", 
    user_id: Optional[int] = None,
    request: Request = None
):
    """记录商家点击（埋点）"""
    try:
        # 获取请求头信息
        headers = {}
        if request:
            headers = {
                "X-Forwarded-For": request.headers.get("X-Forwarded-For", ""),
                "X-Real-IP": request.headers.get("X-Real-IP", ""),
                "User-Agent": request.headers.get("User-Agent", ""),
                "Referer": request.headers.get("Referer", "")
            }
        
        result = analytics_service.track_click(merchant_id, user_id, click_type, headers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录点击失败: {str(e)}")


class SponsorshipRequest(BaseModel):
    bid_amount: float
    daily_budget: float
    sponsorship_type: str = "bidding"


@router.post("/sponsor")
async def create_sponsorship(request: SponsorshipRequest, user_id: int = 1):
    """创建商家赞助"""
    try:
        import sqlite3
        from datetime import datetime
        
        # 验证商家是否已认证
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM merchants WHERE user_id = ? AND status = 'approved'", (user_id,))
        merchant = cursor.fetchone()
        
        if not merchant:
            conn.close()
            raise ValidationException("请先完成商家认证")
        
        merchant_id = merchant[0]
        
        # 验证金额
        if request.bid_amount < RANKING_CONFIG['min_bid_amount']:
            raise ValidationException(f"竞价金额不能低于{RANKING_CONFIG['min_bid_amount']}元")
        
        if request.daily_budget < RANKING_CONFIG['min_daily_budget']:
            raise ValidationException(f"每日预算不能低于{RANKING_CONFIG['min_daily_budget']}元")
        
        # 计算CPC单价（根据类别）
        cursor.execute("SELECT category FROM merchants WHERE id = ?", (merchant_id,))
        category_row = cursor.fetchone()
        category = category_row[0] if category_row else "其他"
        cpc_price = RANKING_CONFIG['cpc_price_by_category'].get(category, RANKING_CONFIG['default_cpc_price'])
        
        # 创建赞助记录
        start_date = datetime.now()
        cursor.execute("""
            INSERT INTO merchant_sponsorships
            (merchant_id, sponsorship_type, bid_amount, cpc_price, daily_budget, start_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        """, (merchant_id, request.sponsorship_type, request.bid_amount, 
              cpc_price, request.daily_budget, start_date.strftime('%Y-%m-%d %H:%M:%S')))
        
        sponsorship_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "赞助申请已创建",
            "sponsorship_id": sponsorship_id,
            "payment_required": True,
            "amount": request.bid_amount
        }
    except ValidationException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建赞助失败: {str(e)}")


@router.get("/dashboard/stats")
async def get_merchant_dashboard_stats(user_id: int = 1):
    """获取商家后台统计数据"""
    try:
        import sqlite3
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取商家ID
        cursor.execute("SELECT id FROM merchants WHERE user_id = ?", (user_id,))
        merchant_row = cursor.fetchone()
        if not merchant_row:
            conn.close()
            return {"success": False, "message": "未认证商家"}
        
        merchant_id = merchant_row[0]
        
        # 获取点击统计
        click_stats = analytics_service.get_click_stats(merchant_id)
        
        # 获取转化率
        conversion_rate = analytics_service.get_conversion_rate(merchant_id)
        
        # 获取赞助信息
        cursor.execute("""
            SELECT * FROM merchant_sponsorships
            WHERE merchant_id = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """, (merchant_id,))
        sponsorship = cursor.fetchone()
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "click_stats": click_stats,
                "conversion_rate": conversion_rate,
                "sponsorship": dict(sponsorship) if sponsorship else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

