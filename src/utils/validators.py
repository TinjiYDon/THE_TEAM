"""
数据验证工具模块
提供通用的数据验证函数
"""
import re
from typing import Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证手机号格式（中国大陆）"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_business_license(license_no: str) -> bool:
    """验证经营许可证号格式（简化验证）"""
    # 统一社会信用代码：18位
    # 营业执照号：15位
    # 这里做简化验证，实际应该更严格
    if len(license_no) < 10 or len(license_no) > 20:
        return False
    return license_no.replace('-', '').replace('_', '').isalnum()


def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 1000000) -> bool:
    """验证金额范围"""
    return min_amount <= amount <= max_amount


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """验证日期格式"""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """清理字符串（防止XSS等）"""
    if not text:
        return ""
    # 移除危险字符
    text = text.strip()
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    return text


def format_amount(amount: float, precision: int = 2) -> str:
    """格式化金额"""
    return f"¥{amount:.{precision}f}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if isinstance(dt, str):
        return dt
    return dt.strftime(format_str)

