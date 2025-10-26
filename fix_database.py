"""
修复数据库表结构问题
"""
import sqlite3
import os

def fix_database_schema():
    """修复数据库表结构"""
    db_path = "data/bill_db.sqlite"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查bills表结构
        cursor.execute("PRAGMA table_info(bills)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前bills表字段: {columns}")
        
        # 如果缺少updated_at字段，添加它
        if 'updated_at' not in columns:
            print("添加updated_at字段到bills表...")
            cursor.execute("ALTER TABLE bills ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # 检查invoices表结构
        cursor.execute("PRAGMA table_info(invoices)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"当前invoices表字段: {columns}")
        
        # 如果缺少updated_at字段，添加它
        if 'updated_at' not in columns:
            print("添加updated_at字段到invoices表...")
            cursor.execute("ALTER TABLE invoices ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # 检查是否有loan_products表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='loan_products'")
        if not cursor.fetchone():
            print("创建loan_products表...")
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
        
        # 检查是否有user_profiles表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles'")
        if not cursor.fetchone():
            print("创建user_profiles表...")
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
        
        conn.commit()
        print("数据库表结构修复完成")
        
        # 验证修复结果
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"所有表: {tables}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"修复数据库时出错: {e}")
        return False

def main():
    """主函数"""
    print("修复数据库表结构...")
    if fix_database_schema():
        print("数据库修复成功！")
    else:
        print("数据库修复失败！")

if __name__ == "__main__":
    main()
