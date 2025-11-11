"""
日志工具模块
统一日志配置和管理
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

try:
    from ..config import LOG_CONFIG, BASE_DIR
except ImportError:
    from config import LOG_CONFIG, BASE_DIR

def setup_logger(name: str = "app", level: str = None) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别（如不提供，使用配置中的级别）
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = level or LOG_CONFIG.get("level", "INFO")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 日志格式
    formatter = logging.Formatter(
        LOG_CONFIG.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（带轮转）
    log_file = LOG_CONFIG.get("file") or (BASE_DIR / "logs" / "app.log")
    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# 全局日志记录器
app_logger = setup_logger("app")
merchant_logger = setup_logger("merchant")
analytics_logger = setup_logger("analytics")
fraud_logger = setup_logger("fraud")

