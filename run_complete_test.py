"""完整测试脚本（无需交互）"""
import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def check_server():
    """检查服务器是否运行"""
    try:
        req = urllib.request.Request(f"{BASE_URL}/health", timeout=3)
        response = urllib.request.urlopen(req)
        return response.status == 200
    except:
        return False

def test_api(endpoint, name, method="GET", data=None):
    """测试API"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "POST":
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url)
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"  [OK] {name}")
        if isinstance(result, dict) and 'data' in result:
            data_size = len(result['data']) if isinstance(result['data'], list) else 1
            if data_size > 0:
                print(f"      数据量: {data_size}")
        return True
    except Exception as e:
        error_msg = str(e)
        if "HTTPError" in str(type(e)):
            error_body = e.read().decode()
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('detail', '未知错误')[:60]
            except:
                pass
        print(f"  [X] {name}")
        print(f"      错误: {error_msg}")
        return False

def main():
    print("=" * 60)
    print("账单查询与管理系统 - 完整测试")
    print("=" * 60)
    
    # 等待服务器启动
    print("\n检查服务器状态...")
    max_wait = 15
    for i in range(max_wait):
        if check_server():
            print("✓ 服务器已就绪！")
            break
        time.sleep(1)
        if i < max_wait - 1:
            print(f"等待服务器启动... ({i+1}/{max_wait})")
    else:
        print("\n[错误] 服务器未响应！")
        print("\n请先启动服务器：")
        print("  python run_server.py")
        return
    
    time.sleep(2)  # 等待完全启动
    
    # 运行测试
    tests = [
        # 基础功能
        ("/health", "健康检查"),
        ("/bills?limit=5&user_id=1", "账单列表"),
        ("/analysis/summary?user_id=1", "消费汇总"),
        ("/merchants/top?user_id=1&top_k=10", "商家推荐"),
        
        # AI功能
        ("/ai/advice/1", "AI今日消费分析", "POST", {"query": "今日消费分析"}),
        ("/ai/advice/1", "AI消费趋势", "POST", {"query": "消费趋势分析"}),
        ("/ai/advice/1", "AI好商家推荐", "POST", {"query": "好商家推荐"}),
        ("/ai/recommendations/financial/enhanced/1", "金融产品推荐"),
        
        # 社区功能
        ("/community/posts?limit=10", "社区帖子列表"),
        
        # 预算功能
        ("/budgets?user_id=1", "预算列表"),
        ("/budgets/alerts?user_id=1", "预算预警"),
        
        # 预警功能
        ("/alerts/large-transactions?user_id=1", "大额交易检测"),
    ]
    
    print("\n" + "=" * 60)
    print("开始测试")
    print("=" * 60)
    
    success_count = 0
    total_count = len(tests)
    
    # 按类别测试
    categories = {
        "基础功能": [0, 4],
        "AI功能": [4, 8],
        "社区功能": [8, 9],
        "预算功能": [9, 11],
        "预警功能": [11, 12],
    }
    
    for cat_name, (start, end) in categories.items():
        print(f"\n{cat_name}...")
        for i in range(start, end):
            if i >= len(tests):
                break
            test_item = tests[i]
            if len(test_item) == 4:
                endpoint, name, method, data = test_item
                if test_api(endpoint, name, method, data):
                    success_count += 1
            else:
                endpoint, name = test_item
                if test_api(endpoint, name):
                    success_count += 1
    
    # 测试结果
    print("\n" + "=" * 60)
    print(f"测试完成: {success_count}/{total_count} 通过")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n✅ 所有API测试通过！系统运行正常。")
        print("\n访问地址:")
        print("  前端: http://localhost:3000")
        print("  后端API文档: http://localhost:8000/docs")
        print("  健康消费: http://localhost:3000/health")
    else:
        print(f"\n⚠️ 有 {total_count - success_count} 个API测试失败")
        print("\n如果刚刚重启了服务器，请等待几秒后重新运行测试。")
        print("重启命令: python run_server.py")
    
    print("\n测试账号:")
    print("  用户名: user1 / user2 / user3")
    print("  密码: demo123")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()

