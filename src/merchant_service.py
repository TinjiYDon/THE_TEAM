"""
商家服务模块
包含商家管理、排名计算、榜单更新等功能
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
import json
import math

try:
    from .config import DATABASE_PATH, RANKING_CONFIG
    from .analytics_service import analytics_service
except ImportError:
    from config import DATABASE_PATH, RANKING_CONFIG
    from analytics_service import analytics_service


class MerchantService:
    """商家服务"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.ranking_config = RANKING_CONFIG
    
    def calculate_ranking_score(self, consumption_count: int, consumption_amount: float, 
                               click_count: int = 0, review_count: int = 0, 
                               avg_rating: float = 0.0) -> float:
        """计算排名分数
        
        综合评分 = 消费次数权重(40%) + 消费金额权重(30%) + 点击量权重(20%) + 好评权重(10%)
        
        Args:
            consumption_count: 消费次数
            consumption_amount: 消费总金额
            click_count: 点击量
            review_count: 评论数
            avg_rating: 平均评分
        
        Returns:
            排名分数
        """
        # 归一化处理（使用对数缩放避免数值过大）
        import math
        
        count_score = math.log1p(consumption_count) * 0.4
        amount_score = math.log1p(consumption_amount / 100) * 0.3  # 除以100归一化
        click_score = math.log1p(click_count) * 0.2
        review_score = (avg_rating / 5.0) * math.log1p(review_count) * 0.1
        
        return count_score + amount_score + click_score + review_score
    
    def update_rankings(self, period_days: int = 30):
        """更新商家排名（定时任务调用）
        
        Args:
            period_days: 统计周期（天）
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 计算统计周期
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            # 获取所有已认证的商家
            cursor.execute("""
                SELECT id, merchant_name, category
                FROM merchants
                WHERE status = 'approved'
            """)
            
            merchants = cursor.fetchall()
            
            rankings = []
            
            for merchant in merchants:
                merchant_id = merchant['id']
                merchant_name = merchant['merchant_name']
                category = merchant['category'] or '其他'
                
                # 统计消费数据
                start_str = period_start.strftime('%Y-%m-%d')
                end_str = period_end.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as count,
                        COALESCE(SUM(amount), 0) as total_amount
                    FROM bills
                    WHERE merchant = ? AND consume_time >= ? AND consume_time <= ?
                """, (merchant_name, start_str, end_str))
                
                bill_stats = cursor.fetchone()
                consumption_count = bill_stats['count'] or 0
                consumption_amount = bill_stats['total_amount'] or 0.0
                
                # 获取点击统计
                click_stats = analytics_service.get_click_stats(
                    merchant_id, 
                    start_date=period_start,
                    end_date=period_end
                )
                click_count = click_stats.get('valid_clicks', 0)
                
                # 获取评论统计
                cursor.execute("""
                    SELECT 
                        COUNT(*) as review_count,
                        COALESCE(AVG(rating), 0) as avg_rating
                    FROM merchant_reviews
                    WHERE merchant_id = ? AND status = 'approved'
                """, (merchant_id,))
                
                review_stats = cursor.fetchone()
                review_count = review_stats['review_count'] or 0
                avg_rating = review_stats['avg_rating'] or 0.0
                
                # 计算排名分数
                ranking_score = self.calculate_ranking_score(
                    consumption_count,
                    consumption_amount,
                    click_count,
                    review_count,
                    avg_rating
                )
                
                rankings.append({
                    'merchant_id': merchant_id,
                    'merchant_name': merchant_name,
                    'category': category,
                    'consumption_count': consumption_count,
                    'consumption_amount': consumption_amount,
                    'ranking_score': ranking_score
                })
            
            # 按分数排序
            rankings.sort(key=lambda x: x['ranking_score'], reverse=True)
            
            # 更新排名数据
            cursor.execute("DELETE FROM merchant_rankings WHERE period_start >= ?", 
                          (period_start.strftime('%Y-%m-%d %H:%M:%S'),))
            
            for idx, ranking in enumerate(rankings):
                cursor.execute("""
                    INSERT INTO merchant_rankings
                    (merchant_id, merchant_name, category, total_consumption_count, 
                     total_consumption_amount, ranking_score, ranking_position,
                     period_start, period_end, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    ranking['merchant_id'],
                    ranking['merchant_name'],
                    ranking['category'],
                    ranking['consumption_count'],
                    ranking['consumption_amount'],
                    ranking['ranking_score'],
                    idx + 1,  # 排名位置
                    period_start.strftime('%Y-%m-%d %H:%M:%S'),
                    period_end.strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "updated_count": len(rankings),
                "period_start": period_start.strftime('%Y-%m-%d'),
                "period_end": period_end.strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"更新排名错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_hot_rankings(self, category: Optional[str] = None, 
                        amount_range: Optional[Tuple[float, float]] = None,
                        limit: int = 50) -> List[Dict]:
        """获取热门商家榜单
        
        Args:
            category: 类别筛选
            amount_range: 金额区间筛选 (min, max)
            limit: 返回数量限制
        
        Returns:
            热门商家列表
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            where_clause = "1=1"
            params = []
            
            if category:
                where_clause += " AND category = ?"
                params.append(category)
            
            if amount_range:
                where_clause += " AND total_consumption_amount >= ? AND total_consumption_amount <= ?"
                params.extend(amount_range)
            
            # 获取最新排名数据
            cursor.execute(f"""
                SELECT 
                    r.merchant_id,
                    r.merchant_name,
                    r.category,
                    r.total_consumption_count,
                    r.total_consumption_amount,
                    r.ranking_score,
                    r.ranking_position,
                    m.id as merchant_db_id,
                    mi.avg_rating,
                    mi.review_count,
                    mi.images
                FROM merchant_rankings r
                JOIN merchants m ON r.merchant_id = m.id
                LEFT JOIN merchant_info mi ON m.id = mi.merchant_id
                WHERE {where_clause} AND m.status = 'approved'
                ORDER BY r.ranking_score DESC
                LIMIT ?
            """, params + [limit])
            
            rankings = cursor.fetchall()
            conn.close()
            
            result = []
            for row in rankings:
                images = []
                if row['images']:
                    try:
                        images = json.loads(row['images'])
                    except:
                        pass
                
                result.append({
                    'merchant_id': row['merchant_id'],
                    'merchant_name': row['merchant_name'],
                    'category': row['category'],
                    'consumption_count': row['total_consumption_count'],
                    'consumption_amount': round(row['total_consumption_amount'], 2),
                    'ranking_score': round(row['ranking_score'], 3),
                    'ranking_position': row['ranking_position'],
                    'avg_rating': round(row['avg_rating'] or 0.0, 1),
                    'review_count': row['review_count'] or 0,
                    'images': images[:3] if images else []  # 最多返回3张图片
                })
            
            return result
        except Exception as e:
            print(f"获取热门榜单错误: {e}")
            return []
    
    def get_sponsor_rankings(self, limit: int = 40) -> List[Dict]:
        """获取赞助商家榜单
        
        综合评分 = 竞价出价(40%) + 质量得分(30%) + 相关性得分(30%)
        
        Args:
            limit: 返回数量限制
        
        Returns:
            赞助商家列表（按综合评分排序）
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取活跃的赞助商家
            cursor.execute("""
                SELECT 
                    s.id as sponsorship_id,
                    s.merchant_id,
                    s.sponsorship_type,
                    s.bid_amount,
                    s.cpc_price,
                    s.total_spent,
                    m.merchant_name,
                    m.category,
                    mi.avg_rating,
                    mi.review_count,
                    mi.images
                FROM merchant_sponsorships s
                JOIN merchants m ON s.merchant_id = m.id
                LEFT JOIN merchant_info mi ON m.id = mi.merchant_id
                WHERE s.status = 'active' AND m.status = 'approved'
                ORDER BY s.bid_amount DESC, s.total_spent DESC
            """)
            
            sponsors = cursor.fetchall()
            
            # 计算综合评分
            scored_sponsors = []
            for sponsor in sponsors:
                # 竞价出价分数（归一化到0-1）
                bid_score = min(sponsor['bid_amount'] / 1000.0, 1.0) * 0.4
                
                # 质量得分（基于点击率、转化率等）
                click_stats = analytics_service.get_click_stats(sponsor['merchant_id'])
                conversion_rate = click_stats.get('conversion_rate', 0) / 100.0
                quality_score = (conversion_rate + (sponsor['avg_rating'] or 0) / 5.0) / 2.0 * 0.3
                
                # 相关性得分（简化：基于评论数）
                relevance_score = min(math.log1p(sponsor['review_count'] or 0) / 5.0, 1.0) * 0.3
                
                total_score = bid_score + quality_score + relevance_score
                
                images = []
                if sponsor['images']:
                    try:
                        images = json.loads(sponsor['images'])
                    except:
                        pass
                
                scored_sponsors.append({
                    'sponsorship_id': sponsor['sponsorship_id'],
                    'merchant_id': sponsor['merchant_id'],
                    'merchant_name': sponsor['merchant_name'],
                    'category': sponsor['category'],
                    'sponsorship_type': sponsor['sponsorship_type'],
                    'bid_amount': sponsor['bid_amount'],
                    'cpc_price': sponsor['cpc_price'],
                    'total_spent': sponsor['total_spent'],
                    'avg_rating': round(sponsor['avg_rating'] or 0.0, 1),
                    'review_count': sponsor['review_count'] or 0,
                    'images': images[:2] if images else [],  # 赞助商家最多2张图片
                    'composite_score': total_score
                })
            
            # 按综合评分排序
            scored_sponsors.sort(key=lambda x: x['composite_score'], reverse=True)
            conn.close()
            
            return scored_sponsors[:limit]
        except Exception as e:
            print(f"获取赞助榜单错误: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_merchant_detail(self, merchant_id: int) -> Optional[Dict]:
        """获取商家详情"""
        try:
            import math
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取商家基本信息
            cursor.execute("""
                SELECT m.*, mi.*
                FROM merchants m
                LEFT JOIN merchant_info mi ON m.id = mi.merchant_id
                WHERE m.id = ?
            """, (merchant_id,))
            
            merchant = cursor.fetchone()
            if not merchant:
                conn.close()
                return None
            
            # 获取评论列表
            cursor.execute("""
                SELECT r.*, u.username
                FROM merchant_reviews r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.merchant_id = ? AND r.status = 'approved'
                ORDER BY r.created_at DESC
                LIMIT 20
            """, (merchant_id,))
            
            reviews = cursor.fetchall()
            
            # 获取统计数据
            click_stats = analytics_service.get_click_stats(merchant_id)
            
            business_hours = {}
            if merchant['business_hours']:
                try:
                    business_hours = json.loads(merchant['business_hours'])
                except:
                    pass
            
            images = []
            if merchant['images']:
                try:
                    images = json.loads(merchant['images'])
                except:
                    pass
            
            result = {
                'merchant_id': merchant['id'],
                'merchant_name': merchant['merchant_name'],
                'category': merchant['category'],
                'description': merchant['description'],
                'address': merchant['address'],
                'latitude': merchant['latitude'],
                'longitude': merchant['longitude'],
                'phone': merchant['phone'],
                'business_hours': business_hours,
                'images': images,
                'avg_rating': round(merchant['avg_rating'] or 0.0, 1),
                'review_count': merchant['review_count'] or 0,
                'click_stats': click_stats,
                'reviews': [
                    {
                        'id': r['id'],
                        'user_id': r['user_id'],
                        'username': r['username'] or '匿名用户',
                        'rating': r['rating'],
                        'content': r['content'],
                        'images': json.loads(r['images']) if r['images'] else [],
                        'created_at': r['created_at']
                    }
                    for r in reviews
                ]
            }
            
            conn.close()
            return result
        except Exception as e:
            print(f"获取商家详情错误: {e}")
            import traceback
            traceback.print_exc()
            return None


# 全局实例
merchant_service = MerchantService()
