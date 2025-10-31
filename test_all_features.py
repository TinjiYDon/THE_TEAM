"""全面功能测试脚本"""
import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(name, endpoint, method="GET", data=None):
    """测试API端点"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = urllib.request.urlopen(url, timeout=5)
        else:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, timeout=5)
        
        result = json.loads(response.read().decode())
        success = result.get('success', False) if isinstance(result, dict) else True
        
        if success or response.status == 200:
            print(f"[OK] {name}: {endpoint}")
            return True
        else:
            print(f"[X] {name}: {endpoint} (响应失败)")
            return False
    except Exception as e:
        print(f"[X] {name}: {endpoint}")
        print(f"    错误: {str(e)[:100]}")
        return False

print("=" * 60)
print("全面功能测试")
print("=" * 60)

# 1. 基础API测试
print("\n1. 基础API测试...")
test_endpoint("健康检查", "/health")
test_endpoint("账单列表", "/bills?limit=5&user_id=1")
test_endpoint("消费汇总", "/analysis/summary?user_id=1")
test_endpoint("商家推荐", "/merchants/top?user_id=1&top_k=5")

# 2. AI功能测试
print("\n2. AI功能测试...")
test_endpoint("AI建议-今日消费", "/ai/advice/1", "POST", {"query": "今日消费分析"})
test_endpoint("AI建议-趋势分析", "/ai/advice/1", "POST", {"query": "消费趋势分析"})
test_endpoint("AI建议-好商家", "/ai/advice/1", "POST", {"query": "好商家推荐"})
test_endpoint("金融产品推荐", "/ai/recommendations/financial/enhanced/1")

# 3. 社区功能测试
print("\n3. 社区功能测试...")
test_endpoint("获取帖子列表", "/community/posts?limit=10")
test_endpoint("创建帖子", "/community/posts", "POST", {
    "title": "测试帖子",
    "content": "这是一个测试帖子",
    "bill_id": None
})

# 4. 预算功能测试
print("\n4. 预算功能测试...")
test_endpoint("获取预算列表", "/budgets?user_id=1")
test_endpoint("获取预算预警", "/budgets/alerts?user_id=1")

# 5. 大额交易检测测试
print("\n5. 大额交易检测测试...")
test_endpoint("大额交易检测", "/alerts/large-transactions?user_id=1&threshold=1000")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n访问地址:")
print("  前端: http://localhost:3000")
print("  后端API文档: http://localhost:8000/docs")
print("\n新功能:")
print("  健康消费: http://localhost:3000/health")
print("  社群页面: http://localhost:3000/community")
print("  AI助手: http://localhost:3000/ai-assistant")

