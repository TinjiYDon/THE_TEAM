"""
预警API：查询预警、标记已读/忽略、触发测试
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

try:
    from ...config import DATABASE_PATH
    from ...services.alert_service import alert_service
except ImportError:
    from config import DATABASE_PATH
    from services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(user_id: int = 1, level: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if level:
            cursor.execute("""
                SELECT * FROM alert_events
                WHERE user_id = ? AND level = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, level, limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM alert_events
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return {"success": True, "data": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")


class UpdateStatusRequest(BaseModel):
    status: str  # read/ignored


@router.post("/{event_id}/status")
async def update_alert_status(event_id: int, req: UpdateStatusRequest, user_id: int = 1):
    try:
        if req.status not in {"read", "ignored"}:
            raise HTTPException(status_code=400, detail="状态非法")
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alert_events
            SET status = ?, updated_at = datetime('now')
            WHERE id = ? AND user_id = ?
        """, (req.status, event_id, user_id))
        conn.commit()
        conn.close()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警状态失败: {str(e)}")


