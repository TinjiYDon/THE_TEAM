"""测试API端点"""
import urllib.request
import json

base_url = "http://localhost:8000/api/v1"

endpoints = [
    ("/health", "健康检查"),
    ("/bills?limit=5", "获取账单列表"),
    ("/analysis/summary?user_id=1", "消费汇总"),
    ("/merchants/top?user_id=1", "商家推荐"),
]

print("=" * 60)
print("API端点测试")
print("=" * 60)

success = 0
for endpoint, name in endpoints:
    try:
        url = f"{base_url}{endpoint}"
        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read().decode())
        
        if data.get('success', True):
            print(f"[OK] {name}: {endpoint}")
            success += 1
        else:
            print(f"[X] {name}: {endpoint} (响应失败)")
    except Exception as e:
        print(f"[X] {name}: {endpoint}")
        print(f"    错误: {str(e)[:100]}")

print(f"\n测试结果: {success}/{len(endpoints)} 通过")
print("\n" + "=" * 60)
print("系统测试完成！")
print("=" * 60)
print("\n访问地址:")
print("  前端: http://localhost:3000")
print("  后端API文档: http://localhost:8000/docs")
print("\n登录信息:")
print("  用户名: user1 / user2 / user3")
print("  密码: demo123")

