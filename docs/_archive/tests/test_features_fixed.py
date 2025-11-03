"""修复后的功能测试"""
import urllib.request
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_api(name, endpoint, method="GET", data=None):
    """测试API"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = urllib.request.urlopen(url, timeout=5)
        else:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, timeout=5)
        
        result = json.loads(response.read().decode())
        print(f"[OK] {name}")
        if isinstance(result, dict) and 'data' in result:
            data_size = len(result['data']) if isinstance(result['data'], list) else 1
            print(f"     数据量: {data_size}")
        return True
    except Exception as e:
        error_msg = str(e)
        if "500" in error_msg:
            print(f"[X] {name} - 服务器内部错误")
        elif "404" in error_msg:
            print(f"[X] {name} - 接口不存在")
        else:
            print(f"[X] {name} - {error_msg[:50]}")
        return False

print("=" * 60)
print("修复后的功能测试")
print("=" * 60)

results = []

print("\n1. 基础功能...")
results.append(("健康检查", test_api("健康检查", "/health")))
results.append(("账单列表", test_api("账单列表", "/bills?limit=5&user_id=1")))
results.append(("消费汇总", test_api("消费汇总", "/analysis/summary?user_id=1")))
results.append(("商家推荐", test_api("商家推荐", "/merchants/top?user_id=1")))

print("\n2. AI功能...")
results.append(("AI-今日消费", test_api("AI今日消费分析", "/ai/advice/1", "POST", {"query": "今日消费分析"})))
results.append(("AI-趋势分析", test_api("AI消费趋势", "/ai/advice/1", "POST", {"query": "消费趋势分析"})))
results.append(("AI-好商家", test_api("AI好商家推荐", "/ai/advice/1", "POST", {"query": "好商家推荐"})))
results.append(("金融产品推荐", test_api("金融产品推荐", "/ai/recommendations/financial/enhanced/1")))

print("\n3. 社区功能...")
results.append(("帖子列表", test_api("获取帖子列表", "/community/posts?limit=10")))

print("\n4. 预算功能...")
results.append(("预算列表", test_api("获取预算", "/budgets?user_id=1")))
results.append(("预算预警", test_api("预算预警", "/budgets/alerts?user_id=1")))

print("\n5. 预警功能...")
results.append(("大额交易检测", test_api("大额交易", "/alerts/large-transactions?user_id=1")))

print("\n" + "=" * 60)
print("测试结果")
print("=" * 60)

success = sum(1 for _, r in results if r)
total = len(results)

for name, result in results:
    status = "[OK]" if result else "[X]"
    print(f"{status} {name}")

print(f"\n总计: {success}/{total} 通过")
print("\n访问地址:")
print("  前端: http://localhost:3000")
print("  API文档: http://localhost:8000/docs")
print("  健康消费: http://localhost:3000/health")

