"""
账单查询模块 - 智能查询和NLP处理
"""
import re
import jieba
import jieba.posseg as pseg
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .database import db_manager
from .data_cleaning import data_cleaner
from .config import CLEANING_CONFIG

class BillQueryProcessor:
    """账单查询处理器"""
    
    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()
        
        # 定义查询意图模板
        self.intent_templates = {
            'query_amount': [
                '花了多少钱', '消费多少', '支出多少', '总共多少',
                '花了多少', '消费总额', '总支出'
            ],
            'query_category': [
                '餐饮花了多少', '交通费多少', '购物花了多少',
                '娱乐消费', '医疗费用', '教育支出'
            ],
            'query_time': [
                '今天花了多少', '昨天消费', '这周支出', '本月花费',
                '上个月消费', '今年支出', '最近消费'
            ],
            'query_merchant': [
                '星巴克花了多少', '麦当劳消费', '淘宝购物',
                '滴滴打车', '美团外卖'
            ],
            'query_trend': [
                '消费趋势', '支出变化', '消费分析', '花费统计',
                '消费报告', '支出分析'
            ],
            'query_comparison': [
                '对比', '比较', '相比', '环比', '同比'
            ]
        }
        
        # 时间关键词映射
        self.time_keywords = {
            '今天': 0,
            '昨天': -1,
            '前天': -2,
            '这周': 7,
            '上周': 14,
            '本月': 30,
            '上个月': 60,
            '今年': 365,
            '去年': 730
        }
        
        # 类别关键词映射
        self.category_keywords = {
            '餐饮': ['餐饮', '吃饭', '餐厅', '外卖', '咖啡', '奶茶', '快餐', '美食'],
            '交通': ['交通', '打车', '地铁', '公交', '加油', '停车', '出行', '出租车'],
            '购物': ['购物', '超市', '商场', '网购', '衣服', '日用品', '商品'],
            '娱乐': ['娱乐', '电影', '游戏', 'KTV', '旅游', '休闲', '娱乐'],
            '医疗': ['医疗', '医院', '药店', '体检', '看病', '医疗'],
            '教育': ['教育', '培训', '学习', '书籍', '课程', '教育']
        }
        
        # 初始化TF-IDF向量化器
        self.vectorizer = TfidfVectorizer()
        self._build_intent_model()
    
    def _build_intent_model(self):
        """构建意图识别模型"""
        # 收集所有意图模板
        all_texts = []
        self.intent_labels = []
        
        for intent, templates in self.intent_templates.items():
            for template in templates:
                all_texts.append(template)
                self.intent_labels.append(intent)
        
        # 训练TF-IDF模型
        if all_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(all_texts)
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """解析用户查询"""
        query = query.strip()
        
        # 分词和词性标注
        words = list(jieba.cut(query))
        pos_words = list(pseg.cut(query))
        
        # 提取意图
        intent = self._extract_intent(query)
        
        # 提取时间信息
        time_info = self._extract_time_info(query, words)
        
        # 提取类别信息
        category_info = self._extract_category_info(query, words)
        
        # 提取商家信息
        merchant_info = self._extract_merchant_info(query, words)
        
        # 提取金额信息
        amount_info = self._extract_amount_info(query, words)
        
        return {
            'original_query': query,
            'words': words,
            'pos_words': [(word, flag) for word, flag in pos_words],
            'intent': intent,
            'time_info': time_info,
            'category_info': category_info,
            'merchant_info': merchant_info,
            'amount_info': amount_info,
            'parsed_at': datetime.now().isoformat()
        }
    
    def _extract_intent(self, query: str) -> str:
        """提取查询意图"""
        if not hasattr(self, 'tfidf_matrix'):
            return 'unknown'
        
        # 使用TF-IDF计算相似度
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # 找到最相似的意图
        max_similarity_idx = np.argmax(similarities)
        max_similarity = similarities[max_similarity_idx]
        
        # 如果相似度太低，返回unknown
        if max_similarity < 0.3:
            return 'unknown'
        
        return self.intent_labels[max_similarity_idx]
    
    def _extract_time_info(self, query: str, words: List[str]) -> Dict[str, Any]:
        """提取时间信息"""
        time_info = {
            'type': 'none',
            'start_date': None,
            'end_date': None,
            'time_range': None
        }
        
        # 检查时间关键词
        for keyword, days_offset in self.time_keywords.items():
            if keyword in query:
                if days_offset == 0:  # 今天
                    time_info['type'] = 'single_day'
                    time_info['start_date'] = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    time_info['end_date'] = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                elif days_offset > 0:  # 时间段
                    time_info['type'] = 'range'
                    time_info['start_date'] = datetime.now() - timedelta(days=days_offset)
                    time_info['end_date'] = datetime.now()
                else:  # 具体某天
                    time_info['type'] = 'single_day'
                    target_date = datetime.now() + timedelta(days=days_offset)
                    time_info['start_date'] = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    time_info['end_date'] = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                break
        
        # 检查月份信息
        month_pattern = r'(\d{1,2})月'
        month_match = re.search(month_pattern, query)
        if month_match:
            month = int(month_match.group(1))
            current_year = datetime.now().year
            time_info['type'] = 'month'
            time_info['start_date'] = datetime(current_year, month, 1)
            if month == 12:
                time_info['end_date'] = datetime(current_year + 1, 1, 1) - timedelta(days=1)
            else:
                time_info['end_date'] = datetime(current_year, month + 1, 1) - timedelta(days=1)
        
        return time_info
    
    def _extract_category_info(self, query: str, words: List[str]) -> Dict[str, Any]:
        """提取类别信息"""
        category_info = {
            'category': None,
            'confidence': 0.0
        }
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    category_info['category'] = category
                    category_info['confidence'] = 1.0
                    break
            if category_info['category']:
                break
        
        return category_info
    
    def _extract_merchant_info(self, query: str, words: List[str]) -> Dict[str, Any]:
        """提取商家信息"""
        merchant_info = {
            'merchant': None,
            'confidence': 0.0
        }
        
        # 简单的商家名称提取（可以根据实际需求优化）
        # 这里假设商家名称通常是名词
        for word, pos in pseg.cut(query):
            if pos in ['n', 'nr', 'ns', 'nt'] and len(word) > 1:
                # 检查是否可能是商家名称
                if word not in ['时间', '金额', '消费', '支出', '费用']:
                    merchant_info['merchant'] = word
                    merchant_info['confidence'] = 0.8
                    break
        
        return merchant_info
    
    def _extract_amount_info(self, query: str, words: List[str]) -> Dict[str, Any]:
        """提取金额信息"""
        amount_info = {
            'amount': None,
            'operator': None,  # '>', '<', '=', 'range'
            'min_amount': None,
            'max_amount': None
        }
        
        # 提取数字
        amount_pattern = r'(\d+(?:\.\d+)?)'
        amounts = re.findall(amount_pattern, query)
        
        if amounts:
            amounts = [float(amount) for amount in amounts]
            
            if '超过' in query or '大于' in query or '>' in query:
                amount_info['operator'] = '>'
                amount_info['min_amount'] = max(amounts)
            elif '少于' in query or '小于' in query or '<' in query:
                amount_info['operator'] = '<'
                amount_info['max_amount'] = min(amounts)
            elif '到' in query or '-' in query or '~' in query:
                amount_info['operator'] = 'range'
                amount_info['min_amount'] = min(amounts)
                amount_info['max_amount'] = max(amounts)
            else:
                amount_info['operator'] = '='
                amount_info['amount'] = amounts[0]
        
        return amount_info
    
    def execute_query(self, parsed_query: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
        """执行查询"""
        intent = parsed_query['intent']
        time_info = parsed_query['time_info']
        category_info = parsed_query['category_info']
        merchant_info = parsed_query['merchant_info']
        amount_info = parsed_query['amount_info']
        
        # 根据意图执行不同的查询
        if intent == 'query_amount':
            return self._query_total_amount(user_id, time_info, category_info, merchant_info)
        elif intent == 'query_category':
            return self._query_category_amount(user_id, time_info, category_info)
        elif intent == 'query_time':
            return self._query_time_amount(user_id, time_info)
        elif intent == 'query_merchant':
            return self._query_merchant_amount(user_id, time_info, merchant_info)
        elif intent == 'query_trend':
            return self._query_trend_analysis(user_id, time_info)
        elif intent == 'query_comparison':
            return self._query_comparison(user_id, time_info)
        else:
            return self._query_general(user_id, time_info, category_info, merchant_info, amount_info)
    
    def _query_total_amount(self, user_id: int, time_info: Dict, category_info: Dict, merchant_info: Dict) -> Dict[str, Any]:
        """查询总金额"""
        start_date = time_info.get('start_date')
        end_date = time_info.get('end_date')
        
        # 获取消费汇总
        summary = db_manager.get_spending_summary(user_id, start_date, end_date)
        
        # 根据类别和商家过滤
        bills = db_manager.get_bills(user_id, limit=1000)
        
        if category_info.get('category'):
            bills = [bill for bill in bills if bill.category == category_info['category']]
        
        if merchant_info.get('merchant'):
            bills = [bill for bill in bills if merchant_info['merchant'] in bill.merchant]
        
        # 重新计算金额
        total_amount = sum(bill.amount for bill in bills)
        count = len(bills)
        
        return {
            'query_type': 'total_amount',
            'total_amount': total_amount,
            'count': count,
            'avg_amount': total_amount / count if count > 0 else 0,
            'time_range': f"{start_date.strftime('%Y-%m-%d') if start_date else '全部'} 到 {end_date.strftime('%Y-%m-%d') if end_date else '现在'}",
            'filters': {
                'category': category_info.get('category'),
                'merchant': merchant_info.get('merchant')
            }
        }
    
    def _query_category_amount(self, user_id: int, time_info: Dict, category_info: Dict) -> Dict[str, Any]:
        """查询分类金额"""
        category = category_info.get('category', '全部')
        start_date = time_info.get('start_date')
        end_date = time_info.get('end_date')
        
        if category == '全部':
            # 查询所有分类
            category_data = db_manager.get_category_spending(user_id, start_date, end_date)
            return {
                'query_type': 'category_amount',
                'category': '全部',
                'data': category_data,
                'total_amount': sum(item['total_amount'] for item in category_data)
            }
        else:
            # 查询特定分类
            bills = db_manager.get_bills_by_category(user_id, category)
            if start_date and end_date:
                bills = [bill for bill in bills if start_date <= bill.consume_time <= end_date]
            
            total_amount = sum(bill.amount for bill in bills)
            return {
                'query_type': 'category_amount',
                'category': category,
                'total_amount': total_amount,
                'count': len(bills),
                'avg_amount': total_amount / len(bills) if bills else 0
            }
    
    def _query_time_amount(self, user_id: int, time_info: Dict) -> Dict[str, Any]:
        """查询时间金额"""
        start_date = time_info.get('start_date')
        end_date = time_info.get('end_date')
        
        if not start_date or not end_date:
            # 如果没有具体时间，返回最近30天
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        bills = db_manager.get_bills_by_date_range(user_id, start_date, end_date)
        total_amount = sum(bill.amount for bill in bills)
        
        return {
            'query_type': 'time_amount',
            'total_amount': total_amount,
            'count': len(bills),
            'avg_amount': total_amount / len(bills) if bills else 0,
            'time_range': f"{start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}"
        }
    
    def _query_merchant_amount(self, user_id: int, time_info: Dict, merchant_info: Dict) -> Dict[str, Any]:
        """查询商家金额"""
        merchant = merchant_info.get('merchant')
        if not merchant:
            return {'error': '未找到商家信息'}
        
        bills = db_manager.get_bills_by_merchant(user_id, merchant)
        
        if time_info.get('start_date') and time_info.get('end_date'):
            bills = [bill for bill in bills if time_info['start_date'] <= bill.consume_time <= time_info['end_date']]
        
        total_amount = sum(bill.amount for bill in bills)
        
        return {
            'query_type': 'merchant_amount',
            'merchant': merchant,
            'total_amount': total_amount,
            'count': len(bills),
            'avg_amount': total_amount / len(bills) if bills else 0
        }
    
    def _query_trend_analysis(self, user_id: int, time_info: Dict) -> Dict[str, Any]:
        """查询趋势分析"""
        # 获取月度数据
        current_year = datetime.now().year
        monthly_data = db_manager.get_monthly_spending(user_id, current_year)
        
        return {
            'query_type': 'trend_analysis',
            'monthly_data': monthly_data,
            'total_amount': sum(item['total_amount'] for item in monthly_data),
            'avg_monthly': sum(item['total_amount'] for item in monthly_data) / len(monthly_data) if monthly_data else 0
        }
    
    def _query_comparison(self, user_id: int, time_info: Dict) -> Dict[str, Any]:
        """查询对比分析"""
        # 获取当前月和上个月的数据
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if now.month == 1:
            last_month_start = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            last_month_start = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_bills = db_manager.get_bills_by_date_range(user_id, current_month_start, now)
        last_month_bills = db_manager.get_bills_by_date_range(user_id, last_month_start, current_month_start)
        
        current_amount = sum(bill.amount for bill in current_month_bills)
        last_amount = sum(bill.amount for bill in last_month_bills)
        
        change_amount = current_amount - last_amount
        change_percent = (change_amount / last_amount * 100) if last_amount > 0 else 0
        
        return {
            'query_type': 'comparison',
            'current_month': {
                'amount': current_amount,
                'count': len(current_month_bills)
            },
            'last_month': {
                'amount': last_amount,
                'count': len(last_month_bills)
            },
            'change': {
                'amount': change_amount,
                'percent': change_percent
            }
        }
    
    def _query_general(self, user_id: int, time_info: Dict, category_info: Dict, merchant_info: Dict, amount_info: Dict) -> Dict[str, Any]:
        """通用查询"""
        # 获取基础数据
        start_date = time_info.get('start_date')
        end_date = time_info.get('end_date')
        
        if start_date and end_date:
            bills = db_manager.get_bills_by_date_range(user_id, start_date, end_date)
        else:
            bills = db_manager.get_bills(user_id, limit=1000)
        
        # 应用过滤条件
        if category_info.get('category'):
            bills = [bill for bill in bills if bill.category == category_info['category']]
        
        if merchant_info.get('merchant'):
            bills = [bill for bill in bills if merchant_info['merchant'] in bill.merchant]
        
        if amount_info.get('amount'):
            if amount_info['operator'] == '>':
                bills = [bill for bill in bills if bill.amount > amount_info['min_amount']]
            elif amount_info['operator'] == '<':
                bills = [bill for bill in bills if bill.amount < amount_info['max_amount']]
            elif amount_info['operator'] == 'range':
                bills = [bill for bill in bills if amount_info['min_amount'] <= bill.amount <= amount_info['max_amount']]
            else:
                bills = [bill for bill in bills if abs(bill.amount - amount_info['amount']) < 0.01]
        
        total_amount = sum(bill.amount for bill in bills)
        
        return {
            'query_type': 'general',
            'total_amount': total_amount,
            'count': len(bills),
            'avg_amount': total_amount / len(bills) if bills else 0,
            'bills': bills[:10],  # 只返回前10条记录
            'filters': {
                'time': time_info,
                'category': category_info,
                'merchant': merchant_info,
                'amount': amount_info
            }
        }

# 创建全局查询处理器实例
query_processor = BillQueryProcessor()
