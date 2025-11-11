"""
预警服务：统一风险评估、事件落库与结果结构化输出
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import sqlite3

try:
    from ..config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH


RiskLevel = str  # 'high' | 'medium' | 'low'


class AlertService:
    def __init__(self):
        pass

    def _get_user_prefs(self, user_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alert_prefs WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {
                "threshold_high": 0.8,
                "threshold_medium": 0.5,
                "channel_email": 1,
                "channel_sms": 0,
                "channel_wecom": 1,
                "channel_wechat_mp": 0,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "07:00",
                "break_quiet_for_high": 1,
                "rate_limit_per_hour": 5
            }
        return dict(row)

    def _score_rules(self, bill: Dict[str, Any], recent_bills: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        规则打分：返回风险分(0-1)与证据列表
        """
        evidence = []
        score = 0.0

        amount = float(bill.get('amount', 0) or 0)
        if amount >= 1000:
            score += 0.4
            evidence.append({
                "type": "large_amount",
                "message": f"单笔消费金额较大：¥{amount:.2f}"
            })

        # 近1小时频次与金额
        recent_count = 0
        recent_total = 0.0
        now = datetime.now()
        for b in recent_bills or []:
            t = b.get('consume_time')
            try:
                if isinstance(t, str):
                    from datetime import datetime as dt
                    tt = dt.fromisoformat(t.replace(' ', 'T'))
                else:
                    tt = t
                if (now - tt).total_seconds() < 3600:
                    recent_count += 1
                    recent_total += float(b.get('amount', 0) or 0)
            except Exception:
                continue

        if recent_count >= 5:
            score += 0.3
            evidence.append({
                "type": "frequent_transactions",
                "message": f"1小时内消费笔数较多：{recent_count}笔"
            })
        if recent_total >= 2000:
            score += 0.2
            evidence.append({
                "type": "high_frequency_amount",
                "message": f"1小时内消费总额较高：¥{recent_total:.2f}"
            })

        # 类别异常（简单示例）
        abnormal_categories = {"未知", "其他"}
        category = bill.get("category") or "未知"
        if category in abnormal_categories and amount >= 300:
            score += 0.1
            evidence.append({
                "type": "abnormal_category",
                "message": f"类别为{category}且金额较高"
            })

        return min(score, 1.0), evidence

    def _level_from_score(self, score: float, prefs: Dict[str, Any]) -> RiskLevel:
        if score >= float(prefs.get("threshold_high", 0.8)):
            return "high"
        if score >= float(prefs.get("threshold_medium", 0.5)):
            return "medium"
        return "low"

    def evaluate_bill(self, user_id: int, bill: Dict[str, Any], recent_bills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对单笔账单进行风险评估，返回结构化结果（不落库）
        """
        prefs = self._get_user_prefs(user_id)
        score, evidence = self._score_rules(bill, recent_bills)
        level = self._level_from_score(score, prefs)

        title = "消费风险预警" if level != "low" else "消费提醒"
        reason = f"综合规则评分={score:.2f}，阈值(H={prefs.get('threshold_high')}, M={prefs.get('threshold_medium')})"

        return {
            "level": level,
            "score": score,
            "title": title,
            "reason": reason,
            "evidence": evidence,
            "prefs": prefs
        }

    def create_event(self, user_id: int, bill_id: Optional[int], result: Dict[str, Any], event_type: str = "rules") -> int:
        """
        将评估结果写入 alert_events，返回 event_id
        """
        conn = sqlite3.connect(str(DATABASE_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alert_events (user_id, bill_id, level, event_type, title, reason, evidence, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', datetime('now'))
        """, (
            user_id,
            bill_id,
            result.get("level"),
            event_type,
            result.get("title"),
            result.get("reason"),
            json.dumps(result.get("evidence") or [], ensure_ascii=False)
        ))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id


alert_service = AlertService()

