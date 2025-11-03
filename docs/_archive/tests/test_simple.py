"""
简化测试脚本 - 不依赖外部包
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_simple_database():
    """创建简化的数据库"""
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect("data/bill_db.sqlite")
    cursor = conn.cursor()
    
    # 删除已存在的表（如果有）
    cursor.execute("DROP TABLE IF EXISTS bills")
    cursor.execute("DROP TABLE IF EXISTS invoices")
    cursor.execute("DROP TABLE IF EXISTS financial_products")
    
    # 创建账单表
    cursor.execute('''
        CREATE TABLE bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consume_time TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            category TEXT DEFAULT '未知',
            payment_method TEXT NOT NULL,
            location TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建发票表
    cursor.execute('''
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            invoice_time TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            invoice_type TEXT DEFAULT '未知',
            ocr_text TEXT,
            file_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建金融产品表
    cursor.execute('''
        CREATE TABLE financial_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT NOT NULL,
            product_name TEXT NOT NULL,
            interest_rate REAL,
            min_amount REAL,
            max_amount REAL,
            term_months INTEGER,
            risk_level TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("数据库表创建成功")
    return conn

def generate_test_data(conn):
    """生成测试数据"""
    cursor = conn.cursor()
    
    # 商家数据
    merchants = {
        '餐饮': ['星巴克', '麦当劳', '肯德基', '海底捞', '必胜客'],
        '交通': ['滴滴出行', 'Uber', '出租车', '地铁', '公交'],
        '购物': ['淘宝', '京东', '天猫', '沃尔玛', '家乐福'],
        '娱乐': ['电影院', 'KTV', '网吧', '游乐场', '健身房'],
        '医疗': ['人民医院', '药店', '体检中心', '诊所'],
        '教育': ['新东方', '学而思', '新华书店', '培训机构']
    }
    
    payment_methods = ['微信', '支付宝', '银行卡', '现金']
    
    # 生成账单数据
    print("生成账单数据...")
    for i in range(50):
        category = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[category])
        amount = round(random.uniform(10, 500), 2)
        
        # 生成时间（最近30天）
        days_ago = random.randint(0, 30)
        consume_time = datetime.now() - timedelta(days=days_ago)
        
        payment_method = random.choice(payment_methods)
        
        cursor.execute('''
            INSERT INTO bills (user_id, consume_time, amount, merchant, category, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, consume_time.isoformat(), amount, merchant, category, payment_method))
    
    # 生成发票数据
    print("生成发票数据...")
    for i in range(20):
        category = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[category])
        amount = round(random.uniform(20, 300), 2)
        
        days_ago = random.randint(0, 30)
        invoice_time = datetime.now() - timedelta(days=days_ago)
        
        ocr_text = f"发票\n商户：{merchant}\n金额：{amount}元\n时间：{invoice_time.strftime('%Y年%m月%d日')}"
        
        cursor.execute('''
            INSERT INTO invoices (user_id, invoice_time, amount, merchant, invoice_type, ocr_text)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, invoice_time.isoformat(), amount, merchant, category, ocr_text))
    
    # 生成金融产品数据
    print("生成金融产品数据...")
    products = [
        ('理财', '稳健型理财产品A', 0.035, 1000, 100000, 6, 'low', '低风险稳健型理财产品'),
        ('理财', '平衡型理财产品B', 0.045, 5000, 500000, 12, 'medium', '中等风险平衡型理财产品'),
        ('贷款', '个人消费贷款', 0.065, 10000, 500000, 36, 'medium', '个人消费贷款'),
        ('保险', '意外伤害保险', None, 100, 10000, 12, 'low', '意外伤害保险'),
    ]
    
    for product in products:
        cursor.execute('''
            INSERT INTO financial_products 
            (product_type, product_name, interest_rate, min_amount, max_amount, term_months, risk_level, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', product)
    
    conn.commit()
    print("测试数据生成完成")

def test_queries(conn):
    """测试查询功能"""
    cursor = conn.cursor()
    
    print("\n=== 测试查询功能 ===")
    
    # 1. 查询总账单数
    cursor.execute("SELECT COUNT(*) FROM bills")
    bill_count = cursor.fetchone()[0]
    print(f"总账单数: {bill_count}")
    
    # 2. 查询总消费金额
    cursor.execute("SELECT SUM(amount) FROM bills")
    total_amount = cursor.fetchone()[0]
    print(f"总消费金额: {total_amount:.2f}元")
    
    # 3. 按类别统计
    cursor.execute("""
        SELECT category, COUNT(*), SUM(amount), AVG(amount)
        FROM bills 
        GROUP BY category 
        ORDER BY SUM(amount) DESC
    """)
    print("\n按类别统计:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}笔, 总计{row[2]:.2f}元, 平均{row[3]:.2f}元")
    
    # 4. 按支付方式统计
    cursor.execute("""
        SELECT payment_method, COUNT(*), SUM(amount)
        FROM bills 
        GROUP BY payment_method 
        ORDER BY SUM(amount) DESC
    """)
    print("\n按支付方式统计:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}笔, 总计{row[2]:.2f}元")
    
    # 5. 最近7天消费
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute("""
        SELECT COUNT(*), SUM(amount)
        FROM bills 
        WHERE consume_time >= ?
    """, (seven_days_ago,))
    recent = cursor.fetchone()
    print(f"\n最近7天消费: {recent[0]}笔, 总计{recent[1]:.2f}元")
    
    # 6. 查询发票统计
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM invoices")
    invoice_stats = cursor.fetchone()
    print(f"\n发票统计: {invoice_stats[0]}张, 总计{invoice_stats[1]:.2f}元")
    
    # 7. 查询金融产品
    cursor.execute("SELECT product_type, COUNT(*) FROM financial_products GROUP BY product_type")
    print("\n金融产品统计:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}个")

def main():
    """主函数"""
    print("=== 账单查询与管理系统 - 简化测试 ===")
    
    # 创建数据库
    conn = create_simple_database()
    
    # 生成测试数据
    generate_test_data(conn)
    
    # 测试查询功能
    test_queries(conn)
    
    # 关闭连接
    conn.close()
    
    print("\n=== 测试完成 ===")
    print("数据库文件: data/bill_db.sqlite")
    print("可以使用DB Browser for SQLite打开查看数据")

if __name__ == "__main__":
    main()
