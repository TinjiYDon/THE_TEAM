"""
统一异常处理模块
定义自定义异常类和异常处理函数
"""
from typing import Optional


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, code: int, message: str, detail: Optional[str] = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource}不存在"
        if resource_id:
            message = f"{resource}(ID: {resource_id})不存在"
        super().__init__(404, message)


class ValidationException(BusinessException):
    """数据验证异常"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(400, message, detail)


class UnauthorizedException(BusinessException):
    """未授权异常"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(401, message)


class ForbiddenException(BusinessException):
    """禁止访问异常"""
    def __init__(self, message: str = "禁止访问"):
        super().__init__(403, message)


class ConflictException(BusinessException):
    """资源冲突异常"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(409, message, detail)


class MerchantNotFoundException(NotFoundException):
    """商家不存在异常"""
    def __init__(self, merchant_id: Optional[int] = None):
        super().__init__("商家", str(merchant_id) if merchant_id else None)


class MerchantAlreadyExistsException(ConflictException):
    """商家已存在异常"""
    def __init__(self):
        super().__init__("您已经认证过商家")


class PaymentException(BusinessException):
    """支付异常"""
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(400, message, detail)


class FraudDetectionException(BusinessException):
    """防刷检测异常"""
    def __init__(self, message: str = "检测到可疑行为", detail: Optional[str] = None):
        super().__init__(403, message, detail)

