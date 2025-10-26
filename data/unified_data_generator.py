"""
统一数据生成器 - 生成完整的测试数据
包含：用户、账单、发票、金融产品、贷款产品
"""
import sqlite3
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

class UnifiedDataGenerator:
    """统一数据生成器"""
    
    def __init__(self, db_path="data/bill_db.sqlite"):
        self.db_path = db_path
        # 获取当前文件所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.base_dir)
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/models", exist_ok=True)
        os.makedirs("data/exports", exist_ok=True)
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 读取数据库架构 - 尝试多个可能的路径
        schema_paths = [
            os.path.join(self.base_dir, "database_schema.sql"),  # 在data目录下
            os.path.join(self.parent_dir, "data", "database_schema.sql"),  # 在THE_TEAM目录下
            "data/database_schema.sql"  # 相对路径（从当前工作目录）
        ]
        
        schema_sql = None
        for schema_path in schema_paths:
            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                break
        
        if schema_sql is None:
            raise FileNotFoundError(f"找不到database_schema.sql文件，尝试过的路径: {schema_paths}")
        
        # 执行SQL创建表
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        print("数据库初始化完成")
    
    def generate_users(self, count=5) -> List[Dict[str, Any]]:
        """生成用户数据"""
        users = []
        names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]
        
        for i in range(count):
            user = {
                'username': names[i] if i < len(names) else f"用户{i+1}",
                'email': f"user{i+1}@example.com",
                'phone': f"138{random.randint(10000000, 99999999)}",
                'password_hash': f"hash_{random.randint(100000, 999999)}"
            }
            users.append(user)
        
        return users
    
    def generate_bills(self, user_count=5, bills_per_user=50) -> List[Dict[str, Any]]:
        """生成账单数据"""
        bills = []
        
        # 商家数据
        merchants = {
            '餐饮': ['星巴克', '麦当劳', '肯德基', '海底捞', '必胜客', '真功夫', '永和大王', '沙县小吃', '兰州拉面', '重庆小面'],
            '交通': ['滴滴出行', 'Uber', '出租车', '地铁', '公交', '共享单车', '摩拜', '哈啰出行', '中石化', '中石油'],
            '购物': ['淘宝', '京东', '天猫', '拼多多', '苏宁易购', '沃尔玛', '家乐福', '华润万家', '永辉超市', '大润发'],
            '娱乐': ['电影院', 'KTV', '网吧', '游乐场', '动物园', '博物馆', '艺术馆', '演唱会', '健身房', '游泳馆'],
            '医疗': ['人民医院', '中医院', '妇幼保健院', '口腔医院', '眼科医院', '药店', '大药房', '同仁堂', '体检中心', '诊所'],
            '教育': ['新东方', '学而思', '好未来', '英孚教育', '华尔街英语', '新华书店', '当当网', '图书馆', '培训机构', '驾校']
        }
        
        payment_methods = ['微信', '支付宝', '银行卡', '现金', '其他']
        locations = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']
        
        for user_id in range(1, user_count + 1):
            for i in range(bills_per_user):
                # 随机选择类别和商家
                category = random.choice(list(merchants.keys()))
                merchant = random.choice(merchants[category])
                
                # 生成金额（根据类别调整范围）
                amount_ranges = {
                    '餐饮': (10, 200),
                    '交通': (5, 100),
                    '购物': (20, 2000),
                    '娱乐': (30, 500),
                    '医疗': (50, 1000),
                    '教育': (100, 5000)
                }
                min_amount, max_amount = amount_ranges[category]
                amount = round(random.uniform(min_amount, max_amount), 2)
                
                # 生成时间（最近90天）
                days_ago = random.randint(0, 90)
                hours = random.randint(6, 23)
                minutes = random.randint(0, 59)
                consume_time = (datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')
                
                bill = {
                    'user_id': user_id,
                    'consume_time': consume_time,
                    'amount': amount,
                    'merchant': merchant,
                    'category': category,
                    'payment_method': random.choice(payment_methods),
                    'location': random.choice(locations) if random.random() > 0.3 else None,
                    'description': f"在{merchant}的{category}消费" if random.random() > 0.5 else None
                }
                bills.append(bill)
        
        return bills
    
    def generate_invoices(self, user_count=5, invoices_per_user=20) -> List[Dict[str, Any]]:
        """生成发票数据"""
        invoices = []
        
        merchants = ['星巴克', '麦当劳', '肯德基', '海底捞', '滴滴出行', '美团外卖', '淘宝', '京东', '沃尔玛', '家乐福']
        categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '教育']
        
        for user_id in range(1, user_count + 1):
            for i in range(invoices_per_user):
                # 生成时间
                days_ago = random.randint(0, 90)
                hours = random.randint(8, 20)
                minutes = random.randint(0, 59)
                invoice_time = (datetime.now() - timedelta(days=days_ago, hours=hours, minutes=minutes)).strftime('%Y-%m-%d %H:%M:%S')
                
                # 生成金额
                amount = round(random.uniform(20, 1000), 2)
                merchant = random.choice(merchants)
                category = random.choice(categories)
                
                # 生成OCR文本
                ocr_text = f"发票\\n商户：{merchant}\\n金额：{amount}元\\n时间：{invoice_time}\\n发票号：{random.randint(100000, 999999)}"
                
                invoice = {
                    'user_id': user_id,
                    'bill_id': random.randint(1, user_count * 50) if random.random() > 0.5 else None,
                    'invoice_time': invoice_time,
                    'amount': amount,
                    'merchant': merchant,
                    'invoice_type': category,
                    'ocr_text': ocr_text,
                    'image_path': f"/images/invoice_{user_id}_{i+1}.jpg",
                    'confidence': round(random.uniform(0.7, 0.95), 3)
                }
                invoices.append(invoice)
        
        return invoices
    
    def generate_financial_products(self) -> List[Dict[str, Any]]:
        """生成金融产品数据"""
        products = [
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
            },
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
            }
        ]
        return products
    
    def generate_loan_products(self) -> List[Dict[str, Any]]:
        """生成贷款产品数据"""
        products = [
            {
                'name': '个人消费贷',
                'description': '用于日常消费的信用贷款',
                'interest_rate': 6.50,
                'term_min': 12,
                'term_max': 60,
                'amount_min': 10000,
                'amount_max': 500000,
                'eligibility_criteria': json.dumps({"credit_score_min": 600, "income_proof_required": True})
            },
            {
                'name': '房屋抵押贷',
                'description': '以房产为抵押的长期贷款',
                'interest_rate': 4.90,
                'term_min': 60,
                'term_max': 360,
                'amount_min': 100000,
                'amount_max': 10000000,
                'eligibility_criteria': json.dumps({"property_type": "residential", "ltv_ratio_max": 70})
            },
            {
                'name': '小微企业贷',
                'description': '支持小微企业的经营贷款',
                'interest_rate': 8.00,
                'term_min': 6,
                'term_max': 36,
                'amount_min': 50000,
                'amount_max': 2000000,
                'eligibility_criteria': json.dumps({"business_age_min": 1, "annual_revenue_min": 500000})
            },
            {
                'name': '公务员专享贷',
                'description': '针对公务员和事业单位员工的低利率信用贷款',
                'interest_rate': 4.50,
                'term_min': 12,
                'term_max': 60,
                'amount_min': 50000,
                'amount_max': 800000,
                'eligibility_criteria': json.dumps({"employment_type": "public_sector", "credit_score_min": 620})
            },
            {
                'name': '汽车消费贷',
                'description': '用于购买新车或二手车的专项贷款',
                'interest_rate': 5.80,
                'term_min': 24,
                'term_max': 60,
                'amount_min': 30000,
                'amount_max': 1000000,
                'eligibility_criteria': json.dumps({"down_payment_ratio_min": 20, "vehicle_age_max": 5})
            }
        ]
        return products
    
    def generate_user_profiles(self, user_count=5) -> List[Dict[str, Any]]:
        """生成用户画像数据"""
        profiles = []
        
        for user_id in range(1, user_count + 1):
            # 随机生成用户画像
            income_levels = ['low', 'medium', 'high']
            risk_tolerances = ['conservative', 'moderate', 'aggressive']
            
            spending_pattern = {
                'total_amount': random.uniform(5000, 50000),
                'avg_amount': random.uniform(50, 500),
                'frequency': random.uniform(0.5, 3.0),
                'stability': random.choice(['stable', 'moderate', 'volatile'])
            }
            
            investment_preference = {
                'preferred_categories': random.sample(['餐饮', '交通', '购物', '娱乐', '医疗', '教育'], 3),
                'risk_tolerance': random.choice(risk_tolerances),
                'investment_amount': random.uniform(1000, 100000)
            }
            
            profile = {
                'user_id': user_id,
                'income_level': random.choice(income_levels),
                'spending_pattern': json.dumps(spending_pattern),
                'risk_tolerance': random.choice(risk_tolerances),
                'investment_preference': json.dumps(investment_preference),
                'credit_score': random.randint(300, 850)
            }
            profiles.append(profile)
        
        return profiles
    
    def save_to_database(self, users, bills, invoices, financial_products, loan_products, user_profiles):
        """保存数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 插入用户数据
            print("插入用户数据...")
            for user in users:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (username, email, phone, password_hash)
                    VALUES (?, ?, ?, ?)
                """, (user['username'], user['email'], user['phone'], user['password_hash']))
            
            # 插入账单数据
            print("插入账单数据...")
            for bill in bills:
                cursor.execute("""
                    INSERT INTO bills (user_id, consume_time, amount, merchant, category, payment_method, location, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill['user_id'], bill['consume_time'], bill['amount'], bill['merchant'], 
                      bill['category'], bill['payment_method'], bill['location'], bill['description']))
            
            # 插入发票数据
            print("插入发票数据...")
            for invoice in invoices:
                cursor.execute("""
                    INSERT INTO invoices (user_id, bill_id, invoice_time, amount, merchant, invoice_type, ocr_text, image_path, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (invoice['user_id'], invoice['bill_id'], invoice['invoice_time'], invoice['amount'],
                      invoice['merchant'], invoice['invoice_type'], invoice['ocr_text'], invoice['image_path'], invoice['confidence']))
            
            # 插入金融产品数据
            print("插入金融产品数据...")
            for product in financial_products:
                cursor.execute("""
                    INSERT OR REPLACE INTO financial_products (product_type, product_name, interest_rate, min_amount, max_amount, term_months, risk_level, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (product['product_type'], product['product_name'], product['interest_rate'], 
                      product['min_amount'], product['max_amount'], product['term_months'], product['risk_level'], product['description']))
            
            # 插入贷款产品数据
            print("插入贷款产品数据...")
            for product in loan_products:
                cursor.execute("""
                    INSERT OR REPLACE INTO loan_products (name, description, interest_rate, term_min, term_max, amount_min, amount_max, eligibility_criteria)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (product['name'], product['description'], product['interest_rate'], 
                      product['term_min'], product['term_max'], product['amount_min'], product['amount_max'], product['eligibility_criteria']))
            
            # 插入用户画像数据
            print("插入用户画像数据...")
            for profile in user_profiles:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_profiles (user_id, income_level, spending_pattern, risk_tolerance, investment_preference, credit_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (profile['user_id'], profile['income_level'], profile['spending_pattern'], 
                      profile['risk_tolerance'], profile['investment_preference'], profile['credit_score']))
            
            conn.commit()
            print("数据保存成功！")
            
        except Exception as e:
            print(f"保存数据时出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def generate_all_data(self, user_count=5, bills_per_user=50, invoices_per_user=20):
        """生成所有数据"""
        print("=== 统一数据生成器 ===")
        print(f"生成 {user_count} 个用户的数据...")
        
        # 初始化数据库
        self.init_database()
        
        # 生成各种数据
        users = self.generate_users(user_count)
        bills = self.generate_bills(user_count, bills_per_user)
        invoices = self.generate_invoices(user_count, invoices_per_user)
        financial_products = self.generate_financial_products()
        loan_products = self.generate_loan_products()
        user_profiles = self.generate_user_profiles(user_count)
        
        # 保存到数据库
        self.save_to_database(users, bills, invoices, financial_products, loan_products, user_profiles)
        
        # 生成统计报告
        self.generate_statistics_report()
        
        print("=== 数据生成完成 ===")
        print(f"数据库文件: {self.db_path}")
        print(f"用户数量: {len(users)}")
        print(f"账单数量: {len(bills)}")
        print(f"发票数量: {len(invoices)}")
        print(f"金融产品数量: {len(financial_products)}")
        print(f"贷款产品数量: {len(loan_products)}")
        print(f"用户画像数量: {len(user_profiles)}")
    
    def generate_statistics_report(self):
        """生成统计报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bills")
        bill_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM bills")
        total_amount = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(amount) FROM bills")
        avg_amount = cursor.fetchone()[0] or 0
        
        # 按类别统计
        cursor.execute("""
            SELECT category, COUNT(*), SUM(amount), AVG(amount)
            FROM bills 
            GROUP BY category 
            ORDER BY SUM(amount) DESC
        """)
        category_stats = cursor.fetchall()
        
        # 生成报告
        report = f"""
# 数据生成统计报告

## 基础统计
- 用户数量: {user_count}
- 账单数量: {bill_count}
- 发票数量: {invoice_count}
- 总消费金额: {total_amount:.2f}元
- 平均消费金额: {avg_amount:.2f}元

## 分类消费统计
"""
        
        for category, count, total, avg in category_stats:
            report += f"- {category}: {count}笔, 总计{total:.2f}元, 平均{avg:.2f}元\n"
        
        report += f"""
## 生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文件位置
- 数据库: {self.db_path}
- 导出目录: data/exports/
"""
        
        # 保存报告 - 使用绝对路径
        export_dir = os.path.join(self.parent_dir, "data", "exports")
        os.makedirs(export_dir, exist_ok=True)
        report_path = os.path.join(export_dir, "statistics_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"统计报告已保存到: {report_path}")
        
        conn.close()

def main():
    """主函数"""
    generator = UnifiedDataGenerator()
    generator.generate_all_data(
        user_count=5,
        bills_per_user=100,
        invoices_per_user=30
    )

if __name__ == "__main__":
    main()
