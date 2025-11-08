"""
兼容性查询工具 - 解决 SQLAlchemy 线程会话失效问题

提供若干轻量级的直接 SQLite 查询函数，供 FastAPI 接口快速读取统计数据。
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from .config import DATABASE_PATH
except ImportError:  # pragma: no cover
    from config import DATABASE_PATH


def _dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    """将 sqlite3.Row 转换为普通字典。"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def _get_connection() -> sqlite3.Connection:
    """创建带行工厂的数据库连接。"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = _dict_factory
    try:
        yield conn
    finally:
        conn.close()


def _normalize_datetime(value: Any) -> str:
    """将 datetime 对象统一转换为字符串表示。"""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value) if value is not None else ""


def get_bills_simple(
    user_id: int = 1,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    获取账单列表，返回字典列表。

    该方法避免了 SQLAlchemy Session 在多线程中的失效问题。
    """
    query = (
        "SELECT id, user_id, consume_time, amount, merchant, category, "
        "payment_method, location, description, created_at, updated_at "
        "FROM bills WHERE user_id = ? "
        "ORDER BY datetime(consume_time) DESC, id DESC "
        "LIMIT ? OFFSET ?"
    )
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (user_id, limit, offset))
        rows = cur.fetchall()

    # 统一时间格式，确保上层逻辑可直接解析
    for row in rows:
        row["consume_time"] = _normalize_datetime(row.get("consume_time"))
        row["created_at"] = _normalize_datetime(row.get("created_at"))
        row["updated_at"] = _normalize_datetime(row.get("updated_at"))
    return rows


def get_bill_by_id(bill_id: int) -> Optional[Dict[str, Any]]:
    """根据账单 ID 返回单条记录。"""
    query = (
        "SELECT id, user_id, consume_time, amount, merchant, category, "
        "payment_method, location, description, created_at, updated_at "
        "FROM bills WHERE id = ? LIMIT 1"
    )
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (bill_id,))
        row = cur.fetchone()

    if not row:
        return None

    row["consume_time"] = _normalize_datetime(row.get("consume_time"))
    row["created_at"] = _normalize_datetime(row.get("created_at"))
    row["updated_at"] = _normalize_datetime(row.get("updated_at"))
    return row


def create_bill_simple(bill_data: Dict[str, Any]) -> int:
    """
    直接写入账单记录，返回插入的 ID。

    仅用于兜底场景，主流程仍推荐使用 SQLAlchemy 数据模型。
    """
    payload = bill_data.copy()
    consume_time = payload.get("consume_time")
    if consume_time:
        payload["consume_time"] = _normalize_datetime(consume_time)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload.setdefault("created_at", now)
    payload.setdefault("updated_at", now)

    columns = ", ".join(payload.keys())
    placeholders = ", ".join(["?"] * len(payload))
    values = list(payload.values())

    query = f"INSERT INTO bills ({columns}) VALUES ({placeholders})"

    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, values)
        conn.commit()
        return cur.lastrowid


def get_spending_summary_simple(user_id: int = 1) -> Dict[str, Any]:
    """
    统计用户消费概要信息。

    返回结构与 database.db_manager.get_spending_summary 保持一致。
    """
    summary_query = (
        "SELECT "
        "COUNT(*) AS total_count, "
        "COALESCE(SUM(amount), 0) AS total_amount, "
        "COALESCE(AVG(amount), 0) AS avg_amount "
        "FROM bills WHERE user_id = ?"
    )
    category_query = (
        "SELECT COALESCE(category, '未知') AS category, "
        "COALESCE(SUM(amount), 0) AS total_amount, "
        "COUNT(*) AS count "
        "FROM bills WHERE user_id = ? GROUP BY COALESCE(category, '未知')"
    )
    payment_query = (
        "SELECT COALESCE(payment_method, '其他') AS payment_method, "
        "COALESCE(SUM(amount), 0) AS total_amount, "
        "COUNT(*) AS count "
        "FROM bills WHERE user_id = ? GROUP BY COALESCE(payment_method, '其他')"
    )

    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(summary_query, (user_id,))
        summary_row = cur.fetchone() or {"total_count": 0, "total_amount": 0, "avg_amount": 0}

        cur.execute(category_query, (user_id,))
        category_rows = cur.fetchall()

        cur.execute(payment_query, (user_id,))
        payment_rows = cur.fetchall()

    categories: Dict[str, Dict[str, Any]] = {}
    for row in category_rows:
        categories[row["category"]] = {
            "amount": float(row["total_amount"] or 0),
            "count": int(row["count"] or 0),
        }

    payment_methods: Dict[str, Dict[str, Any]] = {}
    for row in payment_rows:
        key = row["payment_method"]
        payment_methods[key] = {
            "amount": float(row["total_amount"] or 0),
            "count": int(row["count"] or 0),
        }

    return {
        "total_amount": float(summary_row.get("total_amount") or 0),
        "total_count": int(summary_row.get("total_count") or 0),
        "avg_amount": float(summary_row.get("avg_amount") or 0),
        "categories": categories,
        "payment_methods": payment_methods,
    }

