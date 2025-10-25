"""
AI服务模块 - 用户画像、推荐系统、智能分析
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import jieba.analyse
from collections import Counter
import json

from .database import db_manager
from .config import AI_CONFIG

class UserProfiler:
    """用户画像生成器"""
    
    def __init__(self):
        self.config = AI_CONFIG
        # 初始化jieba
        jieba.initialize()
    
    def generate_user_profile(self, user_id: int) -> Dict[str, Any]:
        """生成用户画像"""
        # 获取用户消费数据
        bills = db_manager.get_bills(user_id, limit=1000)
        
        if not bills:
            return self._get_default_profile(user_id)
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'consume_time': bill.consume_time,
            'amount': bill.amount,
            'merchant': bill.merchant,
            'category': bill.category,
            'payment_method': bill.payment_method
        } for bill in bills])
        
        # 生成各种画像特征
        profile = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'spending_pattern': self._analyze_spending_pattern(df),
            'category_preference': self._analyze_category_preference(df),
            'payment_behavior': self._analyze_payment_behavior(df),
            'consumption_habits': self._analyze_consumption_habits(df),
            'risk_profile': self._analyze_risk_profile(df),
            'financial_health': self._analyze_financial_health(df),
            'recommendation_tags': self._generate_recommendation_tags(df)
        }
        
        # 保存用户画像到数据库
        self._save_user_profile(user_id, profile)
        
        return profile
    
    def _get_default_profile(self, user_id: int) -> Dict[str, Any]:
        """获取默认用户画像"""
        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'spending_pattern': {'type': 'unknown', 'level': 'low'},
            'category_preference': {},
            'payment_behavior': {'preferred_method': 'unknown'},
            'consumption_habits': {'frequency': 'low', 'consistency': 'unknown'},
            'risk_profile': {'tolerance': 'conservative'},
            'financial_health': {'score': 50, 'level': 'average'},
            'recommendation_tags': ['new_user']
        }
    
    def _analyze_spending_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析消费模式"""
        total_amount = df['amount'].sum()
        avg_amount = df['amount'].mean()
        std_amount = df['amount'].std()
        
        # 消费水平分类
        if total_amount > 10000:
            level = 'high'
        elif total_amount > 5000:
            level = 'medium'
        else:
            level = 'low'
        
        # 消费稳定性
        cv = std_amount / avg_amount if avg_amount > 0 else 0
        if cv < 0.5:
            stability = 'stable'
        elif cv < 1.0:
            stability = 'moderate'
        else:
            stability = 'volatile'
        
        # 消费类型
        if avg_amount > 500:
            pattern_type = 'high_value'
        elif avg_amount > 100:
            pattern_type = 'medium_value'
        else:
            pattern_type = 'low_value'
        
        return {
            'type': pattern_type,
            'level': level,
            'stability': stability,
            'total_amount': total_amount,
            'avg_amount': avg_amount,
            'coefficient_variation': cv
        }
    
    def _analyze_category_preference(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析类别偏好"""
        category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        total_amount = category_data.sum()
        
        preferences = {}
        for category, amount in category_data.items():
            preferences[category] = {
                'amount': amount,
                'percentage': amount / total_amount * 100,
                'preference_level': 'high' if amount / total_amount > 0.3 else 'medium' if amount / total_amount > 0.1 else 'low'
            }
        
        # 主要偏好类别
        top_categories = category_data.head(3).index.tolist()
        
        return {
            'preferences': preferences,
            'top_categories': top_categories,
            'diversity_score': len(category_data) / 10  # 类别多样性评分
        }
    
    def _analyze_payment_behavior(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析支付行为"""
        payment_data = df.groupby('payment_method')['amount'].sum().sort_values(ascending=False)
        total_amount = payment_data.sum()
        
        payment_behavior = {}
        for method, amount in payment_data.items():
            payment_behavior[method] = {
                'amount': amount,
                'percentage': amount / total_amount * 100,
                'frequency': len(df[df['payment_method'] == method])
            }
        
        preferred_method = payment_data.index[0]
        
        return {
            'preferred_method': preferred_method,
            'behavior': payment_behavior,
            'diversity': len(payment_data)
        }
    
    def _analyze_consumption_habits(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析消费习惯"""
        # 消费频率
        df['date'] = df['consume_time'].dt.date
        daily_counts = df.groupby('date').size()
        avg_daily_frequency = daily_counts.mean()
        
        if avg_daily_frequency > 3:
            frequency = 'high'
        elif avg_daily_frequency > 1:
            frequency = 'medium'
        else:
            frequency = 'low'
        
        # 消费时间偏好
        df['hour'] = df['consume_time'].dt.hour
        hourly_counts = df.groupby('hour').size()
        peak_hour = hourly_counts.idxmax()
        
        if 6 <= peak_hour <= 11:
            time_preference = 'morning'
        elif 12 <= peak_hour <= 17:
            time_preference = 'afternoon'
        elif 18 <= peak_hour <= 22:
            time_preference = 'evening'
        else:
            time_preference = 'night'
        
        # 消费一致性
        weekly_amounts = df.groupby(df['consume_time'].dt.isocalendar().week)['amount'].sum()
        consistency = 1 - (weekly_amounts.std() / weekly_amounts.mean()) if weekly_amounts.mean() > 0 else 0
        
        return {
            'frequency': frequency,
            'avg_daily_frequency': avg_daily_frequency,
            'time_preference': time_preference,
            'peak_hour': peak_hour,
            'consistency': 'high' if consistency > 0.7 else 'medium' if consistency > 0.4 else 'low'
        }
    
    def _analyze_risk_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析风险偏好"""
        # 基于消费金额的波动性
        amount_std = df['amount'].std()
        amount_mean = df['amount'].mean()
        volatility = amount_std / amount_mean if amount_mean > 0 else 0
        
        # 基于消费类别的多样性
        category_diversity = len(df['category'].unique())
        
        # 基于单次消费金额
        max_amount = df['amount'].max()
        avg_amount = df['amount'].mean()
        
        if volatility > 1.0 and max_amount > avg_amount * 3:
            risk_tolerance = 'aggressive'
        elif volatility > 0.5 or category_diversity > 5:
            risk_tolerance = 'moderate'
        else:
            risk_tolerance = 'conservative'
        
        return {
            'tolerance': risk_tolerance,
            'volatility': volatility,
            'category_diversity': category_diversity,
            'max_single_amount': max_amount
        }
    
    def _analyze_financial_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析财务健康度"""
        total_amount = df['amount'].sum()
        avg_amount = df['amount'].mean()
        
        # 基础评分
        score = 50
        
        # 消费合理性评分
        if avg_amount < 100:
            score += 20
        elif avg_amount < 300:
            score += 10
        elif avg_amount > 1000:
            score -= 20
        
        # 消费多样性评分
        category_count = len(df['category'].unique())
        if category_count > 5:
            score += 15
        elif category_count > 3:
            score += 10
        
        # 消费稳定性评分
        daily_amounts = df.groupby(df['consume_time'].dt.date)['amount'].sum()
        if len(daily_amounts) > 1:
            stability = 1 - (daily_amounts.std() / daily_amounts.mean()) if daily_amounts.mean() > 0 else 0
            if stability > 0.7:
                score += 15
            elif stability > 0.4:
                score += 10
        
        # 确保评分在0-100之间
        score = max(0, min(100, score))
        
        if score >= 80:
            level = 'excellent'
        elif score >= 60:
            level = 'good'
        elif score >= 40:
            level = 'average'
        else:
            level = 'poor'
        
        return {
            'score': score,
            'level': level,
            'total_amount': total_amount,
            'avg_amount': avg_amount,
            'category_diversity': category_count
        }
    
    def _generate_recommendation_tags(self, df: pd.DataFrame) -> List[str]:
        """生成推荐标签"""
        tags = []
        
        # 基于消费金额
        total_amount = df['amount'].sum()
        if total_amount > 10000:
            tags.append('high_spender')
        elif total_amount < 2000:
            tags.append('low_spender')
        
        # 基于消费类别
        category_data = df.groupby('category')['amount'].sum()
        if '餐饮' in category_data and category_data['餐饮'] / total_amount > 0.4:
            tags.append('food_lover')
        if '娱乐' in category_data and category_data['娱乐'] / total_amount > 0.3:
            tags.append('entertainment_focused')
        
        # 基于支付方式
        payment_data = df.groupby('payment_method').size()
        if '微信' in payment_data and payment_data['微信'] > len(df) * 0.7:
            tags.append('wechat_user')
        if '支付宝' in payment_data and payment_data['支付宝'] > len(df) * 0.7:
            tags.append('alipay_user')
        
        # 基于消费频率
        daily_counts = df.groupby(df['consume_time'].dt.date).size()
        if daily_counts.mean() > 2:
            tags.append('frequent_buyer')
        
        return tags
    
    def _save_user_profile(self, user_id: int, profile: Dict[str, Any]):
        """保存用户画像到数据库"""
        profile_data = {
            'user_id': user_id,
            'spending_pattern': json.dumps(profile['spending_pattern']),
            'risk_tolerance': profile['risk_profile']['tolerance'],
            'investment_preference': json.dumps(profile['category_preference'])
        }
        
        # 更新或创建用户画像
        existing_profile = db_manager.get_user_profile(user_id)
        if existing_profile:
            db_manager.update_user_profile(user_id, profile_data)
        else:
            db_manager.create_user_profile(profile_data)


class RecommendationEngine:
    """推荐引擎"""
    
    def __init__(self):
        self.config = AI_CONFIG
    
    def get_financial_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取金融产品推荐"""
        # 获取用户画像
        profiler = UserProfiler()
        profile = profiler.generate_user_profile(user_id)
        
        # 获取金融产品
        products = db_manager.get_financial_products()
        
        if not products:
            return []
        
        recommendations = []
        
        for product in products:
            score = self._calculate_recommendation_score(profile, product)
            if score > 0.3:  # 只推荐评分较高的产品
                recommendations.append({
                    'product_id': product.id,
                    'product_name': product.product_name,
                    'product_type': product.product_type,
                    'interest_rate': product.interest_rate,
                    'min_amount': product.min_amount,
                    'max_amount': product.max_amount,
                    'risk_level': product.risk_level,
                    'description': product.description,
                    'recommendation_score': score,
                    'reason': self._get_recommendation_reason(profile, product)
                })
        
        # 按推荐评分排序
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def _calculate_recommendation_score(self, profile: Dict[str, Any], product) -> float:
        """计算推荐评分"""
        score = 0.0
        
        # 基于用户风险偏好
        risk_tolerance = profile['risk_profile']['tolerance']
        if risk_tolerance == 'aggressive' and product.risk_level in ['high', 'medium']:
            score += 0.3
        elif risk_tolerance == 'moderate' and product.risk_level in ['medium', 'low']:
            score += 0.3
        elif risk_tolerance == 'conservative' and product.risk_level == 'low':
            score += 0.3
        
        # 基于用户消费水平
        spending_level = profile['spending_pattern']['level']
        if spending_level == 'high' and product.min_amount and product.min_amount <= 10000:
            score += 0.2
        elif spending_level == 'medium' and product.min_amount and product.min_amount <= 5000:
            score += 0.2
        elif spending_level == 'low' and product.min_amount and product.min_amount <= 1000:
            score += 0.2
        
        # 基于产品类型偏好
        if product.product_type == '理财' and 'savings_focused' in profile['recommendation_tags']:
            score += 0.2
        elif product.product_type == '贷款' and 'high_spender' in profile['recommendation_tags']:
            score += 0.2
        elif product.product_type == '保险' and 'conservative' in profile['risk_profile']['tolerance']:
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_recommendation_reason(self, profile: Dict[str, Any], product) -> str:
        """获取推荐理由"""
        reasons = []
        
        # 风险匹配
        risk_tolerance = profile['risk_profile']['tolerance']
        if risk_tolerance == 'conservative' and product.risk_level == 'low':
            reasons.append("符合您的保守投资偏好")
        elif risk_tolerance == 'aggressive' and product.risk_level == 'high':
            reasons.append("匹配您的高风险承受能力")
        
        # 金额匹配
        spending_level = profile['spending_pattern']['level']
        if spending_level == 'high' and product.min_amount and product.min_amount <= 10000:
            reasons.append("适合您的高消费水平")
        elif spending_level == 'low' and product.min_amount and product.min_amount <= 1000:
            reasons.append("适合您的消费预算")
        
        # 类型匹配
        if product.product_type == '理财':
            reasons.append("帮助您实现财富增值")
        elif product.product_type == '贷款':
            reasons.append("满足您的资金需求")
        elif product.product_type == '保险':
            reasons.append("提供风险保障")
        
        return "；".join(reasons) if reasons else "基于您的消费习惯推荐"
    
    def get_spending_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """获取消费建议"""
        # 获取用户消费数据
        bills = db_manager.get_bills(user_id, limit=1000)
        
        if not bills:
            return []
        
        df = pd.DataFrame([{
            'consume_time': bill.consume_time,
            'amount': bill.amount,
            'category': bill.category,
            'merchant': bill.merchant
        } for bill in bills])
        
        recommendations = []
        
        # 基于消费类别的建议
        category_data = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        total_amount = category_data.sum()
        
        for category, amount in category_data.items():
            percentage = amount / total_amount * 100
            if percentage > 50:
                recommendations.append({
                    'type': 'category_balance',
                    'title': f'{category}消费占比过高',
                    'message': f'{category}消费占总消费的{percentage:.1f}%，建议增加其他类别消费',
                    'priority': 'high',
                    'action': f'减少{category}消费，增加其他类别支出'
                })
        
        # 基于消费金额的建议
        avg_amount = df['amount'].mean()
        if avg_amount > 500:
            recommendations.append({
                'type': 'amount_control',
                'title': '单次消费金额较高',
                'message': f'平均单次消费{avg_amount:.2f}元，建议控制单次消费金额',
                'priority': 'medium',
                'action': '制定单次消费限额，避免冲动消费'
            })
        
        # 基于消费频率的建议
        daily_counts = df.groupby(df['consume_time'].dt.date).size()
        if daily_counts.mean() > 3:
            recommendations.append({
                'type': 'frequency_control',
                'title': '消费频率过高',
                'message': f'平均每日消费{daily_counts.mean():.1f}次，建议减少不必要的消费',
                'priority': 'medium',
                'action': '制定消费计划，减少冲动消费'
            })
        
        return recommendations


class IntelligentAnalyzer:
    """智能分析器"""
    
    def __init__(self):
        self.profiler = UserProfiler()
        self.recommendation_engine = RecommendationEngine()
    
    def generate_comprehensive_analysis(self, user_id: int) -> Dict[str, Any]:
        """生成综合分析报告"""
        # 生成用户画像
        profile = self.profiler.generate_user_profile(user_id)
        
        # 获取金融产品推荐
        financial_recommendations = self.recommendation_engine.get_financial_recommendations(user_id)
        
        # 获取消费建议
        spending_recommendations = self.recommendation_engine.get_spending_recommendations(user_id)
        
        # 生成智能洞察
        insights = self._generate_intelligent_insights(profile)
        
        return {
            'user_profile': profile,
            'financial_recommendations': financial_recommendations,
            'spending_recommendations': spending_recommendations,
            'intelligent_insights': insights,
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_intelligent_insights(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成智能洞察"""
        insights = []
        
        # 基于消费模式的洞察
        spending_pattern = profile['spending_pattern']
        if spending_pattern['type'] == 'high_value' and spending_pattern['stability'] == 'stable':
            insights.append({
                'type': 'spending_insight',
                'title': '稳定的高价值消费模式',
                'message': '您的消费模式显示您偏好高质量商品，且消费稳定，建议考虑投资理财产品',
                'confidence': 0.8
            })
        
        # 基于风险偏好的洞察
        risk_profile = profile['risk_profile']
        if risk_profile['tolerance'] == 'conservative':
            insights.append({
                'type': 'risk_insight',
                'title': '保守型投资者',
                'message': '您的消费行为显示您偏好稳定，建议选择低风险的理财产品',
                'confidence': 0.9
            })
        
        # 基于财务健康的洞察
        financial_health = profile['financial_health']
        if financial_health['level'] == 'excellent':
            insights.append({
                'type': 'financial_insight',
                'title': '优秀的财务管理能力',
                'message': '您的消费习惯显示您有良好的财务管理能力，可以考虑更高收益的投资',
                'confidence': 0.85
            })
        
        return insights

# 创建全局AI服务实例
user_profiler = UserProfiler()
recommendation_engine = RecommendationEngine()
intelligent_analyzer = IntelligentAnalyzer()
