"""
API v1 路由模块
"""
from fastapi import APIRouter

# 创建主路由器
api_router = APIRouter()

# 导入各个子路由（延迟导入避免循环依赖）
def register_routes():
    """注册所有路由"""
    from . import merchants, rankings, feedback, alerts, settings
    
    api_router.include_router(merchants.router, tags=["merchants"])
    api_router.include_router(rankings.router, tags=["rankings"])
    api_router.include_router(feedback.router, tags=["feedback"])
    api_router.include_router(alerts.router, tags=["alerts"])
    api_router.include_router(settings.router, tags=["settings"])

