"""
数据模型定义
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Bill(Base):
    """账单表"""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)
    consume_time = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String(255), nullable=False)
    category = Column(String(50), default="未知")
    payment_method = Column(String(50), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Invoice(Base):
    """发票表"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, default=1)
    invoice_time = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String(255), nullable=False)
    invoice_type = Column(String(50), default="未知")
    ocr_text = Column(Text)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())

class FinancialProduct(Base):
    """金融产品表"""
    __tablename__ = "financial_products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_type = Column(String(50), nullable=False)  # 理财/贷款/保险
    product_name = Column(String(255), nullable=False)
    interest_rate = Column(Float)
    min_amount = Column(Float)
    max_amount = Column(Float)
    term_months = Column(Integer)
    risk_level = Column(String(20))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class UserProfile(Base):
    """用户画像表"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    income_level = Column(String(20))
    spending_pattern = Column(JSON)  # 存储消费模式JSON
    risk_tolerance = Column(String(20))
    investment_preference = Column(JSON)  # 存储投资偏好JSON
    credit_score = Column(Integer)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserBudget(Base):
    """用户预算表"""
    __tablename__ = "user_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category = Column(String(50))
    monthly_budget = Column(Float, nullable=False)
    current_spent = Column(Float, default=0.0)
    alert_threshold = Column(Float, default=0.8)  # 80%触发预警
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class UserSubscription(Base):
    """用户订阅表"""
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subscription_type = Column(String(50), default="free")  # free/premium
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    is_active = Column(Integer, default=1)  # 1=active, 0=expired
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class OCRUsageQuota(Base):
    """OCR使用配额表"""
    __tablename__ = "ocr_usage_quota"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    used_at = Column(DateTime, nullable=False)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

class CommunityPost(Base):
    """社区帖子表"""
    __tablename__ = "community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    bill_id = Column(Integer)  # 关联的账单ID
    invoice_id = Column(Integer)  # 关联的发票ID
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PostComment(Base):
    """帖子评论表"""
    __tablename__ = "post_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PostLike(Base):
    """帖子点赞表"""
    __tablename__ = "post_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())


class UserPreference(Base):
    """用户偏好设置表"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    city = Column(String(100), default="")
    job = Column(String(100), default="")
    budget_cycle = Column(String(50), default="monthly")
    notify_budget = Column(Integer, default=1)  # 1=on, 0=off
    notify_insight = Column(Integer, default=1)
    notify_community = Column(Integer, default=1)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserRequestLog(Base):
    """用户操作申请记录（导出/注销等）"""
    __tablename__ = "user_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    request_type = Column(String(50), nullable=False)  # export/deactivate
    status = Column(String(20), default="pending")  # pending/done/rejected
    detail = Column(Text)
    created_at = Column(DateTime, default=func.now())


class Merchant(Base):
    """商家表"""
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True)
    merchant_name = Column(String(255), nullable=False)
    business_license = Column(String(100))
    license_image_path = Column(String(500))
    category = Column(String(50))
    status = Column(String(20), default="pending")  # pending/approved/rejected
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MerchantInfo(Base):
    """商家详细信息表"""
    __tablename__ = "merchant_info"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False, unique=True)
    description = Column(Text)
    address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(20))
    business_hours = Column(Text)  # JSON格式
    images = Column(Text)  # JSON数组
    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MerchantRanking(Base):
    """商家排名数据表"""
    __tablename__ = "merchant_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False)
    merchant_name = Column(String(255), nullable=False)
    category = Column(String(50))
    total_consumption_count = Column(Integer, default=0)
    total_consumption_amount = Column(Float, default=0.0)
    ranking_score = Column(Float, default=0.0)
    ranking_position = Column(Integer)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MerchantSponsorship(Base):
    """商家赞助记录表"""
    __tablename__ = "merchant_sponsorships"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False)
    sponsorship_type = Column(String(20), default="bidding")  # bidding/cpc
    bid_amount = Column(Float, default=0.0)
    cpc_price = Column(Float, default=0.0)
    daily_budget = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    status = Column(String(20), default="active")  # active/paused/expired
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MerchantClick(Base):
    """商家点击统计表"""
    __tablename__ = "merchant_clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False)
    user_id = Column(Integer)
    click_type = Column(String(20), default="view")  # view/click/detail/navigate
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    referrer = Column(String(500))
    device_fingerprint = Column(String(100))
    is_valid = Column(Integer, default=1)  # 1=valid, 0=invalid
    created_at = Column(DateTime, default=func.now())


class MerchantReview(Base):
    """商家评论表"""
    __tablename__ = "merchant_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    rating = Column(Integer)  # 1-5
    content = Column(Text)
    images = Column(Text)  # JSON数组
    status = Column(String(20), default="pending")  # pending/approved/rejected
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MerchantPayment(Base):
    """支付记录表"""
    __tablename__ = "merchant_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False)
    sponsorship_id = Column(Integer)
    payment_type = Column(String(20), nullable=False)  # wechat/alipay
    amount = Column(Float, nullable=False)
    transaction_id = Column(String(100))
    status = Column(String(20), default="pending")  # pending/success/failed
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class UserFeedback(Base):
    """用户反馈表"""
    __tablename__ = "user_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    feedback_type = Column(String(50), nullable=False)  # function/merchant_info/shop_info/suggestion
    title = Column(String(255))
    content = Column(Text, nullable=False)
    contact_email = Column(String(255))
    status = Column(String(20), default="pending")  # pending/processing/resolved
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class FraudDetectionLog(Base):
    """防刷检测记录表"""
    __tablename__ = "fraud_detection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer)
    detection_type = Column(String(50), nullable=False)  # click_fraud/review_fraud/ranking_manipulation
    suspicious_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)  # 0-1
    action_taken = Column(String(50))  # blocked/flagged/reviewed
    details = Column(Text)  # JSON格式
    created_at = Column(DateTime, default=func.now())