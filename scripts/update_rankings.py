"""
榜单更新定时任务脚本
每2小时执行一次，更新商家排名数据
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.merchant_service import merchant_service
from src.config import RANKING_CONFIG
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'ranking_update.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """执行榜单更新"""
    try:
        logger.info("开始更新商家榜单...")
        result = merchant_service.update_rankings(period_days=30)
        
        if result.get('success'):
            logger.info(f"榜单更新成功: 更新了 {result.get('updated_count', 0)} 个商家")
            logger.info(f"统计周期: {result.get('period_start')} 至 {result.get('period_end')}")
        else:
            logger.error(f"榜单更新失败: {result.get('error')}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"榜单更新异常: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

