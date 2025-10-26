"""
数据清洗模块
"""
import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import jieba
from .config import CLEANING_CONFIG

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.config = CLEANING_CONFIG
        # 初始化jieba分词
        jieba.initialize()
    
    def clean_bill_data(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗账单数据"""
        cleaned_data = bill_data.copy()
        
        # 清洗金额
        if 'amount' in cleaned_data:
            cleaned_data['amount'] = self._clean_amount(cleaned_data['amount'])
        
        # 清洗时间
        if 'consume_time' in cleaned_data:
            cleaned_data['consume_time'] = self._clean_datetime(cleaned_data['consume_time'])
        
        # 清洗商家名称
        if 'merchant' in cleaned_data:
            cleaned_data['merchant'] = self._clean_merchant(cleaned_data['merchant'])
        
        # 清洗类别
        if 'category' in cleaned_data:
            cleaned_data['category'] = self._clean_category(cleaned_data['category'])
        
        # 清洗支付方式
        if 'payment_method' in cleaned_data:
            cleaned_data['payment_method'] = self._clean_payment_method(cleaned_data['payment_method'])
        
        # 清洗描述
        if 'description' in cleaned_data:
            cleaned_data['description'] = self._clean_description(cleaned_data['description'])
        
        return cleaned_data
    
    def _clean_amount(self, amount: Any) -> float:
        """清洗金额数据"""
        if isinstance(amount, (int, float)):
            amount = float(amount)
        elif isinstance(amount, str):
            # 提取数字
            amount_str = re.sub(r'[^\d.-]', '', amount)
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
        
        # 验证金额范围
        if amount < self.config['min_amount']:
            amount = self.config['min_amount']
        elif amount > self.config['max_amount']:
            amount = self.config['max_amount']
        
        return round(amount, 2)
    
    def _clean_datetime(self, datetime_str: Any) -> datetime:
        """清洗时间数据"""
        if isinstance(datetime_str, datetime):
            return datetime_str
        
        if isinstance(datetime_str, str):
            # 尝试多种时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败，返回当前时间
            return datetime.now()
        
        return datetime.now()
    
    def _clean_merchant(self, merchant: str) -> str:
        """清洗商家名称"""
        if not merchant or not isinstance(merchant, str):
            return "未知商家"
        
        # 去除多余空格和特殊字符
        merchant = re.sub(r'\s+', ' ', merchant.strip())
        merchant = re.sub(r'[^\w\s\u4e00-\u9fff]', '', merchant)
        
        # 如果为空，返回默认值
        if not merchant:
            return "未知商家"
        
        return merchant
    
    def _clean_category(self, category: str) -> str:
        """清洗消费类别"""
        if not category or not isinstance(category, str):
            return "未知"
        
        category = category.strip()
        
        # 标准化类别名称
        category_mapping = {
            '餐饮': ['餐饮', '吃饭', '餐厅', '外卖', '咖啡', '奶茶', '快餐'],
            '交通': ['交通', '打车', '地铁', '公交', '加油', '停车', '出行'],
            '购物': ['购物', '超市', '商场', '网购', '衣服', '日用品'],
            '娱乐': ['娱乐', '电影', '游戏', 'KTV', '旅游', '休闲'],
            '医疗': ['医疗', '医院', '药店', '体检', '看病'],
            '教育': ['教育', '培训', '学习', '书籍', '课程'],
            '其他': ['其他', '未知', '杂项']
        }
        
        for standard_category, keywords in category_mapping.items():
            if any(keyword in category for keyword in keywords):
                return standard_category
        
        # 如果不在映射中，检查是否在配置的类别列表中
        if category in self.config['categories']:
            return category
        
        return "其他"
    
    def _clean_payment_method(self, payment_method: str) -> str:
        """清洗支付方式"""
        if not payment_method or not isinstance(payment_method, str):
            return "其他"
        
        payment_method = payment_method.strip()
        
        # 标准化支付方式
        payment_mapping = {
            '微信': ['微信', 'wechat', 'weixin'],
            '支付宝': ['支付宝', 'alipay', 'zfb'],
            '银行卡': ['银行卡', '银行', 'card', '借记卡', '信用卡'],
            '现金': ['现金', 'cash'],
            '其他': ['其他', '未知']
        }
        
        for standard_method, keywords in payment_mapping.items():
            if any(keyword in payment_method.lower() for keyword in keywords):
                return standard_method
        
        return "其他"
    
    def _clean_description(self, description: str) -> str:
        """清洗描述信息"""
        if not description or not isinstance(description, str):
            return ""
        
        # 去除多余空格和换行
        description = re.sub(r'\s+', ' ', description.strip())
        
        # 限制长度
        if len(description) > 500:
            description = description[:500] + "..."
        
        return description
    
    def detect_anomalies(self, bills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测异常数据"""
        anomalies = []
        
        if not bills:
            return anomalies
        
        # 转换为DataFrame便于分析
        df = pd.DataFrame(bills)
        
        # 检测异常金额
        if 'amount' in df.columns:
            amount_mean = df['amount'].mean()
            amount_std = df['amount'].std()
            
            # 使用3σ原则检测异常值
            threshold = amount_mean + 3 * amount_std
            anomaly_bills = df[df['amount'] > threshold]
            
            for _, bill in anomaly_bills.iterrows():
                anomalies.append({
                    'type': 'amount_anomaly',
                    'bill_id': bill.get('id'),
                    'value': bill['amount'],
                    'threshold': threshold,
                    'description': f"金额异常：{bill['amount']}元，超过阈值{threshold:.2f}元"
                })
        
        # 检测重复数据
        if 'merchant' in df.columns and 'amount' in df.columns:
            duplicate_groups = df.groupby(['merchant', 'amount']).size()
            duplicate_groups = duplicate_groups[duplicate_groups > 1]
            
            for (merchant, amount), count in duplicate_groups.items():
                duplicate_bills = df[(df['merchant'] == merchant) & (df['amount'] == amount)]
                for _, bill in duplicate_bills.iterrows():
                    anomalies.append({
                        'type': 'duplicate',
                        'bill_id': bill.get('id'),
                        'merchant': merchant,
                        'amount': amount,
                        'count': count,
                        'description': f"重复数据：{merchant} {amount}元，共{count}条"
                    })
        
        return anomalies
    
    def validate_data_quality(self, bills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证数据质量"""
        if not bills:
            return {
                'total_count': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'quality_score': 0.0,
                'issues': []
            }
        
        total_count = len(bills)
        valid_count = 0
        issues = []
        
        for bill in bills:
            is_valid = True
            
            # 检查必填字段
            required_fields = ['consume_time', 'amount', 'merchant', 'payment_method']
            for field in required_fields:
                if field not in bill or not bill[field]:
                    is_valid = False
                    issues.append(f"缺少必填字段：{field}")
            
            # 检查金额有效性
            if 'amount' in bill:
                try:
                    amount = float(bill['amount'])
                    if amount <= 0:
                        is_valid = False
                        issues.append(f"金额无效：{amount}")
                except (ValueError, TypeError):
                    is_valid = False
                    issues.append(f"金额格式错误：{bill['amount']}")
            
            # 检查时间有效性
            if 'consume_time' in bill:
                try:
                    if isinstance(bill['consume_time'], str):
                        datetime.strptime(bill['consume_time'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    is_valid = False
                    issues.append(f"时间格式错误：{bill['consume_time']}")
            
            if is_valid:
                valid_count += 1
        
        quality_score = valid_count / total_count if total_count > 0 else 0.0
        
        return {
            'total_count': total_count,
            'valid_count': valid_count,
            'invalid_count': total_count - valid_count,
            'quality_score': quality_score,
            'issues': issues[:10]  # 只返回前10个问题
        }
    
    def generate_cleaning_report(self, bills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据清洗报告"""
        # 数据质量验证
        quality_report = self.validate_data_quality(bills)
        
        # 异常检测
        anomalies = self.detect_anomalies(bills)
        
        # 统计信息
        if bills:
            df = pd.DataFrame(bills)
            stats = {
                'total_amount': df['amount'].sum() if 'amount' in df.columns else 0,
                'avg_amount': df['amount'].mean() if 'amount' in df.columns else 0,
                'category_distribution': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
                'payment_method_distribution': df['payment_method'].value_counts().to_dict() if 'payment_method' in df.columns else {}
            }
        else:
            stats = {
                'total_amount': 0,
                'avg_amount': 0,
                'category_distribution': {},
                'payment_method_distribution': {}
            }
        
        return {
            'quality_report': quality_report,
            'anomalies': anomalies,
            'statistics': stats,
            'cleaning_timestamp': datetime.now().isoformat()
        }

# 创建全局数据清洗器实例
data_cleaner = DataCleaner()
