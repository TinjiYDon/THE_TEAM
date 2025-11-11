"""
异常处理中间件
统一处理应用中的异常
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from ..utils.exceptions import BusinessException
except ImportError:
    from utils.exceptions import BusinessException


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    return JSONResponse(
        status_code=exc.code,
        content={
            "success": False,
            "detail": exc.message,
            "error_code": exc.code,
            "error_detail": exc.detail
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "error_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "")
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "请求参数验证失败",
            "errors": error_messages,
            "error_code": 422
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理（兜底）"""
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    
    # 生产环境不返回详细错误信息
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": "服务器内部错误",
            "error_code": 500
        }
    )

