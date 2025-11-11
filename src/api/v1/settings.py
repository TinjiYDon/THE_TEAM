"""
预警设置API：查询与保存用户预警偏好
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

try:
    from ...config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH

router = APIRouter(prefix="/settings", tags=["settings"])


class AlertPrefsRequest(BaseModel):
    threshold_high: Optional[float] = 0.8
    threshold_medium: Optional[float] = 0.5
    channel_email: Optional[bool] = True
    channel_sms: Optional[bool] = False
    channel_wecom: Optional[bool] = True
    channel_wechat_mp: Optional[bool] = False
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "07:00"
    break_quiet_for_high: Optional[bool] = True
    rate_limit_per_hour: Optional[int] = 5


@router.get("/alert_prefs")
async def get_alert_prefs(user_id: int = 1):
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alert_prefs WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {"success": True, "data": None}
        return {"success": True, "data": dict(row)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警偏好失败: {str(e)}")


@router.post("/alert_prefs")
async def save_alert_prefs(req: AlertPrefsRequest, user_id: int = 1):
    try:
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alert_prefs
            (user_id, threshold_high, threshold_medium, channel_email, channel_sms, channel_wecom, channel_wechat_mp,
             quiet_hours_start, quiet_hours_end, break_quiet_for_high, rate_limit_per_hour, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                threshold_high=excluded.threshold_high,
                threshold_medium=excluded.threshold_medium,
                channel_email=excluded.channel_email,
                channel_sms=excluded.channel_sms,
                channel_wecom=excluded.channel_wecom,
                channel_wechat_mp=excluded.channel_wechat_mp,
                quiet_hours_start=excluded.quiet_hours_start,
                quiet_hours_end=excluded.quiet_hours_end,
                break_quiet_for_high=excluded.break_quiet_for_high,
                rate_limit_per_hour=excluded.rate_limit_per_hour,
                updated_at=datetime('now')
        """, (
            user_id,
            req.threshold_high, req.threshold_medium,
            1 if req.channel_email else 0,
            1 if req.channel_sms else 0,
            1 if req.channel_wecom else 0,
            1 if req.channel_wechat_mp else 0,
            req.quiet_hours_start, req.quiet_hours_end,
            1 if req.break_quiet_for_high else 0,
            req.rate_limit_per_hour
        ))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存预警偏好失败: {str(e)}")


