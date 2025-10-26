"""
测试数据生成器 - 生成模拟账单和发票数据
"""
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager, init_database

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        # 商家数据
        self.merchants = {
            '餐饮': [
                '星巴克', '麦当劳', '肯德基', '海底捞', '必胜客', '真功夫', '永和大王',
                '沙县小吃', '兰州拉面', '重庆小面', '黄焖鸡米饭', '麻辣烫', '烧烤摊',
                '奶茶店', '咖啡厅', '西餐厅', '日料店', '韩式料理', '火锅店', '自助餐'
            ],
            '交通': [
                '滴滴出行', 'Uber', '出租车', '地铁', '公交', '共享单车', '摩拜',
                '哈啰出行', '青桔单车', '中石化', '中石油', '壳牌', 'BP加油站',
                '停车场', 'ETC', '高速费', '机场快线', '高铁', '飞机票'
            ],
            '购物': [
                '淘宝', '京东', '天猫', '拼多多', '苏宁易购', '国美', '沃尔玛',
                '家乐福', '华润万家', '永辉超市', '大润发', '优衣库', 'ZARA',
                'H&M', 'GAP', 'Nike', 'Adidas', '苹果官方', '华为官方', '小米官方'
            ],
            '娱乐': [
                '电影院', 'KTV', '网吧', '游戏厅', '游乐场', '动物园', '博物馆',
                '艺术馆', '演唱会', '话剧', '音乐会', '体育比赛', '健身房',
                '游泳馆', '瑜伽馆', '台球厅', '保龄球', '高尔夫', '滑雪场'
            ],
            '医疗': [
                '人民医院', '中医院', '妇幼保健院', '口腔医院', '眼科医院',
                '药店', '大药房', '同仁堂', '海王星辰', '益丰大药房',
                '体检中心', '诊所', '社区卫生服务中心', '急救中心'
            ],
            '教育': [
                '新东方', '学而思', '好未来', '英孚教育', '华尔街英语',
                '新华书店', '当当网', '亚马逊', '图书馆', '培训机构',
                '驾校', '技能培训', '职业培训', '在线教育', 'MOOC'
            ],
            '其他': [
                '水电费', '燃气费', '物业费', '网费', '话费', '保险',
                '银行', '证券公司', '基金公司', '理财', '投资', '捐款',
                '礼金', '红包', '转账', '提现', '充值', '缴费'
            ]
        }
        
        # 支付方式
        self.payment_methods = ['微信', '支付宝', '银行卡', '现金', '其他']
        
        # 消费金额范围（按类别）
        self.amount_ranges = {
            '餐饮': (10, 200),
            '交通': (5, 100),
            '购物': (20, 2000),
            '娱乐': (30, 500),
            '医疗': (50, 1000),
            '教育': (100, 5000),
            '其他': (10, 1000)
        }
        
        # 发票类型关键词
        self.invoice_keywords = {
            '餐饮': ['餐饮服务', '餐厅', '咖啡', '奶茶', '快餐', '美食'],
            '交通': ['交通费', '打车', '出租车', '地铁', '加油', '停车'],
            '购物': ['商品销售', '零售', '网购', '超市', '商场'],
            '娱乐': ['娱乐服务', '电影', 'KTV', '游戏', '旅游'],
            '医疗': ['医疗服务', '医院', '药店', '药品', '体检'],
            '教育': ['教育服务', '培训', '学习', '书籍', '课程']
        }
    
    def generate_bills(self, user_id: int = 1, count: int = 100, days_back: int = 90) -> List[Dict[str, Any]]:
        """生成账单数据"""
        bills = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(count):
            # 随机选择类别
            category = random.choice(list(self.merchants.keys()))
            
            # 随机选择商家
            merchant = random.choice(self.merchants[category])
            
            # 生成金额
            min_amount, max_amount = self.amount_ranges[category]
            amount = round(random.uniform(min_amount, max_amount), 2)
            
            # 生成时间（在指定天数内随机）
            random_days = random.randint(0, days_back)
            random_hours = random.randint(6, 23)
            random_minutes = random.randint(0, 59)
            consume_time = start_date + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            # 随机选择支付方式
            payment_method = random.choice(self.payment_methods)
            
            # 生成位置（可选）
            locations = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']
            location = random.choice(locations) if random.random() > 0.3 else None
            
            # 生成描述（可选）
            descriptions = [
                f"在{merchant}消费",
                f"购买{category}相关商品",
                f"使用{payment_method}支付",
                f"消费时间：{consume_time.strftime('%Y-%m-%d %H:%M')}",
                None
            ]
            description = random.choice(descriptions)
            
            bill = {
                'user_id': user_id,
                'consume_time': consume_time,
                'amount': amount,
                'merchant': merchant,
                'category': category,
                'payment_method': payment_method,
                'location': location,
                'description': description
            }
            
            bills.append(bill)
        
        return bills
    
    def generate_invoices(self, user_id: int = 1, count: int = 50, days_back: int = 90) -> List[Dict[str, Any]]:
        """生成发票数据"""
        invoices = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(count):
            # 随机选择类别
            category = random.choice(list(self.merchants.keys()))
            
            # 随机选择商家
            merchant = random.choice(self.merchants[category])
            
            # 生成金额
            min_amount, max_amount = self.amount_ranges[category]
            amount = round(random.uniform(min_amount, max_amount), 2)
            
            # 生成时间
            random_days = random.randint(0, days_back)
            random_hours = random.randint(8, 20)
            random_minutes = random.randint(0, 59)
            invoice_time = start_date + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            # 生成OCR文本
            ocr_text = self._generate_ocr_text(merchant, amount, category, invoice_time)
            
            # 生成文件路径
            file_path = f"invoices/invoice_{user_id}_{i+1}.jpg"
            
            invoice = {
                'user_id': user_id,
                'invoice_time': invoice_time,
                'amount': amount,
                'merchant': merchant,
                'invoice_type': category,
                'ocr_text': ocr_text,
                'file_path': file_path
            }
            
            invoices.append(invoice)
        
        return invoices
    
    def _generate_ocr_text(self, merchant: str, amount: float, category: str, invoice_time: datetime) -> str:
        """生成OCR识别文本"""
        # 基础发票信息
        ocr_text = f"发票\n"
        ocr_text += f"商户：{merchant}\n"
        ocr_text += f"时间：{invoice_time.strftime('%Y年%m月%d日 %H:%M')}\n"
        ocr_text += f"金额：{amount:.2f}元\n"
        
        # 添加类别相关关键词
        if category in self.invoice_keywords:
            keywords = random.choice(self.invoice_keywords[category])
            ocr_text += f"服务：{keywords}\n"
        
        # 添加一些随机信息
        ocr_text += f"发票号：{random.randint(100000, 999999)}\n"
        ocr_text += f"总计：{amount:.2f}元\n"
        
        return ocr_text
    
    def generate_financial_products(self) -> List[Dict[str, Any]]:
        """生成金融产品数据"""
        products = []
        
        # 理财产品
        products.extend([
            {
                'product_type': '理财',
                'product_name': '稳健型理财产品A',
                'interest_rate': 0.035,
                'min_amount': 1000,
                'max_amount': 100000,
                'term_months': 6,
                'risk_level': 'low',
                'description': '低风险稳健型理财产品，适合保守型投资者'
            },
            {
                'product_type': '理财',
                'product_name': '平衡型理财产品B',
                'interest_rate': 0.045,
                'min_amount': 5000,
                'max_amount': 500000,
                'term_months': 12,
                'risk_level': 'medium',
                'description': '中等风险平衡型理财产品，适合稳健型投资者'
            },
            {
                'product_type': '理财',
                'product_name': '成长型理财产品C',
                'interest_rate': 0.055,
                'min_amount': 10000,
                'max_amount': 1000000,
                'term_months': 24,
                'risk_level': 'high',
                'description': '高风险高收益理财产品，适合激进型投资者'
            }
        ])
        
        # 贷款产品
        products.extend([
            {
                'product_type': '贷款',
                'product_name': '个人消费贷款',
                'interest_rate': 0.065,
                'min_amount': 10000,
                'max_amount': 500000,
                'term_months': 36,
                'risk_level': 'medium',
                'description': '个人消费贷款，用于日常消费支出'
            },
            {
                'product_type': '贷款',
                'product_name': '房屋抵押贷款',
                'interest_rate': 0.045,
                'min_amount': 100000,
                'max_amount': 5000000,
                'term_months': 240,
                'risk_level': 'low',
                'description': '房屋抵押贷款，利率较低，期限较长'
            },
            {
                'product_type': '贷款',
                'product_name': '汽车贷款',
                'interest_rate': 0.055,
                'min_amount': 50000,
                'max_amount': 1000000,
                'term_months': 60,
                'risk_level': 'medium',
                'description': '汽车贷款，专用于购买汽车'
            }
        ])
        
        # 保险产品
        products.extend([
            {
                'product_type': '保险',
                'product_name': '意外伤害保险',
                'interest_rate': None,
                'min_amount': 100,
                'max_amount': 10000,
                'term_months': 12,
                'risk_level': 'low',
                'description': '意外伤害保险，提供意外保障'
            },
            {
                'product_type': '保险',
                'product_name': '重大疾病保险',
                'interest_rate': None,
                'min_amount': 500,
                'max_amount': 50000,
                'term_months': 240,
                'risk_level': 'low',
                'description': '重大疾病保险，提供重疾保障'
            },
            {
                'product_type': '保险',
                'product_name': '投资连结保险',
                'interest_rate': 0.04,
                'min_amount': 1000,
                'max_amount': 100000,
                'term_months': 120,
                'risk_level': 'medium',
                'description': '投资连结保险，兼具保障和投资功能'
            }
        ])
        
        return products
    
    def save_to_database(self, user_id: int = 1, bill_count: int = 100, invoice_count: int = 50):
        """保存测试数据到数据库"""
        print("开始生成测试数据...")
        
        # 生成账单数据
        print(f"生成 {bill_count} 条账单数据...")
        bills = self.generate_bills(user_id, bill_count)
        
        # 保存账单数据
        for bill in bills:
            try:
                db_manager.create_bill(bill)
            except Exception as e:
                print(f"保存账单失败: {e}")
        
        print(f"成功保存 {len(bills)} 条账单数据")
        
        # 生成发票数据
        print(f"生成 {invoice_count} 条发票数据...")
        invoices = self.generate_invoices(user_id, invoice_count)
        
        # 保存发票数据
        for invoice in invoices:
            try:
                db_manager.create_invoice(invoice)
            except Exception as e:
                print(f"保存发票失败: {e}")
        
        print(f"成功保存 {len(invoices)} 条发票数据")
        
        # 生成金融产品数据
        print("生成金融产品数据...")
        products = self.generate_financial_products()
        
        # 保存金融产品数据
        for product in products:
            try:
                db_manager.create_financial_product(product)
            except Exception as e:
                print(f"保存金融产品失败: {e}")
        
        print(f"成功保存 {len(products)} 个金融产品")
        
        print("测试数据生成完成！")
    
    def generate_sample_queries(self) -> List[str]:
        """生成示例查询语句"""
        queries = [
            "今天花了多少钱",
            "昨天餐饮消费多少",
            "这周购物花了多少",
            "本月交通费多少",
            "星巴克消费了多少",
            "上个月总支出",
            "餐饮消费趋势",
            "消费分析报告",
            "支付方式统计",
            "消费类别对比"
        ]
        return queries

def main():
    """主函数"""
    # 初始化数据库
    init_database()
    
    # 创建数据生成器
    generator = TestDataGenerator()
    
    # 生成测试数据
    generator.save_to_database(
        user_id=1,
        bill_count=200,  # 生成200条账单
        invoice_count=50  # 生成50条发票
    )
    
    # 生成示例查询
    queries = generator.generate_sample_queries()
    print("\n示例查询语句:")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")

if __name__ == "__main__":
    main()
