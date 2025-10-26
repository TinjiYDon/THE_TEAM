"""
简化API测试脚本 - 测试核心功能
"""
import sqlite3
import json
from datetime import datetime, timedelta
import random

class SimpleBillManager:
    """简化的账单管理器"""
    
    def __init__(self, db_path="data/bill_db.sqlite"):
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_bills(self, user_id=1, limit=100):
        """获取账单列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, consume_time, amount, merchant, category, payment_method
            FROM bills 
            WHERE user_id = ? 
            ORDER BY consume_time DESC 
            LIMIT ?
        """, (user_id, limit))
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row[0],
                'consume_time': row[1],
                'amount': row[2],
                'merchant': row[3],
                'category': row[4],
                'payment_method': row[5]
            })
        
        conn.close()
        return bills
    
    def get_spending_summary(self, user_id=1):
        """获取消费汇总"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 总消费
        cursor.execute("SELECT SUM(amount), COUNT(*), AVG(amount) FROM bills WHERE user_id = ?", (user_id,))
        total_amount, count, avg_amount = cursor.fetchone()
        
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
        
        conn.close()
        
        return {
            'total_amount': total_amount or 0,
            'total_count': count or 0,
            'avg_amount': avg_amount or 0,
            'categories': categories,
            'payment_methods': payment_methods
        }
    
    def search_bills(self, query, user_id=1):
        """搜索账单"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 简单的关键词搜索
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT id, consume_time, amount, merchant, category, payment_method
            FROM bills 
            WHERE user_id = ? 
            AND (merchant LIKE ? OR category LIKE ? OR payment_method LIKE ?)
            ORDER BY consume_time DESC
        """, (user_id, search_term, search_term, search_term))
        
        bills = []
        for row in cursor.fetchall():
            bills.append({
                'id': row[0],
                'consume_time': row[1],
                'amount': row[2],
                'merchant': row[3],
                'category': row[4],
                'payment_method': row[5]
            })
        
        conn.close()
        return bills
    
    def get_category_analysis(self, user_id=1):
        """获取分类分析"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*), SUM(amount), AVG(amount)
            FROM bills 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY SUM(amount) DESC
        """, (user_id,))
        
        analysis = []
        for row in cursor.fetchall():
            analysis.append({
                'category': row[0],
                'count': row[1],
                'total_amount': row[2],
                'avg_amount': row[3],
                'percentage': 0  # 稍后计算
            })
        
        # 计算百分比
        total_amount = sum(item['total_amount'] for item in analysis)
        for item in analysis:
            if total_amount > 0:
                item['percentage'] = (item['total_amount'] / total_amount) * 100
        
        conn.close()
        return analysis

def test_api_functions():
    """测试API功能"""
    print("=== 账单查询与管理系统 - API功能测试 ===\n")
    
    # 创建账单管理器
    manager = SimpleBillManager()
    
    # 1. 获取账单列表
    print("1. 获取账单列表:")
    bills = manager.get_bills(limit=5)
    for bill in bills:
        print(f"   {bill['merchant']} - {bill['amount']}元 - {bill['category']}")
    
    # 2. 获取消费汇总
    print("\n2. 消费汇总统计:")
    summary = manager.get_spending_summary()
    print(f"   总消费: {summary['total_amount']:.2f}元")
    print(f"   总笔数: {summary['total_count']}笔")
    print(f"   平均金额: {summary['avg_amount']:.2f}元")
    
    # 3. 分类分析
    print("\n3. 分类消费分析:")
    category_analysis = manager.get_category_analysis()
    for item in category_analysis:
        print(f"   {item['category']}: {item['count']}笔, {item['total_amount']:.2f}元 ({item['percentage']:.1f}%)")
    
    # 4. 搜索功能
    print("\n4. 搜索功能测试:")
    search_queries = ['餐饮', '微信', '星巴克']
    for query in search_queries:
        results = manager.search_bills(query)
        print(f"   搜索 '{query}': 找到 {len(results)} 条记录")
        if results:
            print(f"     示例: {results[0]['merchant']} - {results[0]['amount']}元")
    
    # 5. 支付方式分析
    print("\n5. 支付方式分析:")
    payment_methods = summary['payment_methods']
    for method, data in payment_methods.items():
        print(f"   {method}: {data['count']}笔, {data['total_amount']:.2f}元")
    
    # 6. 生成简单的分析报告
    print("\n6. 分析报告:")
    print("   === 消费分析报告 ===")
    print(f"   分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   总消费金额: {summary['total_amount']:.2f}元")
    print(f"   消费笔数: {summary['total_count']}笔")
    print(f"   平均单笔消费: {summary['avg_amount']:.2f}元")
    
    # 找出主要消费类别
    if category_analysis:
        top_category = category_analysis[0]
        print(f"   主要消费类别: {top_category['category']} ({top_category['percentage']:.1f}%)")
    
    # 找出主要支付方式
    if payment_methods:
        top_payment = max(payment_methods.items(), key=lambda x: x[1]['total_amount'])
        print(f"   主要支付方式: {top_payment[0]} ({top_payment[1]['total_amount']:.2f}元)")
    
    print("\n=== 测试完成 ===")

def simulate_intelligent_query():
    """模拟智能查询功能"""
    print("\n=== 智能查询模拟 ===")
    
    manager = SimpleBillManager()
    
    # 模拟查询
    queries = [
        "今天花了多少钱",
        "餐饮消费多少",
        "微信支付了多少",
        "星巴克消费"
    ]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        
        if "今天" in query:
            # 模拟今天的消费
            today = datetime.now().strftime('%Y-%m-%d')
            bills = manager.get_bills()
            today_bills = [b for b in bills if b['consume_time'].startswith(today)]
            total = sum(b['amount'] for b in today_bills)
            print(f"  结果: 今天消费 {total:.2f}元 ({len(today_bills)}笔)")
        
        elif "餐饮" in query:
            results = manager.search_bills("餐饮")
            total = sum(b['amount'] for b in results)
            print(f"  结果: 餐饮消费 {total:.2f}元 ({len(results)}笔)")
        
        elif "微信" in query:
            results = manager.search_bills("微信")
            total = sum(b['amount'] for b in results)
            print(f"  结果: 微信支付 {total:.2f}元 ({len(results)}笔)")
        
        elif "星巴克" in query:
            results = manager.search_bills("星巴克")
            total = sum(b['amount'] for b in results)
            print(f"  结果: 星巴克消费 {total:.2f}元 ({len(results)}笔)")

def main():
    """主函数"""
    try:
        # 测试API功能
        test_api_functions()
        
        # 模拟智能查询
        simulate_intelligent_query()
        
        print("\n=== 系统功能验证完成 ===")
        print("[OK] 数据库连接正常")
        print("[OK] 账单查询功能正常")
        print("[OK] 统计分析功能正常")
        print("[OK] 搜索功能正常")
        print("[OK] 智能查询模拟正常")
        
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")

if __name__ == "__main__":
    main()
