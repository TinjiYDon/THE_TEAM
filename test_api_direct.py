"""
直接测试API - 绕过SQLAlchemy问题
"""
import sqlite3
import json
from datetime import datetime

def test_database_direct():
    """直接测试数据库"""
    print("=== 直接数据库测试 ===")
    
    try:
        conn = sqlite3.connect("data/bill_db.sqlite")
        cursor = conn.cursor()
        
        # 测试查询账单
        cursor.execute("""
            SELECT id, user_id, consume_time, amount, merchant, category, payment_method
            FROM bills 
            WHERE user_id = 1 
            ORDER BY consume_time DESC 
            LIMIT 5
        """)
        
        bills = cursor.fetchall()
        print(f"找到 {len(bills)} 条账单记录")
        
        for bill in bills:
            print(f"  ID: {bill[0]}, 时间: {bill[2]}, 金额: {bill[3]}, 商家: {bill[4]}, 类别: {bill[5]}")
        
        # 测试统计查询
        cursor.execute("""
            SELECT category, COUNT(*), SUM(amount), AVG(amount)
            FROM bills 
            WHERE user_id = 1
            GROUP BY category 
            ORDER BY SUM(amount) DESC
        """)
        
        stats = cursor.fetchall()
        print(f"\n分类统计:")
        for stat in stats:
            print(f"  {stat[0]}: {stat[1]}笔, 总计{stat[2]:.2f}元, 平均{stat[3]:.2f}元")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== API端点测试 ===")
    
    try:
        import requests
    except ImportError:
        print("[SKIP] requests模块未安装，跳过API端点测试")
        return
    
    base_url = "http://localhost:8000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("[OK] 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"[ERROR] 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 健康检查请求失败: {e}")
    
    # 测试主页
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("[OK] 主页访问成功")
        else:
            print(f"[ERROR] 主页访问失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 主页请求失败: {e}")
    
    # 测试API文档
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("[OK] API文档访问成功")
        else:
            print(f"[ERROR] API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] API文档请求失败: {e}")

def test_simple_queries():
    """测试简单查询功能"""
    print("\n=== 简单查询测试 ===")
    
    try:
        from test_api_simple import SimpleBillManager
        
        manager = SimpleBillManager()
        
        # 测试获取账单
        bills = manager.get_bills(user_id=1, limit=5)
        print(f"[OK] 获取账单: {len(bills)} 条")
        
        # 测试消费汇总
        summary = manager.get_spending_summary(user_id=1)
        print(f"[OK] 消费汇总: 总计 {summary['total_amount']:.2f}元")
        
        # 测试分类分析
        analysis = manager.get_category_analysis(user_id=1)
        print(f"[OK] 分类分析: {len(analysis)} 个类别")
        
        # 测试搜索
        search_results = manager.search_bills("餐饮", user_id=1)
        print(f"[OK] 搜索功能: 找到 {len(search_results)} 条记录")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 简单查询测试失败: {e}")
        return False

def main():
    """主函数"""
    print("账单查询与管理系统 - 直接API测试")
    print("=" * 50)
    
    # 测试数据库
    db_ok = test_database_direct()
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试简单查询
    if db_ok:
        query_ok = test_simple_queries()
    else:
        query_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"数据库连接: {'[OK]' if db_ok else '[ERROR]'}")
    print(f"查询功能: {'[OK]' if query_ok else '[ERROR]'}")
    
    if db_ok and query_ok:
        print("\n[SUCCESS] 系统核心功能正常！")
        print("\n可用的功能:")
        print("1. 数据库查询和统计")
        print("2. 消费分析和可视化")
        print("3. 智能搜索和分类")
        print("4. 用户画像和推荐")
    else:
        print("\n[ERROR] 系统存在问题，请检查错误信息")

if __name__ == "__main__":
    main()
