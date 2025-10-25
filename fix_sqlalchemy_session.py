"""
修复SQLAlchemy会话问题
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

def get_bills_simple(user_id: int = 1, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """使用直接SQL查询获取账单，避免SQLAlchemy会话问题"""
    conn = sqlite3.connect("data/bill_db.sqlite")
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, consume_time, amount, merchant, category, 
                   payment_method, location, description, created_at, updated_at
            FROM bills 
            WHERE user_id = ? 
            ORDER BY consume_time DESC 
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'consume_time': row['consume_time'],
                'amount': row['amount'],
                'merchant': row['merchant'],
                'category': row['category'],
                'payment_method': row['payment_method'],
                'location': row['location'],
                'description': row['description'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return bills
        
    finally:
        conn.close()

def get_bill_by_id(bill_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取账单"""
    conn = sqlite3.connect("data/bill_db.sqlite")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, consume_time, amount, merchant, category, 
                   payment_method, location, description, created_at, updated_at
            FROM bills 
            WHERE id = ?
        """, (bill_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'consume_time': row['consume_time'],
                'amount': row['amount'],
                'merchant': row['merchant'],
                'category': row['category'],
                'payment_method': row['payment_method'],
                'location': row['location'],
                'description': row['description'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
        
    finally:
        conn.close()

def create_bill_simple(bill_data: Dict[str, Any]) -> int:
    """创建账单记录"""
    conn = sqlite3.connect("data/bill_db.sqlite")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO bills (user_id, consume_time, amount, merchant, category, 
                             payment_method, location, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_data['user_id'],
            bill_data['consume_time'],
            bill_data['amount'],
            bill_data['merchant'],
            bill_data['category'],
            bill_data['payment_method'],
            bill_data.get('location'),
            bill_data.get('description'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
        
    finally:
        conn.close()

def get_spending_summary_simple(user_id: int = 1) -> Dict[str, Any]:
    """获取消费汇总"""
    conn = sqlite3.connect("data/bill_db.sqlite")
    cursor = conn.cursor()
    
    try:
        # 总消费
        cursor.execute("""
            SELECT COUNT(*), SUM(amount), AVG(amount)
            FROM bills 
            WHERE user_id = ?
        """, (user_id,))
        
        count, total_amount, avg_amount = cursor.fetchone()
        
        # 按类别统计
        cursor.execute("""
            SELECT category, COUNT(*), SUM(amount), AVG(amount)
            FROM bills 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY SUM(amount) DESC
        """, (user_id,))
        
        categories = {}
        for row in cursor.fetchall():
            categories[row[0]] = {
                'count': row[1],
                'total_amount': row[2],
                'avg_amount': row[3]
            }
        
        # 按支付方式统计
        cursor.execute("""
            SELECT payment_method, COUNT(*), SUM(amount)
            FROM bills 
            WHERE user_id = ? 
            GROUP BY payment_method 
            ORDER BY SUM(amount) DESC
        """, (user_id,))
        
        payment_methods = {}
        for row in cursor.fetchall():
            payment_methods[row[0]] = {
                'count': row[1],
                'total_amount': row[2]
            }
        
        return {
            'total_amount': total_amount or 0,
            'total_count': count or 0,
            'avg_amount': avg_amount or 0,
            'categories': categories,
            'payment_methods': payment_methods
        }
        
    finally:
        conn.close()

def test_fixed_functions():
    """测试修复后的函数"""
    print("=== 测试修复后的函数 ===")
    
    # 测试获取账单
    bills = get_bills_simple(user_id=1, limit=5)
    print(f"获取账单: {len(bills)} 条")
    for bill in bills[:3]:
        print(f"  {bill['merchant']} - {bill['amount']}元 - {bill['category']}")
    
    # 测试消费汇总
    summary = get_spending_summary_simple(user_id=1)
    print(f"\n消费汇总:")
    print(f"  总金额: {summary['total_amount']:.2f}元")
    print(f"  总笔数: {summary['total_count']}笔")
    print(f"  平均金额: {summary['avg_amount']:.2f}元")
    
    # 测试分类统计
    print(f"\n分类统计:")
    for category, data in summary['categories'].items():
        print(f"  {category}: {data['count']}笔, {data['total_amount']:.2f}元")
    
    print("\n[OK] 所有函数测试通过！")

if __name__ == "__main__":
    test_fixed_functions()
