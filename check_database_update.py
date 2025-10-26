"""
检查数据库更新
"""
import sqlite3
from datetime import datetime
import os

def check_database():
    """检查数据库内容"""
    db_path = "data/bill_db.sqlite"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return
    
    # 获取文件信息
    file_stat = os.stat(db_path)
    file_size = file_stat.st_size
    file_time = datetime.fromtimestamp(file_stat.st_mtime)
    
    print(f"数据库文件: {db_path}")
    print(f"文件大小: {file_size} 字节")
    print(f"最后修改: {file_time}")
    print()
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    print(f"数据库表: {tables}")
    print()
    
    # 统计每个表的数据
    for table in tables:
        if table == 'sqlite_sequence':
            continue
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        # 获取最后更新时间
        if 'created_at' in [desc[0] for desc in cursor.execute(f"PRAGMA table_info({table})").fetchall()]:
            cursor.execute(f"SELECT MAX(created_at) as last_update FROM {table}")
            last_update = cursor.fetchone()['last_update']
            print(f"  {table}: {count} 条记录 (最后更新: {last_update})")
        else:
            print(f"  {table}: {count} 条记录")
    
    print()
    
    # 检查具体的数据统计
    print("=== 数据统计 ===")
    
    # 用户统计
    cursor.execute("SELECT COUNT(*) as count, MAX(created_at) as last_update FROM users")
    users_info = cursor.fetchone()
    print(f"用户: {users_info['count']} 个")
    
    # 账单统计
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            MIN(consume_time) as earliest,
            MAX(consume_time) as latest
        FROM bills
    """)
    bills_info = cursor.fetchone()
    print(f"账单: {bills_info['count']} 条")
    print(f"  总金额: {bills_info['total_amount']:.2f}元")
    print(f"  平均金额: {bills_info['avg_amount']:.2f}元")
    print(f"  时间范围: {bills_info['earliest']} 到 {bills_info['latest']}")
    
    # 发票统计
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            MIN(invoice_time) as earliest,
            MAX(invoice_time) as latest
        FROM invoices
    """)
    invoices_info = cursor.fetchone()
    print(f"发票: {invoices_info['count']} 条")
    print(f"  总金额: {invoices_info['total_amount']:.2f}元")
    print(f"  平均金额: {invoices_info['avg_amount']:.2f}元")
    
    # 金融产品统计
    cursor.execute("SELECT COUNT(*) as count FROM financial_products")
    products_count = cursor.fetchone()[0]
    print(f"金融产品: {products_count} 个")
    
    # 贷款产品统计
    cursor.execute("SELECT COUNT(*) as count FROM loan_products")
    loans_count = cursor.fetchone()[0]
    print(f"贷款产品: {loans_count} 个")
    
    # 按类别统计
    print()
    print("=== 消费分类统计 ===")
    cursor.execute("""
        SELECT category, COUNT(*) as count, SUM(amount) as total, AVG(amount) as avg
        FROM bills 
        GROUP BY category 
        ORDER BY total DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['category']}: {row['count']}笔, 总计{row['total']:.2f}元, 平均{row['avg']:.2f}元")
    
    conn.close()
    
    print()
    print("=== 数据库检查完成 ===")

if __name__ == "__main__":
    check_database()
