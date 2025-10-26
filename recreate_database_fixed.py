"""
重新创建数据库 - 修复版本
"""
import sqlite3
import os
import shutil
from datetime import datetime

def backup_existing_database():
    """备份现有数据库"""
    db_path = "data/bill_db.sqlite"
    if os.path.exists(db_path):
        backup_path = f"data/bill_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
        shutil.copy2(db_path, backup_path)
        print(f"数据库已备份到: {backup_path}")
        return backup_path
    return None

def create_new_database():
    """创建新的数据库"""
    db_path = "data/bill_db.sqlite"
    
    # 删除现有数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print("已删除现有数据库")
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            password_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建账单表
    cursor.execute("""
        CREATE TABLE bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consume_time TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            merchant TEXT NOT NULL,
            category TEXT DEFAULT '未知',
            payment_method TEXT NOT NULL,
            location TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # 创建发票表
    cursor.execute("""
        CREATE TABLE invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bill_id INTEGER,
            invoice_time TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            merchant TEXT NOT NULL,
            invoice_type TEXT DEFAULT '未知',
            ocr_text TEXT,
            image_path TEXT,
            confidence REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE SET NULL
        )
    """)
    
    # 创建金融产品表
    cursor.execute("""
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建贷款产品表
    cursor.execute("""
        CREATE TABLE loan_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            interest_rate REAL NOT NULL,
            term_min INTEGER NOT NULL,
            term_max INTEGER NOT NULL,
            amount_min REAL NOT NULL,
            amount_max REAL NOT NULL,
            eligibility_criteria TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建用户画像表
    cursor.execute("""
        CREATE TABLE user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            income_level TEXT,
            spending_pattern TEXT,
            risk_tolerance TEXT,
            investment_preference TEXT,
            credit_score INTEGER,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # 创建索引
    indexes = [
        "CREATE INDEX idx_users_username ON users(username)",
        "CREATE INDEX idx_users_email ON users(email)",
        "CREATE INDEX idx_bills_user_id ON bills(user_id)",
        "CREATE INDEX idx_bills_time ON bills(consume_time)",
        "CREATE INDEX idx_bills_category ON bills(category)",
        "CREATE INDEX idx_bills_merchant ON bills(merchant)",
        "CREATE INDEX idx_invoices_user_id ON invoices(user_id)",
        "CREATE INDEX idx_invoices_time ON invoices(invoice_time)",
        "CREATE INDEX idx_invoices_bill_id ON invoices(bill_id)",
        "CREATE INDEX idx_loan_products_interest ON loan_products(interest_rate)",
        "CREATE INDEX idx_loan_products_amount ON loan_products(amount_min, amount_max)",
        "CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    conn.close()
    print("新数据库创建完成")

def generate_sample_data():
    """生成示例数据"""
    from data.unified_data_generator import UnifiedDataGenerator
    
    generator = UnifiedDataGenerator()
    generator.generate_all_data(
        user_count=3,
        bills_per_user=50,
        invoices_per_user=20
    )

def main():
    """主函数"""
    print("重新创建数据库...")
    
    # 备份现有数据库
    backup_path = backup_existing_database()
    
    # 创建新数据库
    create_new_database()
    
    # 生成示例数据
    print("生成示例数据...")
    generate_sample_data()
    
    print("数据库重建完成！")
    if backup_path:
        print(f"原数据库已备份到: {backup_path}")

if __name__ == "__main__":
    main()
