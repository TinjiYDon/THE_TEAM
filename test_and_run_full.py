"""
完整测试和运行脚本
检查依赖、数据库、API，并提供启动指南
"""
import sys
import subprocess
import sqlite3
from pathlib import Path
import time

# 尝试导入requests，如果没有则使用urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    try:
        from urllib.request import urlopen
        from urllib.error import URLError, HTTPError
    except ImportError:
        urlopen = None

def check_dependencies():
    """检查Python依赖"""
    print("=" * 60)
    print("1. 检查Python依赖...")
    print("=" * 60)
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pandas',
        'pydantic', 'jieba', 'numpy', 'matplotlib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[X] {package} - 缺失")
            missing.append(package)
    
    if missing:
        print(f"\n缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("[OK] 所有依赖已安装")
    return True

def check_database():
    """检查数据库"""
    print("\n" + "=" * 60)
    print("2. 检查数据库...")
    print("=" * 60)
    
    db_path = Path(__file__).parent / 'data' / 'bill_db.sqlite'
    
    if not db_path.exists():
        print(f"[X] 数据库不存在: {db_path}")
        print("正在初始化数据库...")
        try:
            from src.database import init_database
            init_database()
            print("[OK] 数据库初始化完成")
        except Exception as e:
            print(f"[X] 数据库初始化失败: {e}")
            return False
    else:
            print(f"[OK] 数据库存在: {db_path}")
    
    # 检查表和数据
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        tables = ['users', 'bills', 'financial_products', 'loan_products']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  {table}: {count} 条")
        
        conn.close()
        print("[OK] 数据库检查完成")
        return True
    except Exception as e:
        print(f"[X] 数据库检查失败: {e}")
        return False

def check_backend():
    """检查后端服务"""
    print("\n" + "=" * 60)
    print("3. 检查后端服务...")
    print("=" * 60)
    
    if HAS_REQUESTS:
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("[OK] 后端服务正在运行 (http://localhost:8000)")
                return True
        except requests.exceptions.RequestException:
            pass
    elif urlopen:
        try:
            response = urlopen("http://localhost:8000/api/v1/health", timeout=2)
            if response.getcode() == 200:
                print("[OK] 后端服务正在运行 (http://localhost:8000)")
                return True
        except (URLError, HTTPError):
            pass
    
    print("[X] 后端服务未运行")
    print("\n启动后端服务:")
    print("  方法1: python run_server.py")
    print("  方法2: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
    return False

def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 60)
    print("4. 测试API端点...")
    print("=" * 60)
    
    if not HAS_REQUESTS:
        print("[X] requests模块未安装，跳过API测试")
        print("  可以运行: pip install requests")
        return False
    
    base_url = "http://localhost:8000/api/v1"
    
    endpoints = [
        ("/health", "健康检查"),
        ("/bills?limit=5", "获取账单列表"),
        ("/analysis/summary", "消费汇总"),
        ("/merchants/top", "商家推荐"),
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"[OK] {name}: {endpoint}")
                success_count += 1
            else:
                print(f"[X] {name}: {endpoint} (状态码: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[X] {name}: {endpoint} (错误: {str(e)[:50]})")
    
    print(f"\n成功: {success_count}/{len(endpoints)}")
    return success_count == len(endpoints)

def check_frontend():
    """检查前端服务"""
    print("\n" + "=" * 60)
    print("5. 检查前端服务...")
    print("=" * 60)
    
    if HAS_REQUESTS:
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                print("[OK] 前端服务正在运行 (http://localhost:3000)")
                return True
        except requests.exceptions.RequestException:
            pass
    elif urlopen:
        try:
            response = urlopen("http://localhost:3000", timeout=2)
            if response.getcode() == 200:
                print("[OK] 前端服务正在运行 (http://localhost:3000)")
                return True
        except (URLError, HTTPError):
            pass
    
    print("[X] 前端服务未运行")
    print("\n启动前端服务:")
    print("  1. cd frontend")
    print("  2. npm install  # 首次需要")
    print("  3. npm run dev")
    return False

def print_startup_guide():
    """打印启动指南"""
    print("\n" + "=" * 60)
    print("启动指南")
    print("=" * 60)
    
    print("\n【后端启动】")
    print("  终端1: python run_server.py")
    print("  或: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
    print("  后端地址: http://localhost:8000")
    print("  API文档: http://localhost:8000/docs")
    
    print("\n【前端启动】")
    print("  终端2: cd frontend")
    print("         npm install  # 首次需要")
    print("         npm run dev")
    print("  前端地址: http://localhost:3000")
    
    print("\n【访问地址】")
    print("  - 前端主页: http://localhost:3000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/api/v1/health")
    
    print("\n【测试账号】")
    print("  用户名: user1 / user2 / user3")
    print("  密码: demo123")

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("账单管理系统 - 完整测试和运行")
    print("=" * 60)
    
    results = []
    
    # 1. 检查依赖
    results.append(("依赖检查", check_dependencies()))
    
    # 2. 检查数据库
    results.append(("数据库检查", check_database()))
    
    # 3. 检查后端
    backend_running = check_backend()
    results.append(("后端服务", backend_running))
    
    # 4. 如果后端运行，测试API
    if backend_running:
        results.append(("API测试", test_api_endpoints()))
    
    # 5. 检查前端
    results.append(("前端服务", check_frontend()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[X] 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if not all_passed:
        print("\n" + "=" * 60)
        print_startup_guide()
    else:
        print("\n[OK] 所有检查通过，系统准备就绪！")
        print("\n访问地址:")
        print("  前端: http://localhost:3000")
        print("  后端: http://localhost:8000/docs")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

