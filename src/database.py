"""
数据库操作模块
"""
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import time
import threading

try:
    from .config import DATABASE_URL, DATABASE_PATH
    from .models import (
        Base, Bill, Invoice, User, FinancialProduct, UserProfile,
        UserBudget, UserSubscription, OCRUsageQuota,
        CommunityPost, PostComment, PostLike,
        UserPreference, UserRequestLog
    )
except ImportError:
    from config import DATABASE_URL, DATABASE_PATH
    from models import (
        Base, Bill, Invoice, User, FinancialProduct, UserProfile,
        UserBudget, UserSubscription, OCRUsageQuota,
        CommunityPost, PostComment, PostLike,
        UserPreference, UserRequestLog
    )
from sqlalchemy import func

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """初始化数据库，创建所有表"""
    # 确保数据目录存在
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")

@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        # 简易内存缓存（短期，避免热点统计重复计算）
        self._summary_cache: Dict[str, Any] = {}
        self._category_cache: Dict[str, Any] = {}
        self._cache_ttl_seconds = 30
        self._lock = threading.Lock()
    
    # 账单相关操作
    def create_bill(self, bill_data: Dict[str, Any]) -> Bill:
        """创建账单记录"""
        with get_db_session() as session:
            bill = Bill(**bill_data)
            session.add(bill)
            session.commit()
            session.refresh(bill)
            # 失效并预热缓存
            try:
                self._invalidate_user_caches(bill.user_id)
                self._warm_caches_async(bill.user_id)
            except Exception:
                pass
            return bill
    
    def get_bills(self, user_id: int = 1, limit: int = 100, offset: int = 0) -> List[Bill]:
        """获取账单列表"""
        with get_db_session() as session:
            return session.query(Bill).filter(Bill.user_id == user_id)\
                .order_by(Bill.consume_time.desc())\
                .offset(offset).limit(limit).all()
    
    def get_bills_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Bill]:
        """按日期范围获取账单"""
        with get_db_session() as session:
            return session.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.consume_time >= start_date,
                Bill.consume_time <= end_date
            ).order_by(Bill.consume_time.desc()).all()
    
    def get_bills_by_category(self, user_id: int, category: str) -> List[Bill]:
        """按类别获取账单"""
        with get_db_session() as session:
            return session.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.category == category
            ).order_by(Bill.consume_time.desc()).all()
    
    def get_bills_by_merchant(self, user_id: int, merchant: str) -> List[Bill]:
        """按商家获取账单"""
        with get_db_session() as session:
            return session.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.merchant.like(f"%{merchant}%")
            ).order_by(Bill.consume_time.desc()).all()
    
    def update_bill(self, bill_id: int, update_data: Dict[str, Any]) -> Optional[Bill]:
        """更新账单记录"""
        with get_db_session() as session:
            bill = session.query(Bill).filter(Bill.id == bill_id).first()
            if bill:
                for key, value in update_data.items():
                    setattr(bill, key, value)
                session.commit()
                session.refresh(bill)
                try:
                    self._invalidate_user_caches(bill.user_id)
                    self._warm_caches_async(bill.user_id)
                except Exception:
                    pass
                return bill
            return None
    
    def delete_bill(self, bill_id: int) -> bool:
        """删除账单记录"""
        with get_db_session() as session:
            bill = session.query(Bill).filter(Bill.id == bill_id).first()
            if bill:
                session.delete(bill)
                session.commit()
                try:
                    self._invalidate_user_caches(bill.user_id)
                    self._warm_caches_async(bill.user_id)
                except Exception:
                    pass
                return True
            return False

    # 列表总数计算（供接口使用）
    def get_bills_total(self, user_id: int = 1, merchant: Optional[str] = None,
                        category: Optional[str] = None, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> int:
        with get_db_session() as session:
            query = session.query(Bill).filter(Bill.user_id == user_id)
            if merchant:
                query = query.filter(Bill.merchant.like(f"%{merchant}%"))
            if category:
                query = query.filter(Bill.category == category)
            if start_date:
                query = query.filter(Bill.consume_time >= start_date)
            if end_date:
                query = query.filter(Bill.consume_time <= end_date)
            return query.count()
    
    # 发票相关操作
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Invoice:
        """创建发票记录"""
        with get_db_session() as session:
            invoice = Invoice(**invoice_data)
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            return invoice
    
    def get_invoices(self, user_id: int = 1, limit: int = 100) -> List[Invoice]:
        """获取发票列表"""
        with get_db_session() as session:
            return session.query(Invoice).filter(Invoice.user_id == user_id)\
                .order_by(Invoice.invoice_time.desc())\
                .limit(limit).all()
    
    # 统计分析
    def get_spending_summary(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """获取消费汇总统计"""
        # 缓存键
        cache_key = f"summary:{user_id}:{start_date.isoformat() if start_date else ''}:{end_date.isoformat() if end_date else ''}"
        now_ts = time.time()
        cached = self._summary_cache.get(cache_key)
        if cached and (now_ts - cached['ts'] <= self._cache_ttl_seconds):
            return cached['data']

        with get_db_session() as session:
            query = session.query(Bill).filter(Bill.user_id == user_id)
            
            if start_date:
                query = query.filter(Bill.consume_time >= start_date)
            if end_date:
                query = query.filter(Bill.consume_time <= end_date)
            
            bills = query.all()
            
            if not bills:
                data = {
                    "total_amount": 0,
                    "total_count": 0,
                    "avg_amount": 0,
                    "categories": {},
                    "payment_methods": {}
                }
                self._summary_cache[cache_key] = {"ts": now_ts, "data": data}
                return data
            
            total_amount = sum(bill.amount for bill in bills)
            total_count = len(bills)
            avg_amount = total_amount / total_count if total_count > 0 else 0
            
            # 按类别统计
            categories = {}
            for bill in bills:
                category = bill.category or "未知"
                if category not in categories:
                    categories[category] = {"amount": 0, "count": 0}
                categories[category]["amount"] += bill.amount
                categories[category]["count"] += 1
            
            # 按支付方式统计
            payment_methods = {}
            for bill in bills:
                method = bill.payment_method
                if method not in payment_methods:
                    payment_methods[method] = {"amount": 0, "count": 0}
                payment_methods[method]["amount"] += bill.amount
                payment_methods[method]["count"] += 1
            
            data = {
                "total_amount": total_amount,
                "total_count": total_count,
                "avg_amount": avg_amount,
                "categories": categories,
                "payment_methods": payment_methods
            }
            self._summary_cache[cache_key] = {"ts": now_ts, "data": data}
            return data
    
    def get_monthly_spending(self, user_id: int, year: int) -> List[Dict[str, Any]]:
        """获取月度消费数据"""
        with get_db_session() as session:
            # 使用SQL查询按月统计
            query = text("""
                SELECT 
                    strftime('%m', consume_time) as month,
                    SUM(amount) as total_amount,
                    COUNT(*) as count,
                    AVG(amount) as avg_amount
                FROM bills 
                WHERE user_id = :user_id 
                AND strftime('%Y', consume_time) = :year
                GROUP BY strftime('%m', consume_time)
                ORDER BY month
            """)
            
            result = session.execute(query, {"user_id": user_id, "year": str(year)})
            return [{"month": row[0], "total_amount": row[1], "count": row[2], "avg_amount": row[3]} 
                   for row in result.fetchall()]
    
    def get_category_spending(self, user_id: int, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
        """获取分类消费数据"""
        cache_key = f"category:{user_id}:{start_date.isoformat() if start_date else ''}:{end_date.isoformat() if end_date else ''}"
        now_ts = time.time()
        cached = self._category_cache.get(cache_key)
        if cached and (now_ts - cached['ts'] <= self._cache_ttl_seconds):
            return cached['data']

        with get_db_session() as session:
            query = session.query(Bill.category, 
                                func.sum(Bill.amount).label('total_amount'),
                                func.count(Bill.id).label('count'),
                                func.avg(Bill.amount).label('avg_amount'))\
                .filter(Bill.user_id == user_id)
            
            if start_date:
                query = query.filter(Bill.consume_time >= start_date)
            if end_date:
                query = query.filter(Bill.consume_time <= end_date)
            
            result = query.group_by(Bill.category).all()
            
            data = [{
                "category": row[0] or "未知",
                "total_amount": float(row[1]),
                "count": row[2],
                "avg_amount": float(row[3])
            } for row in result]
            self._category_cache[cache_key] = {"ts": now_ts, "data": data}
            return data

    # 缓存维护
    def _invalidate_user_caches(self, user_id: int) -> None:
        with self._lock:
            self._summary_cache = {k: v for k, v in self._summary_cache.items() if not k.startswith(f"summary:{user_id}:")}
            self._category_cache = {k: v for k, v in self._category_cache.items() if not k.startswith(f"category:{user_id}:")}

    def _warm_caches_async(self, user_id: int) -> None:
        t = threading.Thread(target=self._warm_caches, args=(user_id,), daemon=True)
        t.start()

    def _warm_caches(self, user_id: int) -> None:
        try:
            # 预热常用窗口（近30天）
            end = datetime.now()
            start = end - timedelta(days=30)
            _ = self.get_spending_summary(user_id, start, end)
            _ = self.get_category_spending(user_id, start, end)
        except Exception:
            pass
    
    # 金融产品相关
    def create_financial_product(self, product_data: Dict[str, Any]) -> FinancialProduct:
        """创建金融产品"""
        with get_db_session() as session:
            product = FinancialProduct(**product_data)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
    
    def get_financial_products(self, product_type: str = None) -> List[FinancialProduct]:
        """获取金融产品列表"""
        with get_db_session() as session:
            query = session.query(FinancialProduct)
            if product_type:
                query = query.filter(FinancialProduct.product_type == product_type)
            return query.all()
    
    # 用户画像相关
    def create_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """创建用户画像"""
        with get_db_session() as session:
            profile = UserProfile(**profile_data)
            session.add(profile)
            session.commit()
            session.refresh(profile)
            return profile
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """获取用户画像"""
        with get_db_session() as session:
            return session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> Optional[UserProfile]:
        """更新用户画像"""
        with get_db_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if profile:
                for key, value in update_data.items():
                    setattr(profile, key, value)
                session.commit()
                session.refresh(profile)
                return profile
            return None

    # 预算相关操作
    def create_budget(self, budget_data: Dict[str, Any]) -> UserBudget:
        """创建预算"""
        with get_db_session() as session:
            budget = UserBudget(**budget_data)
            session.add(budget)
            session.commit()
            session.refresh(budget)
            return {
                "id": budget.id,
                "user_id": budget.user_id,
                "category": budget.category,
                "monthly_budget": float(budget.monthly_budget or 0),
                "current_spent": float(budget.current_spent or 0),
                "alert_threshold": float(budget.alert_threshold or 0),
            }

    def get_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户预算列表"""
        with get_db_session() as session:
            rows = session.query(UserBudget).filter(UserBudget.user_id == user_id).all()
            return [
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "category": row.category,
                    "monthly_budget": float(row.monthly_budget or 0),
                    "current_spent": float(row.current_spent or 0),
                    "alert_threshold": float(row.alert_threshold or 0),
                }
                for row in rows
            ]

    def get_budget_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """获取预算预警"""
        with get_db_session() as session:
            budgets = session.query(UserBudget).filter(UserBudget.user_id == user_id).all()
            alerts = []
            for budget in budgets:
                usage_ratio = budget.current_spent / budget.monthly_budget if budget.monthly_budget > 0 else 0
                if usage_ratio >= budget.alert_threshold:
                    alerts.append({
                        "budget_id": budget.id,
                        "category": budget.category,
                        "monthly_budget": budget.monthly_budget,
                        "current_spent": budget.current_spent,
                        "usage_ratio": usage_ratio,
                        "alert_threshold": budget.alert_threshold
                    })
            return alerts

    # 社区帖子相关操作
    def create_post(self, post_data: Dict[str, Any]) -> CommunityPost:
        """创建帖子"""
        with get_db_session() as session:
            post = CommunityPost(**post_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            return post

    def get_posts(self, limit: int = 20, offset: int = 0) -> List[CommunityPost]:
        """获取帖子列表"""
        with get_db_session() as session:
            return session.query(CommunityPost).order_by(CommunityPost.created_at.desc()).offset(offset).limit(limit).all()

    def like_post(self, post_id: int, user_id: int) -> bool:
        """点赞帖子"""
        with get_db_session() as session:
            # 检查是否已点赞
            existing = session.query(PostLike).filter(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            ).first()
            if existing:
                return False  # 已点赞
            
            # 添加点赞
            like = PostLike(post_id=post_id, user_id=user_id)
            session.add(like)
            
            # 更新帖子点赞数
            post = session.query(CommunityPost).filter(CommunityPost.id == post_id).first()
            if post:
                post.likes_count = (post.likes_count or 0) + 1
            
            session.commit()
            return True

    def create_comment(self, comment_data: Dict[str, Any]) -> PostComment:
        """创建评论"""
        with get_db_session() as session:
            comment = PostComment(**comment_data)
            session.add(comment)
            
            # 更新帖子评论数
            post = session.query(CommunityPost).filter(CommunityPost.id == comment_data['post_id']).first()
            if post:
                post.comments_count = (post.comments_count or 0) + 1
            
            session.commit()
            session.refresh(comment)
            return comment

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        default = {
            "user_id": user_id,
            "city": "",
            "job": "",
            "budget_cycle": "monthly",
            "notify_budget": True,
            "notify_insight": True,
            "notify_community": True,
            "updated_at": datetime.now()
        }
        with get_db_session() as session:
            pref = session.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            if not pref:
                return default
            return {
                "user_id": pref.user_id,
                "city": pref.city or "",
                "job": pref.job or "",
                "budget_cycle": pref.budget_cycle or "monthly",
                "notify_budget": bool(pref.notify_budget),
                "notify_insight": bool(pref.notify_insight),
                "notify_community": bool(pref.notify_community),
                "updated_at": pref.updated_at or datetime.now()
            }

    def upsert_user_preferences(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新或创建用户偏好设置"""
        payload = {
            "city": data.get("city", ""),
            "job": data.get("job", ""),
            "budget_cycle": data.get("budget_cycle", "monthly"),
            "notify_budget": 1 if data.get("notify_budget", True) else 0,
            "notify_insight": 1 if data.get("notify_insight", True) else 0,
            "notify_community": 1 if data.get("notify_community", True) else 0,
        }
        with get_db_session() as session:
            pref = session.query(UserPreference).filter(UserPreference.user_id == user_id).first()
            if pref:
                for key, value in payload.items():
                    setattr(pref, key, value)
                session.commit()
                session.refresh(pref)
            else:
                pref = UserPreference(user_id=user_id, **payload)
                session.add(pref)
                session.commit()
                session.refresh(pref)
            return {
                "user_id": pref.user_id,
                "city": pref.city or "",
                "job": pref.job or "",
                "budget_cycle": pref.budget_cycle or "monthly",
                "notify_budget": bool(pref.notify_budget),
                "notify_insight": bool(pref.notify_insight),
                "notify_community": bool(pref.notify_community),
                "updated_at": pref.updated_at or datetime.now()
            }

    def create_user_request(self, user_id: int, request_type: str, detail: str = "") -> UserRequestLog:
        """记录用户导出/注销等申请"""
        with get_db_session() as session:
            req = UserRequestLog(
                user_id=user_id,
                request_type=request_type,
                detail=detail,
                status="pending"
            )
            session.add(req)
            session.commit()
            session.refresh(req)
            return req

# 创建全局数据库管理器实例
db_manager = DatabaseManager()
