"""
AI防刷检测模块
用于检测恶意刷单、刷热度、刷点击量等行为
"""
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import sqlite3

try:
    from .config import ANTI_FRAUD_CONFIG, DATABASE_PATH
except ImportError:
    from config import ANTI_FRAUD_CONFIG, DATABASE_PATH


class AntiFraudDetector:
    """防刷检测器"""
    
    def __init__(self):
        self.config = ANTI_FRAUD_CONFIG
        self.db_path = DATABASE_PATH
    
    def generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """生成设备指纹"""
        if not self.config.get("device_fingerprint_enabled", True):
            return ""
        
        # 组合用户代理和IP地址生成指纹
        fingerprint_str = f"{user_agent}:{ip_address}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def detect_click_fraud(self, merchant_id: int, window_minutes: int = 60) -> Dict:
        """检测点击欺诈
        
        Args:
            merchant_id: 商家ID
            window_minutes: 检测时间窗口（分钟）
        
        Returns:
            检测结果字典，包含风险分数、可疑点击数等
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取时间窗口内的点击记录
            cutoff_time = (datetime.now() - timedelta(minutes=window_minutes)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT id, user_id, ip_address, device_fingerprint, click_type, created_at
                FROM merchant_clicks
                WHERE merchant_id = ? AND created_at >= ? AND is_valid = 1
                ORDER BY created_at DESC
            """, (merchant_id, cutoff_time))
            
            clicks = cursor.fetchall()
            conn.close()
            
            if not clicks:
                return {
                    "risk_score": 0.0,
                    "suspicious_count": 0,
                    "details": {},
                    "action_taken": None
                }
            
            # 分析点击模式
            ip_counts = defaultdict(int)
            device_counts = defaultdict(int)
            user_counts = defaultdict(int)
            time_intervals = []
            
            prev_time = None
            for click in clicks:
                ip = click['ip_address'] or ''
                device = click['device_fingerprint'] or ''
                user_id = click['user_id'] or 0
                click_time = datetime.fromisoformat(click['created_at'].replace(' ', 'T'))
                
                ip_counts[ip] += 1
                device_counts[device] += 1
                user_counts[user_id] += 1
                
                if prev_time:
                    interval = (click_time - prev_time).total_seconds()
                    time_intervals.append(interval)
                prev_time = click_time
            
            # 计算风险指标
            risk_factors = {}
            
            # 1. IP频率检测
            max_ip_clicks = max(ip_counts.values()) if ip_counts else 0
            ip_rate_limit = self.config.get("click_rate_limit", 10)
            if max_ip_clicks > ip_rate_limit:
                risk_factors["ip_frequency"] = min(max_ip_clicks / ip_rate_limit, 2.0)
            
            # 2. 设备指纹重复检测
            max_device_clicks = max(device_counts.values()) if device_counts else 0
            if max_device_clicks > ip_rate_limit:
                risk_factors["device_frequency"] = min(max_device_clicks / ip_rate_limit, 2.0)
            
            # 3. 时间间隔异常检测（过于规律的点击）
            if time_intervals:
                avg_interval = sum(time_intervals) / len(time_intervals)
                # 如果时间间隔过于规律（标准差小），可能是机器人
                if len(time_intervals) > 5:
                    variance = sum((x - avg_interval) ** 2 for x in time_intervals) / len(time_intervals)
                    std_dev = variance ** 0.5
                    if std_dev < avg_interval * 0.1:  # 标准差小于平均值的10%
                        risk_factors["regular_pattern"] = 1.5
            
            # 4. 单用户大量点击
            max_user_clicks = max(user_counts.values()) if user_counts else 0
            if max_user_clicks > 20:
                risk_factors["user_frequency"] = min(max_user_clicks / 20, 2.0)
            
            # 5. IP白名单检查
            suspicious_ips = []
            for ip, count in ip_counts.items():
                if ip and ip not in self.config.get("ip_whitelist", []):
                    if count > ip_rate_limit:
                        suspicious_ips.append(ip)
            
            # 计算综合风险分数（0-1）
            risk_score = 0.0
            if risk_factors:
                # 加权平均
                weights = {
                    "ip_frequency": 0.3,
                    "device_frequency": 0.3,
                    "regular_pattern": 0.2,
                    "user_frequency": 0.2
                }
                weighted_sum = sum(risk_factors.get(k, 0) * weights.get(k, 0) for k in weights.keys())
                risk_score = min(weighted_sum / sum(weights.values()), 1.0)
            
            # 确定可疑点击数
            suspicious_count = len([c for c in clicks if c['ip_address'] in suspicious_ips])
            
            # 决定采取的行动
            action_taken = None
            if risk_score >= self.config.get("risk_score_threshold", 0.7):
                if self.config.get("auto_block_enabled", True):
                    action_taken = "blocked"
                else:
                    action_taken = "flagged"
            elif risk_score >= self.config.get("review_required_score", 0.5):
                action_taken = "reviewed"
            
            return {
                "risk_score": round(risk_score, 3),
                "suspicious_count": suspicious_count,
                "total_clicks": len(clicks),
                "details": {
                    "risk_factors": risk_factors,
                    "suspicious_ips": suspicious_ips[:10],  # 最多返回10个
                    "max_ip_clicks": max_ip_clicks,
                    "max_device_clicks": max_device_clicks,
                    "max_user_clicks": max_user_clicks
                },
                "action_taken": action_taken
            }
        except Exception as e:
            print(f"防刷检测错误: {e}")
            return {
                "risk_score": 0.0,
                "suspicious_count": 0,
                "details": {"error": str(e)},
                "action_taken": None
            }
    
    def detect_review_fraud(self, merchant_id: int, window_days: int = 30) -> Dict:
        """检测评论欺诈（刷好评/差评）"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT id, user_id, rating, content, created_at
                FROM merchant_reviews
                WHERE merchant_id = ? AND created_at >= ? AND status = 'approved'
                ORDER BY created_at DESC
            """, (merchant_id, cutoff_time))
            
            reviews = cursor.fetchall()
            conn.close()
            
            if not reviews:
                return {
                    "risk_score": 0.0,
                    "suspicious_count": 0,
                    "details": {}
                }
            
            # 分析评论模式
            user_review_counts = defaultdict(int)
            rating_distribution = defaultdict(int)
            content_similarity = []
            
            for review in reviews:
                user_id = review['user_id']
                rating = review['rating']
                content = review['content'] or ''
                
                user_review_counts[user_id] += 1
                rating_distribution[rating] += 1
                content_similarity.append(len(content))
            
            risk_factors = {}
            
            # 1. 单用户多次评论
            max_user_reviews = max(user_review_counts.values()) if user_review_counts else 0
            if max_user_reviews > 3:
                risk_factors["user_repeat"] = min(max_user_reviews / 3, 2.0)
            
            # 2. 评分分布异常（全部5星或全部1星）
            total_reviews = len(reviews)
            if total_reviews > 5:
                five_star_ratio = rating_distribution.get(5, 0) / total_reviews
                one_star_ratio = rating_distribution.get(1, 0) / total_reviews
                if five_star_ratio > 0.9 or one_star_ratio > 0.9:
                    risk_factors["rating_bias"] = 1.5
            
            # 3. 评论内容相似度（简单检测：长度过于一致）
            if len(content_similarity) > 5:
                avg_length = sum(content_similarity) / len(content_similarity)
                variance = sum((x - avg_length) ** 2 for x in content_similarity) / len(content_similarity)
                std_dev = variance ** 0.5
                if std_dev < avg_length * 0.2:  # 内容长度过于一致
                    risk_factors["content_similarity"] = 1.2
            
            # 计算风险分数
            risk_score = 0.0
            if risk_factors:
                risk_score = min(sum(risk_factors.values()) / len(risk_factors), 1.0)
            
            return {
                "risk_score": round(risk_score, 3),
                "suspicious_count": max_user_reviews - 1 if max_user_reviews > 1 else 0,
                "total_reviews": total_reviews,
                "details": {
                    "risk_factors": risk_factors,
                    "rating_distribution": dict(rating_distribution),
                    "max_user_reviews": max_user_reviews
                }
            }
        except Exception as e:
            print(f"评论欺诈检测错误: {e}")
            return {
                "risk_score": 0.0,
                "suspicious_count": 0,
                "details": {"error": str(e)}
            }
    
    def detect_ranking_manipulation(self, merchant_id: int, window_days: int = 7) -> Dict:
        """检测排名操纵（异常消费增长）"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取商家名称
            cursor.execute("SELECT merchant_name FROM merchants WHERE id = ?", (merchant_id,))
            merchant_row = cursor.fetchone()
            if not merchant_row:
                conn.close()
                return {"risk_score": 0.0, "details": {}}
            
            merchant_name = merchant_row['merchant_name']
            
            # 获取最近window_days天的账单数据
            cutoff_time = (datetime.now() - timedelta(days=window_days)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT DATE(consume_time) as date, COUNT(*) as count, SUM(amount) as total
                FROM bills
                WHERE merchant = ? AND consume_time >= ?
                GROUP BY DATE(consume_time)
                ORDER BY date DESC
            """, (merchant_name, cutoff_time))
            
            daily_stats = cursor.fetchall()
            conn.close()
            
            if len(daily_stats) < 3:
                return {"risk_score": 0.0, "details": {}}
            
            # 分析每日消费模式
            daily_counts = [row['count'] for row in daily_stats]
            daily_totals = [row['total'] for row in daily_stats]
            
            # 检测异常增长（突然大幅增长可能是刷单）
            risk_factors = {}
            
            if len(daily_counts) >= 3:
                # 计算增长率
                recent_avg = sum(daily_counts[-3:]) / 3
                previous_avg = sum(daily_counts[:-3]) / max(len(daily_counts) - 3, 1) if len(daily_counts) > 3 else recent_avg
                
                if previous_avg > 0:
                    growth_rate = (recent_avg - previous_avg) / previous_avg
                    if growth_rate > 2.0:  # 增长超过200%
                        risk_factors["sudden_growth"] = min(growth_rate / 2.0, 2.0)
            
            # 检测异常金额（单笔金额异常大）
            if daily_totals:
                avg_daily = sum(daily_totals) / len(daily_totals)
                max_daily = max(daily_totals)
                if max_daily > avg_daily * 5:
                    risk_factors["amount_anomaly"] = 1.3
            
            risk_score = 0.0
            if risk_factors:
                risk_score = min(sum(risk_factors.values()) / len(risk_factors), 1.0)
            
            return {
                "risk_score": round(risk_score, 3),
                "details": {
                    "risk_factors": risk_factors,
                    "daily_stats": [{"date": row['date'], "count": row['count'], "total": row['total']} for row in daily_stats]
                }
            }
        except Exception as e:
            print(f"排名操纵检测错误: {e}")
            return {
                "risk_score": 0.0,
                "details": {"error": str(e)}
            }
    
    def log_fraud_detection(self, merchant_id: Optional[int], detection_type: str, 
                           risk_score: float, suspicious_count: int, 
                           action_taken: Optional[str], details: Dict):
        """记录防刷检测日志"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fraud_detection_logs 
                (merchant_id, detection_type, suspicious_count, risk_score, action_taken, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                merchant_id,
                detection_type,
                suspicious_count,
                risk_score,
                action_taken,
                json.dumps(details, ensure_ascii=False)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"记录防刷日志错误: {e}")
    
    def mark_invalid_clicks(self, merchant_id: int, click_ids: List[int]):
        """标记无效点击"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(click_ids))
            cursor.execute(f"""
                UPDATE merchant_clicks
                SET is_valid = 0
                WHERE merchant_id = ? AND id IN ({placeholders})
            """, [merchant_id] + click_ids)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"标记无效点击错误: {e}")


# 全局实例
anti_fraud_detector = AntiFraudDetector()
