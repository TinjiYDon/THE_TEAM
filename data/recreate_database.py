"""
重新创建数据库结构 - 修复版本
"""

import sqlite3
import os

def add_users_table():
    """在现有数据库基础上新增用户表"""
    db_path = 'bill_db.sqlite'
    
    print("=== 在现有数据库基础上新增用户表 ===")
    
    try:
        # 连接现有数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查现有表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        print(f"现有表: {existing_tables}")
        
        # 1. 创建用户表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            password_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("✓ 创建了 users 表")
        
        # 2. 为现有表添加 user_id 字段（如果不存在）
        # 检查 bills 表是否有 user_id 字段
        cursor.execute("PRAGMA table_info(bills)")
        bills_columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in bills_columns:
            cursor.execute("ALTER TABLE bills ADD COLUMN user_id INTEGER")
            print("✓ 为 bills 表添加了 user_id 字段")
        else:
            print("✓ bills 表已有 user_id 字段")
        
        # 检查 invoices 表是否有 user_id 字段
        cursor.execute("PRAGMA table_info(invoices)")
        invoices_columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in invoices_columns:
            cursor.execute("ALTER TABLE invoices ADD COLUMN user_id INTEGER")
            print("✓ 为 invoices 表添加了 user_id 字段")
        else:
            print("✓ invoices 表已有 user_id 字段")
        
        # 3. 创建索引（如果不存在）
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("✓ 创建了用户相关索引")
        
        conn.commit()
        
        # 验证结果
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\n所有表: {[table[0] for table in tables]}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        print(f"所有索引: {[index[0] for index in indexes]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"添加用户表时出错: {e}")
        return False

def insert_sample_users():
    """插入示例用户数据"""
    print("\n=== 插入示例用户数据 ===")
    
    try:
        conn = sqlite3.connect('bill_db.sqlite')
        cursor = conn.cursor()
        
        # 插入示例用户
        users_data = [
            ('张三', 'zhangsan@example.com', '13800138001', 'password_hash_1'),
            ('李四', 'lisi@example.com', '13800138002', 'password_hash_2'),
            ('王五', 'wangwu@example.com', '13800138003', 'password_hash_3')
        ]
        
        for username, email, phone, pwd_hash in users_data:
            cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, phone, password_hash) 
            VALUES (?, ?, ?, ?)
            ''', (username, email, phone, pwd_hash))
        
        print("✓ 插入了3个示例用户")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"插入示例用户数据时出错: {e}")
        return False

def insert_sample_data():
    """插入示例数据"""
    print("\n=== 插入示例数据 ===")
    
    try:
        conn = sqlite3.connect('bill_db.sqlite')
        cursor = conn.cursor()
        
        # 插入示例用户
        users_data = [
            ('张三', 'zhangsan@example.com', '13800138001', 'password_hash_1'),
            ('李四', 'lisi@example.com', '13800138002', 'password_hash_2'),
            ('王五', 'wangwu@example.com', '13800138003', 'password_hash_3')
        ]
        
        for username, email, phone, pwd_hash in users_data:
            cursor.execute('''
            INSERT INTO users (username, email, phone, password_hash) 
            VALUES (?, ?, ?, ?)
            ''', (username, email, phone, pwd_hash))
        
        print("✓ 插入了3个示例用户")
        
        # 插入示例账单数据
        import random
        from datetime import datetime, timedelta
        
        merchants = ['星巴克', '麦当劳', '肯德基', '海底捞', '滴滴出行', '美团外卖']
        categories = ['餐饮', '交通', '购物', '娱乐']
        payment_methods = ['微信', '支付宝', '银行卡', '现金']
        
        for user_id in range(1, 4):  # 为每个用户插入5条账单
            for i in range(5):
                days_ago = random.randint(0, 30)
                hours = random.randint(8, 22)
                consume_time = (datetime.now() - timedelta(days=days_ago, hours=hours)).strftime('%Y-%m-%d %H:%M')
                
                amount = round(random.uniform(10, 200), 2)
                merchant = random.choice(merchants)
                category = random.choice(categories)
                payment_method = random.choice(payment_methods)
                
                cursor.execute('''
                INSERT INTO bills (user_id, consume_time, amount, merchant, category, payment_method, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, consume_time, amount, merchant, category, payment_method, f"用户{user_id}的{category}消费"))
        
        print("✓ 插入了15条示例账单数据")
        
        # 插入示例发票数据
        for user_id in range(1, 4):  # 为每个用户插入3条发票
            for i in range(3):
                days_ago = random.randint(0, 30)
                hours = random.randint(8, 22)
                invoice_time = (datetime.now() - timedelta(days=days_ago, hours=hours)).strftime('%Y-%m-%d %H:%M')
                
                amount = round(random.uniform(50, 500), 2)
                merchant = random.choice(merchants)
                invoice_type = random.choice(categories)
                
                cursor.execute('''
                INSERT INTO invoices (user_id, invoice_time, amount, merchant, invoice_type, ocr_text, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, invoice_time, amount, merchant, invoice_type, f"OCR识别文本: {merchant} {amount}元", f"/images/invoice_{user_id}_{i}.jpg"))
        
        print("✓ 插入了9条示例发票数据")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"插入示例数据时出错: {e}")
        return False

def show_data_summary():
    """显示数据摘要"""
    print("\n=== 数据摘要 ===")
    
    try:
        conn = sqlite3.connect('bill_db.sqlite')
        cursor = conn.cursor()
        
        # 显示用户信息
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        print(f"用户总数: {len(users)}")
        for user in users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}")
        
        # 显示每个用户的账单数量
        for user_id in range(1, 4):
            cursor.execute("SELECT COUNT(*) FROM bills WHERE user_id = ?", (user_id,))
            bills_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE user_id = ?", (user_id,))
            invoices_count = cursor.fetchone()[0]
            
            print(f"用户{user_id}: {bills_count}条账单, {invoices_count}条发票")
        
        # 显示总统计
        cursor.execute("SELECT COUNT(*) FROM bills")
        total_bills = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM bills")
        total_amount = cursor.fetchone()[0]
        
        print(f"\n总计: {total_bills}条账单, {total_invoices}条发票, 总金额: {total_amount:.2f}元")
        
        conn.close()
        
    except Exception as e:
        print(f"显示数据摘要时出错: {e}")

def main():
    """主函数"""
    print("数据库用户表添加工具")
    print("=" * 50)
    
    # 检查数据库文件是否存在
    if not os.path.exists('bill_db.sqlite'):
        print("错误: bill_db.sqlite 文件不存在")
        print("请先确保数据库文件存在")
        return
    
    # 在现有数据库基础上添加用户表
    if add_users_table():
        # 插入示例用户数据
        if insert_sample_users():
            # 显示数据摘要
            show_data_summary()
            
            print("\n=== 完成 ===")
            print("用户表已成功添加到现有数据库！")
            print("现在可以使用以下方式查看:")
            print("1. SQLite Browser: 打开 bill_db.sqbpro 文件")
            print("2. 命令行: sqlite3 bill_db.sqlite")
            print("3. Python: sqlite3.connect('bill_db.sqlite')")
        else:
            print("示例用户数据插入失败")
    else:
        print("用户表添加失败")

if __name__ == "__main__":
    main()
