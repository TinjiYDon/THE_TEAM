"""
配置文件 - 统一管理所有配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/bill_db.sqlite"
DATABASE_PATH = BASE_DIR / "data" / "bill_db.sqlite"

# 数据目录
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "data" / "models"
TEST_DATA_DIR = BASE_DIR / "data" / "test_data"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)

# API配置
API_V1_PREFIX = "/api/v1"
HOST = "0.0.0.0"
PORT = 8000

# 数据清洗配置
CLEANING_CONFIG = {
    "min_amount": 0.01,  # 最小金额
    "max_amount": 1000000,  # 最大金额
    "date_format": "%Y-%m-%d %H:%M:%S",
    "categories": ["餐饮", "交通", "购物", "娱乐", "医疗", "教育", "其他"],
    "payment_methods": ["微信", "支付宝", "银行卡", "现金", "其他"]
}

# AI模型配置
AI_CONFIG = {
    "nlp_model": "jieba",
    "recommendation_algorithm": "collaborative_filtering",
    "user_profile_features": ["spending_pattern", "category_preference", "amount_range"],
    "min_samples_for_training": 10
}

# 图表配置
CHART_CONFIG = {
    "default_colors": ["#1890ff", "#52c41a", "#faad14", "#f5222d", "#722ed1"],
    "chart_types": ["pie", "bar", "line", "radar", "funnel", "box"],
    "interactive": True
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "app.log"
}

# 确保日志目录存在
(BASE_DIR / "logs").mkdir(exist_ok=True)
