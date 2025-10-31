"""完整的启动和测试脚本"""
import subprocess
import time
import sys
import os
import urllib.request
import json
from pathlib import Path

def check_server_running():
    """检查服务器是否在运行"""
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/health", timeout=3)
        response = urllib.request.urlopen(req)
        if response.status == 200:
            return True
    except:
        pass
    return False

def test_api(endpoint, name, method="GET", data=None):
    """测试API端点"""
    try:
        url = f"http://localhost:8000/api/v1{endpoint}"
        
        if method == "GET":
            req = urllib.request.Request(url)
        else:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None)
            req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"  [OK] {name}")
        if isinstance(result, dict) and 'data' in result:
            data_size = len(result['data']) if isinstance(result['data'], list) else 1
            if data_size > 0:
                print(f"      数据量: {data_size}")
        return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  [X] {name} - HTTP {e.code}")
        try:
            error_data = json.loads(error_body)
            print(f"      错误: {error_data.get('detail', '未知错误')[:80]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"  [X] {name}")
        print(f"      错误: {str(e)[:80]}")
        return False

def run_full_test():
    """运行完整测试"""
    print("\n" + "=" * 60)
    print("运行完整API测试")
    print("=" * 60)
    
    # 等待服务器启动
    print("\n等待服务器启动...")
    for i in range(10):
        if check_server_running():
            print("服务器已就绪！")
            break
        time.sleep(1)
        print(f"等待中... ({i+1}/10)")
    else:
        print("[错误] 服务器未响应，请检查是否正常启动")
        return False
    
    time.sleep(2)  # 再等待2秒确保完全启动
    
    success_count = 0
    total_count = 0
    
    # 基础功能测试
    print("\n1. 基础功能...")
    tests = [
        ("/health", "健康检查"),
        ("/bills?limit=5&user_id=1", "账单列表"),
        ("/analysis/summary?user_id=1", "消费汇总"),
        ("/merchants/top?user_id=1&top_k=10", "商家推荐"),
    ]
    for endpoint, name in tests:
        total_count += 1
        if test_api(endpoint, name):
            success_count += 1
    
    # AI功能测试
    print("\n2. AI功能...")
    ai_tests = [
        ("/ai/advice/1", "AI今日消费分析", "POST", {"query": "今日消费分析"}),
        ("/ai/advice/1", "AI消费趋势", "POST", {"query": "消费趋势分析"}),
        ("/ai/advice/1", "AI好商家推荐", "POST", {"query": "好商家推荐"}),
        ("/ai/recommendations/financial/enhanced/1", "金融产品推荐"),
    ]
    for item in ai_tests:
        total_count += 1
        if len(item) == 4:
            endpoint, name, method, data = item
            if test_api(endpoint, name, method, data):
                success_count += 1
        else:
            endpoint, name = item
            if test_api(endpoint, name):
                success_count += 1
    
    # 社区功能测试
    print("\n3. 社区功能...")
    community_tests = [
        ("/community/posts?limit=10", "获取帖子列表"),
    ]
    for endpoint, name in community_tests:
        total_count += 1
        if test_api(endpoint, name):
            success_count += 1
    
    # 预算功能测试
    print("\n4. 预算功能...")
    budget_tests = [
        ("/budgets?user_id=1", "获取预算"),
        ("/budgets/alerts?user_id=1", "预算预警"),
    ]
    for endpoint, name in budget_tests:
        total_count += 1
        if test_api(endpoint, name):
            success_count += 1
    
    # 预警功能测试
    print("\n5. 预警功能...")
    alert_tests = [
        ("/alerts/large-transactions?user_id=1", "大额交易检测"),
    ]
    for endpoint, name in alert_tests:
        total_count += 1
        if test_api(endpoint, name):
            success_count += 1
    
    # 测试总结
    print("\n" + "=" * 60)
    print(f"测试完成: {success_count}/{total_count} 通过")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n✅ 所有API测试通过！系统运行正常。")
    else:
        print(f"\n⚠️ 有 {total_count - success_count} 个API测试失败")
        print("如果刚刚重启了服务器，请等待几秒后重新运行此测试。")
    
    return success_count == total_count

def main():
    """主函数"""
    print("=" * 60)
    print("账单查询与管理系统 - 启动和测试")
    print("=" * 60)
    
    # 检查服务器状态
    if check_server_running():
        print("\n[检测] 后端服务器正在运行")
        print("[提示] 如果刚刚修改了代码，建议重启服务器以确保使用最新代码")
        choice = input("\n是否继续测试当前服务器？(y/n): ").lower()
        if choice != 'y':
            print("\n请重启服务器后重新运行此脚本")
            print("重启命令: python run_server.py")
            return
    else:
        print("\n[检测] 后端服务器未运行")
        print("\n正在启动服务器...")
        print("\n[重要] 服务器将在后台启动")
        print("请在新的终端窗口中运行: python run_server.py")
        print("\n然后等待10秒后重新运行此测试脚本")
        print("\n或者，如果您已经启动了服务器，请按回车继续...")
        input()
    
    # 运行测试
    run_full_test()
    
    print("\n" + "=" * 60)
    print("访问地址")
    print("=" * 60)
    print("  前端: http://localhost:3000")
    print("  后端API文档: http://localhost:8000/docs")
    print("  健康消费: http://localhost:3000/health")
    print("\n测试账号:")
    print("  用户名: user1 / user2 / user3")
    print("  密码: demo123")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()

