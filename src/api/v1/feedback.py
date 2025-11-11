"""
反馈相关API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3

try:
    from ...config import DATABASE_PATH, FEEDBACK_CONFIG
except ImportError:
    from config import DATABASE_PATH, FEEDBACK_CONFIG

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    feedback_type: str  # function/merchant_info/shop_info/suggestion
    title: Optional[str] = None
    content: str
    contact_email: Optional[EmailStr] = None


@router.post("")
async def submit_feedback(request: FeedbackRequest, user_id: Optional[int] = None):
    """提交用户反馈"""
    try:
        # 保存反馈到数据库
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_feedbacks
            (user_id, feedback_type, title, content, contact_email, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', datetime('now'))
        """, (user_id, request.feedback_type, request.title, 
              request.content, request.contact_email))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 发送邮件通知（如果配置了）
        if FEEDBACK_CONFIG.get("notification_enabled") and FEEDBACK_CONFIG.get("admin_email"):
            try:
                # TODO: 配置SMTP服务器发送邮件
                # 这里只是占位符，实际需要配置SMTP
                pass
            except Exception as e:
                print(f"发送反馈邮件失败: {e}")
        
        return {
            "success": True,
            "message": "反馈已提交，感谢您的建议",
            "feedback_id": feedback_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")

