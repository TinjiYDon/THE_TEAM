"""
埋点统计服务模块
用于记录和统计商家点击、转化等数据
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3
import json

try:
    from .config import DATABASE_PATH
    from .anti_fraud import anti_fraud_detector
except ImportError:
    from config import DATABASE_PATH
    from anti_fraud import anti_fraud_detector


class AnalyticsService:
    """埋点统计服务"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    def track_click(self, merchant_id: int, user_id: Optional[int], 
                   click_type: str, request_headers: Dict) -> Dict:
        """记录点击事件
        
        Args:
            merchant_id: 商家ID
            user_id: 用户ID（可选）
            click_type: 点击类型（view/click/detail/navigate）
            request_headers: 请求头信息（包含IP、User-Agent等）
        
        Returns:
            记录结果，包含是否有效、风险分数等
        """
        try:
            # 提取请求信息
            ip_address = request_headers.get("X-Forwarded-For", request_headers.get("X-Real-IP", ""))
            if ip_address and ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            
            user_agent = request_headers.get("User-Agent", "")
            referrer = request_headers.get("Referer", "")
            
            # 生成设备指纹
            device_fingerprint = anti_fraud_detector.generate_device_fingerprint(user_agent, ip_address)
            
            # 记录点击
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO merchant_clicks 
                (merchant_id, user_id, click_type, ip_address, user_agent, referrer, device_fingerprint, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (merchant_id, user_id, click_type, ip_address, user_agent, referrer, device_fingerprint))
            
            click_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # 异步进行防刷检测（简化版：同步检测）
            fraud_result = anti_fraud_detector.detect_click_fraud(merchant_id, window_minutes=60)
            
            # 如果检测到高风险，标记为无效
            is_valid = 1
            if fraud_result.get("risk_score", 0) >= 0.7:
                is_valid = 0
                # 更新点击记录
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE merchant_clicks SET is_valid = 0 WHERE id = ?
                """, (click_id,))
                conn.commit()
                conn.close()
                
                # 记录防刷日志
                anti_fraud_detector.log_fraud_detection(
                    merchant_id=merchant_id,
                    detection_type="click_fraud",
                    risk_score=fraud_result.get("risk_score", 0),
                    suspicious_count=fraud_result.get("suspicious_count", 0),
                    action_taken="blocked",
                    details=fraud_result.get("details", {})
                )
            
            return {
                "success": True,
                "click_id": click_id,
                "is_valid": is_valid,
                "risk_score": fraud_result.get("risk_score", 0),
                "fraud_detected": fraud_result.get("risk_score", 0) >= 0.7
            }
        except Exception as e:
            print(f"记录点击错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_click_stats(self, merchant_id: int, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None) -> Dict:
        """获取点击统计
        
        Args:
            merchant_id: 商家ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            统计结果
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clause = "merchant_id = ?"
            params = [merchant_id]
            
            if start_date:
                where_clause += " AND created_at >= ?"
                params.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))
            
            if end_date:
                where_clause += " AND created_at <= ?"
                params.append(end_date.strftime('%Y-%m-%d %H:%M:%S'))
            
            # 总点击量
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(DISTINCT user_id) as unique_visitors,
                    COUNT(DISTINCT ip_address) as unique_ips,
                    COUNT(CASE WHEN click_type = 'detail' THEN 1 END) as detail_views,
                    COUNT(CASE WHEN click_type = 'navigate' THEN 1 END) as navigations,
                    COUNT(CASE WHEN is_valid = 1 THEN 1 END) as valid_clicks
                FROM merchant_clicks
                WHERE {where_clause}
            """, params)
            
            stats = cursor.fetchone()
            
            # 按日期统计
            cursor.execute(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT user_id) as visitors
                FROM merchant_clicks
                WHERE {where_clause} AND is_valid = 1
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """, params)
            
            daily_stats = cursor.fetchall()
            conn.close()
            
            return {
                "total_clicks": stats['total_clicks'] or 0,
                "valid_clicks": stats['valid_clicks'] or 0,
                "unique_visitors": stats['unique_visitors'] or 0,
                "unique_ips": stats['unique_ips'] or 0,
                "detail_views": stats['detail_views'] or 0,
                "navigations": stats['navigations'] or 0,
                "conversion_rate": round((stats['detail_views'] or 0) / max(stats['valid_clicks'] or 1, 1) * 100, 2),
                "daily_stats": [
                    {
                        "date": row['date'],
                        "clicks": row['clicks'],
                        "visitors": row['visitors']
                    }
                    for row in daily_stats
                ]
            }
        except Exception as e:
            print(f"获取点击统计错误: {e}")
            return {
                "total_clicks": 0,
                "valid_clicks": 0,
                "unique_visitors": 0,
                "unique_ips": 0,
                "detail_views": 0,
                "navigations": 0,
                "conversion_rate": 0.0,
                "daily_stats": []
            }
    
    def get_conversion_rate(self, merchant_id: int, window_days: int = 30) -> float:
        """计算转化率
        
        转化率 = 详情页访问数 / 总有效点击数
        
        Args:
            merchant_id: 商家ID
            window_days: 时间窗口（天）
        
        Returns:
            转化率（0-100）
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN click_type = 'detail' AND is_valid = 1 THEN 1 END) as details,
                    COUNT(CASE WHEN is_valid = 1 THEN 1 END) as total_valid
                FROM merchant_clicks
                WHERE merchant_id = ? AND created_at >= ?
            """, (merchant_id, cutoff_date))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[1] > 0:
                return round(row[0] / row[1] * 100, 2)
            return 0.0
        except Exception as e:
            print(f"计算转化率错误: {e}")
            return 0.0


# 全局实例
analytics_service = AnalyticsService()
