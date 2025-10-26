"""
发票OCR模块 - 发票识别和分类
"""
import re
import jieba
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

from .database import db_manager
from .data_cleaning import data_cleaner
from .config import CLEANING_CONFIG

class InvoiceOCRProcessor:
    """发票OCR处理器"""
    
    def __init__(self):
        self.config = CLEANING_CONFIG
        # 初始化jieba
        jieba.initialize()
        
        # 发票类型分类器
        self.classifier = None
        self.vectorizer = None
        self._load_classifier()
    
    def _load_classifier(self):
        """加载发票分类器"""
        model_path = "data/models/invoice_classifier.pkl"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                print("发票分类器加载成功")
            except Exception as e:
                print(f"发票分类器加载失败: {e}")
                self._train_default_classifier()
        else:
            self._train_default_classifier()
    
    def _train_default_classifier(self):
        """训练默认分类器"""
        # 创建训练数据
        training_data = self._create_training_data()
        
        if training_data:
            # 准备训练数据
            texts = [item['text'] for item in training_data]
            labels = [item['label'] for item in training_data]
            
            # 创建分类器
            self.classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000)),
                ('clf', MultinomialNB())
            ])
            
            # 训练分类器
            self.classifier.fit(texts, labels)
            
            # 保存分类器
            os.makedirs("data/models", exist_ok=True)
            with open("data/models/invoice_classifier.pkl", 'wb') as f:
                pickle.dump(self.classifier, f)
            
            print("默认发票分类器训练完成")
    
    def _create_training_data(self) -> List[Dict[str, Any]]:
        """创建训练数据"""
        training_data = [
            # 餐饮发票
            {'text': '餐饮服务 星巴克 咖啡 35.50元', 'label': '餐饮'},
            {'text': '餐饮费 麦当劳 汉堡 28.00元', 'label': '餐饮'},
            {'text': '餐饮发票 肯德基 炸鸡 45.00元', 'label': '餐饮'},
            {'text': '餐厅消费 海底捞 火锅 168.00元', 'label': '餐饮'},
            {'text': '外卖费 美团 午餐 25.00元', 'label': '餐饮'},
            
            # 交通发票
            {'text': '交通费 滴滴出行 打车 15.50元', 'label': '交通'},
            {'text': '出租车费 出租车 出行 22.00元', 'label': '交通'},
            {'text': '地铁费 地铁 通勤 6.00元', 'label': '交通'},
            {'text': '加油费 中石化 汽油 200.00元', 'label': '交通'},
            {'text': '停车费 停车场 停车 10.00元', 'label': '交通'},
            
            # 购物发票
            {'text': '商品销售 淘宝 网购 89.00元', 'label': '购物'},
            {'text': '零售商品 京东 电子产品 299.00元', 'label': '购物'},
            {'text': '超市购物 沃尔玛 日用品 156.00元', 'label': '购物'},
            {'text': '服装销售 优衣库 衣服 199.00元', 'label': '购物'},
            {'text': '百货商品 商场 化妆品 88.00元', 'label': '购物'},
            
            # 娱乐发票
            {'text': '娱乐服务 电影院 电影票 35.00元', 'label': '娱乐'},
            {'text': 'KTV消费 钱柜 唱歌 128.00元', 'label': '娱乐'},
            {'text': '游戏充值 腾讯游戏 游戏币 50.00元', 'label': '娱乐'},
            {'text': '旅游服务 携程 酒店 299.00元', 'label': '娱乐'},
            {'text': '健身服务 健身房 会员费 200.00元', 'label': '娱乐'},
            
            # 医疗发票
            {'text': '医疗服务 医院 挂号费 15.00元', 'label': '医疗'},
            {'text': '药品销售 药店 药品 45.00元', 'label': '医疗'},
            {'text': '体检费 体检中心 体检 200.00元', 'label': '医疗'},
            {'text': '医疗费 诊所 看病 80.00元', 'label': '医疗'},
            
            # 教育发票
            {'text': '教育服务 培训机构 课程费 500.00元', 'label': '教育'},
            {'text': '图书销售 书店 书籍 68.00元', 'label': '教育'},
            {'text': '培训费 英语培训 学费 800.00元', 'label': '教育'},
            {'text': '考试费 考试中心 报名费 100.00元', 'label': '教育'},
        ]
        
        return training_data
    
    def process_invoice_text(self, ocr_text: str) -> Dict[str, Any]:
        """处理发票OCR文本"""
        if not ocr_text or not isinstance(ocr_text, str):
            return {
                'error': '无效的OCR文本',
                'extracted_info': {},
                'classification': '未知'
            }
        
        # 提取发票信息
        extracted_info = self._extract_invoice_info(ocr_text)
        
        # 分类发票类型
        invoice_type = self._classify_invoice_type(ocr_text)
        
        # 清洗提取的信息
        cleaned_info = data_cleaner.clean_bill_data(extracted_info)
        
        return {
            'extracted_info': cleaned_info,
            'classification': invoice_type,
            'confidence': self._calculate_confidence(ocr_text, invoice_type),
            'processed_at': datetime.now().isoformat()
        }
    
    def _extract_invoice_info(self, ocr_text: str) -> Dict[str, Any]:
        """从OCR文本中提取发票信息"""
        info = {
            'merchant': '未知商家',
            'amount': 0.0,
            'invoice_time': datetime.now(),
            'description': ocr_text
        }
        
        # 提取金额
        amount_patterns = [
            r'(\d+\.?\d*)\s*元',
            r'金额[：:]\s*(\d+\.?\d*)',
            r'总计[：:]\s*(\d+\.?\d*)',
            r'合计[：:]\s*(\d+\.?\d*)',
            r'￥\s*(\d+\.?\d*)',
            r'¥\s*(\d+\.?\d*)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                try:
                    info['amount'] = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        # 提取商家名称
        merchant_patterns = [
            r'商户[：:]\s*([^\n\r]+)',
            r'商家[：:]\s*([^\n\r]+)',
            r'店铺[：:]\s*([^\n\r]+)',
            r'单位[：:]\s*([^\n\r]+)'
        ]
        
        for pattern in merchant_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                info['merchant'] = match.group(1).strip()
                break
        
        # 如果没有找到明确的商家，尝试从文本中提取可能的商家名称
        if info['merchant'] == '未知商家':
            # 使用jieba分词提取可能的商家名称
            words = list(jieba.cut(ocr_text))
            for word in words:
                if len(word) > 1 and word not in ['发票', '金额', '时间', '日期', '总计', '合计']:
                    # 简单的商家名称判断
                    if any(char in word for char in ['店', '馆', '厅', '楼', '中心', '公司', '集团']):
                        info['merchant'] = word
                        break
        
        # 提取时间
        time_patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'日期[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                try:
                    time_str = match.group(1)
                    # 处理不同的时间格式
                    if '年' in time_str and '月' in time_str and '日' in time_str:
                        time_str = time_str.replace('年', '-').replace('月', '-').replace('日', '')
                    
                    info['invoice_time'] = datetime.strptime(time_str, '%Y-%m-%d')
                    break
                except ValueError:
                    continue
        
        return info
    
    def _classify_invoice_type(self, ocr_text: str) -> str:
        """分类发票类型"""
        if not self.classifier:
            return self._rule_based_classification(ocr_text)
        
        try:
            # 使用机器学习分类器
            prediction = self.classifier.predict([ocr_text])[0]
            confidence = self.classifier.predict_proba([ocr_text]).max()
            
            # 如果置信度太低，使用规则分类
            if confidence < 0.5:
                return self._rule_based_classification(ocr_text)
            
            return prediction
        except Exception as e:
            print(f"分类器预测失败: {e}")
            return self._rule_based_classification(ocr_text)
    
    def _rule_based_classification(self, ocr_text: str) -> str:
        """基于规则的发票分类"""
        text_lower = ocr_text.lower()
        
        # 定义关键词映射
        category_keywords = {
            '餐饮': ['餐饮', '餐厅', '饭店', '咖啡', '奶茶', '快餐', '外卖', '美食', '星巴克', '麦当劳', '肯德基', '海底捞'],
            '交通': ['交通', '打车', '出租车', '地铁', '公交', '加油', '停车', '出行', '滴滴', 'uber'],
            '购物': ['购物', '超市', '商场', '网购', '淘宝', '京东', '衣服', '日用品', '商品', '零售'],
            '娱乐': ['娱乐', '电影', '游戏', 'ktv', '旅游', '休闲', '健身', '电影院', '网吧'],
            '医疗': ['医疗', '医院', '药店', '体检', '看病', '药品', '诊所', '卫生'],
            '教育': ['教育', '培训', '学习', '书籍', '课程', '学校', '考试', '学费']
        }
        
        # 计算每个类别的匹配分数
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score
        
        # 返回得分最高的类别
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return '其他'
    
    def _calculate_confidence(self, ocr_text: str, invoice_type: str) -> float:
        """计算分类置信度"""
        if not self.classifier:
            # 基于规则的置信度计算
            return 0.6 if invoice_type != '其他' else 0.3
        
        try:
            # 使用分类器的预测概率
            probabilities = self.classifier.predict_proba([ocr_text])[0]
            classes = self.classifier.classes_
            
            if invoice_type in classes:
                type_index = list(classes).index(invoice_type)
                return float(probabilities[type_index])
            else:
                return 0.5
        except Exception:
            return 0.5
    
    def create_invoice_record(self, ocr_text: str, file_path: str = None, user_id: int = 1) -> Dict[str, Any]:
        """创建发票记录"""
        # 处理OCR文本
        processed_result = self.process_invoice_text(ocr_text)
        
        if 'error' in processed_result:
            return processed_result
        
        extracted_info = processed_result['extracted_info']
        invoice_type = processed_result['classification']
        confidence = processed_result['confidence']
        
        # 创建发票记录数据
        invoice_data = {
            'user_id': user_id,
            'invoice_time': extracted_info.get('invoice_time', datetime.now()),
            'amount': extracted_info.get('amount', 0.0),
            'merchant': extracted_info.get('merchant', '未知商家'),
            'invoice_type': invoice_type,
            'ocr_text': ocr_text,
            'file_path': file_path
        }
        
        # 保存到数据库
        try:
            invoice = db_manager.create_invoice(invoice_data)
            return {
                'success': True,
                'invoice_id': invoice.id,
                'extracted_info': extracted_info,
                'classification': invoice_type,
                'confidence': confidence,
                'message': '发票记录创建成功'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'创建发票记录失败: {str(e)}',
                'extracted_info': extracted_info,
                'classification': invoice_type
            }
    
    def batch_process_invoices(self, invoice_texts: List[str], user_id: int = 1) -> List[Dict[str, Any]]:
        """批量处理发票"""
        results = []
        
        for i, ocr_text in enumerate(invoice_texts):
            try:
                result = self.create_invoice_record(ocr_text, user_id=user_id)
                results.append({
                    'index': i,
                    'success': result.get('success', False),
                    'invoice_id': result.get('invoice_id'),
                    'classification': result.get('classification', '未知'),
                    'confidence': result.get('confidence', 0.0),
                    'error': result.get('error')
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'error': f'处理失败: {str(e)}',
                    'classification': '未知',
                    'confidence': 0.0
                })
        
        return results
    
    def get_invoice_statistics(self, user_id: int = 1) -> Dict[str, Any]:
        """获取发票统计信息"""
        invoices = db_manager.get_invoices(user_id)
        
        if not invoices:
            return {
                'total_count': 0,
                'total_amount': 0,
                'type_distribution': {},
                'confidence_stats': {}
            }
        
        # 统计信息
        total_count = len(invoices)
        total_amount = sum(invoice.amount for invoice in invoices)
        
        # 类型分布
        type_distribution = {}
        for invoice in invoices:
            invoice_type = invoice.invoice_type or '未知'
            if invoice_type not in type_distribution:
                type_distribution[invoice_type] = {'count': 0, 'amount': 0}
            type_distribution[invoice_type]['count'] += 1
            type_distribution[invoice_type]['amount'] += invoice.amount
        
        return {
            'total_count': total_count,
            'total_amount': total_amount,
            'avg_amount': total_amount / total_count if total_count > 0 else 0,
            'type_distribution': type_distribution,
            'recent_invoices': [
                {
                    'id': invoice.id,
                    'merchant': invoice.merchant,
                    'amount': invoice.amount,
                    'type': invoice.invoice_type,
                    'time': invoice.invoice_time.isoformat()
                }
                for invoice in invoices[:5]
            ]
        }

# 创建全局OCR处理器实例
invoice_ocr_processor = InvoiceOCRProcessor()
