"""
通知服务：支持邮件与企业微信机器人，带简单频控占位
"""
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
import sqlite3
import requests

try:
    from ..config import DATABASE_PATH, FEEDBACK_CONFIG
except ImportError:
    from config import DATABASE_PATH, FEEDBACK_CONFIG


class NotifyService:
    def __init__(self):
        pass

    def _insert_notify_log(self, event_id: int, channel: str, status: str, error: Optional[str] = None):
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notify_logs (event_id, channel, status, error, retry_count, sent_at)
            VALUES (?, ?, ?, ?, 0, datetime('now'))
        """, (event_id, channel, status, error))
        conn.commit()
        conn.close()

    def send_email(self, to_email: str, subject: str, content: str, event_id: Optional[int] = None) -> bool:
        """
        简化版：使用配置中的SMTP，若未配置则直接返回False
        """
        cfg = FEEDBACK_CONFIG or {}
        smtp_host = cfg.get("smtp_host")
        smtp_port = cfg.get("smtp_port", 465)
        smtp_user = cfg.get("smtp_user")
        smtp_pass = cfg.get("smtp_pass")
        from_email = cfg.get("from_email", smtp_user)

        if not (smtp_host and smtp_user and smtp_pass and from_email):
            if event_id:
                self._insert_notify_log(event_id, "email", "failed", "SMTP未配置")
            return False

        try:
            msg = MIMEText(content, "html", "utf-8")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, [to_email], msg.as_string())

            if event_id:
                self._insert_notify_log(event_id, "email", "success")
            return True
        except Exception as e:
            if event_id:
                self._insert_notify_log(event_id, "email", "failed", str(e))
            return False

    def send_wecom(self, webhook_url: str, title: str, content: str, event_id: Optional[int] = None) -> bool:
        """
        企业微信群机器人文本/markdown简单通知
        """
        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"**{title}**\n\n{content}"
                }
            }
            resp = requests.post(webhook_url, json=payload, timeout=5)
            ok = resp.status_code == 200 and resp.json().get("errcode") == 0
            if event_id:
                self._insert_notify_log(event_id, "wecom", "success" if ok else "failed", None if ok else resp.text)
            return ok
        except Exception as e:
            if event_id:
                self._insert_notify_log(event_id, "wecom", "failed", str(e))
            return False


notify_service = NotifyService()

