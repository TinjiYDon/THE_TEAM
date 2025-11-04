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
EXPORTS_DIR = BASE_DIR / "data" / "exports"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

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

# 洞察阈值（可被接口/环境覆盖）
INSIGHT_DEFAULTS = {
    "period_days": int(os.getenv("INSIGHT_PERIOD_DAYS", 90)),
    "dining_share_threshold": float(os.getenv("INSIGHT_DINING_SHARE", 0.35)),
    "dining_min_count": int(os.getenv("INSIGHT_DINING_MIN_COUNT", 10)),
    "top1_lead_threshold": float(os.getenv("INSIGHT_TOP1_LEAD", 0.20)),
}

# 管理配置（演示）
ADMIN_CONFIG = {
    "auto_approve_groups": os.getenv("AUTO_APPROVE_GROUPS", "true").lower() == "true",
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "app.log"
}

# 确保日志目录存在
(BASE_DIR / "logs").mkdir(exist_ok=True)
