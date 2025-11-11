"""
数据库访问工具模块
统一数据库连接和操作接口
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from ..config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = None
    try:
        conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 返回字典格式的结果
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


class DatabaseManager:
    """数据库管理器，提供统一的数据库操作接口"""
    
    @staticmethod
    def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行查询，返回结果列表"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def execute_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """执行查询，返回单条结果"""
        results = DatabaseManager.execute_query(query, params)
        return results[0] if results else None
    
    @staticmethod
    def execute_update(query: str, params: tuple = ()) -> int:
        """执行更新操作，返回受影响的行数"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    @staticmethod
    def execute_insert(query: str, params: tuple = ()) -> int:
        """执行插入操作，返回插入行的ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    @staticmethod
    def execute_many(query: str, params_list: List[tuple]) -> int:
        """批量执行操作"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount


# 全局数据库管理器实例
db = DatabaseManager()

