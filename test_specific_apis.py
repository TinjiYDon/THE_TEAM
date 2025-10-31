"""测试特定API并显示错误详情"""
import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_api_detailed(name, endpoint, method="GET", data=None):
    """详细测试API"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n测试: {name}")
        print(f"URL: {url}")
        
        if method == "GET":
            req = urllib.request.Request(url)
        else:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None)
            req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read().decode())
        
        print(f"[OK] {name}")
        if isinstance(result, dict):
            if 'success' in result:
                print(f"  成功: {result['success']}")
            if 'data' in result:
                data_size = len(result['data']) if isinstance(result['data'], list) else 1
                print(f"  数据量: {data_size}")
        return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[X] {name} - HTTP {e.code}")
        try:
            error_data = json.loads(error_body)
            print(f"  错误详情: {error_data.get('detail', '未知错误')}")
        except:
            print(f"  错误响应: {error_body[:200]}")
        return False
    except Exception as e:
        print(f"[X] {name}")
        print(f"  错误: {str(e)[:100]}")
        return False

print("=" * 60)
print("详细测试失败的API")
print("=" * 60)

# 测试金融产品推荐
test_api_detailed(
    "金融产品推荐",
    "/ai/recommendations/financial/enhanced/1"
)

# 测试社区帖子列表
test_api_detailed(
    "社区帖子列表",
    "/community/posts?limit=10"
)

print("\n" + "=" * 60)
print("如果显示500错误，请重启后端服务器")
print("=" * 60)
print("\n重启命令:")
print("  1. 停止当前服务 (Ctrl+C)")
print("  2. 重新启动: python run_server.py")

