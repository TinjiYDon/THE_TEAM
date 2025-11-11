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

# 支付配置
PAYMENT_CONFIG = {
    "wechat": {
        "app_id": os.getenv("WECHAT_APP_ID", ""),
        "mch_id": os.getenv("WECHAT_MCH_ID", ""),
        "api_key": os.getenv("WECHAT_API_KEY", ""),
        "cert_path": os.getenv("WECHAT_CERT_PATH", ""),
        "notify_url": os.getenv("WECHAT_NOTIFY_URL", f"http://{HOST}:{PORT}{API_V1_PREFIX}/payment/wechat/notify")
    },
    "alipay": {
        "app_id": os.getenv("ALIPAY_APP_ID", ""),
        "private_key": os.getenv("ALIPAY_PRIVATE_KEY", ""),
        "public_key": os.getenv("ALIPAY_PUBLIC_KEY", ""),
        "notify_url": os.getenv("ALIPAY_NOTIFY_URL", f"http://{HOST}:{PORT}{API_V1_PREFIX}/payment/alipay/notify")
    }
}

# 高德地图配置（预留）
AMAP_CONFIG = {
    "api_key": os.getenv("AMAP_API_KEY", ""),  # 高德地图API密钥
    "web_api_key": os.getenv("AMAP_WEB_API_KEY", ""),  # Web端API密钥
    "js_api_key": os.getenv("AMAP_JS_API_KEY", ""),  # JS API密钥
    "base_url": "https://restapi.amap.com/v3"
}

# 商家榜单配置
RANKING_CONFIG = {
    "update_interval_hours": 2,  # 榜单更新间隔（小时）
    "sponsor_display_count": 40,  # 赞助商家最多显示数量
    "sponsor_per_page": 10,  # 每页显示赞助商家数量
    "layout_ratio": 0.618,  # 黄金分割比（左侧热门商家占比）
    "min_bid_amount": 100.0,  # 最低竞价金额（第一周）
    "default_cpc_price": 1.0,  # 默认CPC单价（第二周起）
    "min_daily_budget": 50.0,  # 最低每日预算
    "max_daily_budget": 500.0,  # 最高每日预算
    "cpc_price_by_category": {  # 按类别设置CPC单价
        "餐饮": 1.5,
        "购物": 1.2,
        "娱乐": 1.0,
        "医疗": 2.0,
        "教育": 1.8,
        "其他": 0.8
    }
}

# 防刷检测配置
ANTI_FRAUD_CONFIG = {
    "click_rate_limit": 10,  # 单IP每分钟最大点击次数
    "device_fingerprint_enabled": True,  # 启用设备指纹
    "ip_whitelist": [],  # IP白名单
    "risk_score_threshold": 0.7,  # 风险分数阈值（超过此值标记为可疑）
    "auto_block_enabled": True,  # 自动封禁可疑点击
    "review_required_score": 0.5  # 需要人工审核的风险分数阈值
}

# 商家认证配置
MERCHANT_VERIFICATION_CONFIG = {
    "required_fields": ["merchant_name", "business_license", "category"],
    "license_image_required": True,
    "auto_approve": False,  # 是否自动审核（生产环境建议False）
    "verification_timeout_hours": 48  # 审核超时时间（小时）
}

# 反馈配置
FEEDBACK_CONFIG = {
    "admin_email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
    "auto_reply_enabled": True,  # 是否自动回复
    "notification_enabled": True,  # 是否发送邮件通知
    # SMTP可选配置（用于通知/反馈邮件）
    "smtp_host": os.getenv("SMTP_HOST", ""),
    "smtp_port": int(os.getenv("SMTP_PORT", "465")),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_pass": os.getenv("SMTP_PASS", ""),
    "from_email": os.getenv("FROM_EMAIL", os.getenv("SMTP_USER", "")),
}

# 确保日志目录存在
(BASE_DIR / "logs").mkdir(exist_ok=True)

# 通知配置（企业微信、公众号等）
NOTIFY_CONFIG = {
    "wecom_webhook": os.getenv("WECOM_WEBHOOK", ""),  # 企业微信群机器人Webhook
    # 预留微信公众平台等后续接入
}
