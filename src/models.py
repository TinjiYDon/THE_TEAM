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
