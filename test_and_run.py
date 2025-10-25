"""
测试和运行脚本 - 统一测试和运行入口
"""
import os
import sys
import sqlite3
import subprocess
from datetime import datetime

def check_dependencies():
    """检查依赖包"""
    print("=== 检查依赖包 ===")
    
    required_packages = [
        'sqlite3',  # 内置包
        'json',     # 内置包
        'random',   # 内置包
        'datetime'  # 内置包
    ]
    
    optional_packages = [
        'pandas',
        'numpy', 
        'matplotlib',
        'plotly',
        'jieba',
        'scikit-learn',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package} (可选)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少可选包: {', '.join(missing_packages)}")
        print("运行基础功能不需要这些包，但完整功能需要安装")
        print("安装命令: pip install -r requirements.txt")
    
    return len(missing_packages) == 0

def test_database():
    """测试数据库功能"""
    print("\n=== 测试数据库功能 ===")
    
    try:
        # 检查数据库文件
        db_path = "data/bill_db.sqlite"
        if not os.path.exists(db_path):
            print("数据库文件不存在，正在创建...")
            return False
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"数据库表: {tables}")
        
        # 检查数据
        for table in ['users', 'bills', 'invoices', 'financial_products', 'loan_products']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} 条记录")
            else:
                print(f"  {table}: 表不存在")
        
        conn.close()
        print("[OK] 数据库连接正常")
        return True
        
    except Exception as e:
        print(f"[ERROR] 数据库测试失败: {e}")
        return False

def test_api_functions():
    """测试API功能"""
    print("\n=== 测试API功能 ===")
    
    try:
        # 导入测试模块
        sys.path.append('src')
        from test_api_simple import SimpleBillManager
        
        # 创建管理器
        manager = SimpleBillManager()
        
        # 测试基本功能
        bills = manager.get_bills(limit=5)
        print(f"[OK] 获取账单: {len(bills)} 条")
        
        summary = manager.get_spending_summary()
        print(f"[OK] 消费汇总: {summary['total_amount']:.2f}元")
        
        category_analysis = manager.get_category_analysis()
        print(f"[OK] 分类分析: {len(category_analysis)} 个类别")
        
        search_results = manager.search_bills("餐饮")
        print(f"[OK] 搜索功能: 找到 {len(search_results)} 条记录")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API功能测试失败: {e}")
        return False

def generate_test_data():
    """生成测试数据"""
    print("\n=== 生成测试数据 ===")
    
    try:
        # 运行统一数据生成器
        from data.unified_data_generator import UnifiedDataGenerator
        
        generator = UnifiedDataGenerator()
        generator.generate_all_data(
            user_count=3,
            bills_per_user=50,
            invoices_per_user=20
        )
        
        print("[OK] 测试数据生成完成")
        return True
        
    except Exception as e:
        print(f"[ERROR] 测试数据生成失败: {e}")
        return False

def run_simple_demo():
    """运行简单演示"""
    print("\n=== 运行简单演示 ===")
    
    try:
        # 运行简化测试
        result = subprocess.run([sys.executable, "test_api_simple.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("[OK] 简单演示运行成功")
            print("演示输出:")
            print(result.stdout[-500:])  # 显示最后500个字符
            return True
        else:
            print(f"[ERROR] 简单演示运行失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 运行演示失败: {e}")
        return False

def run_full_server():
    """运行完整服务器"""
    print("\n=== 运行完整服务器 ===")
    
    try:
        # 检查是否有完整依赖
        try:
            import fastapi
            import uvicorn
            print("[OK] 检测到完整依赖，可以运行服务器")
            
            # 启动服务器
            print("启动服务器...")
            print("访问地址: http://localhost:8000")
            print("API文档: http://localhost:8000/docs")
            print("按 Ctrl+C 停止服务器")
            
            subprocess.run([sys.executable, "run_server.py"])
            
        except ImportError:
            print("[ERROR] 缺少完整依赖，无法运行服务器")
            print("请运行: pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"[ERROR] 运行服务器失败: {e}")
        return False

def show_file_structure():
    """显示文件结构"""
    print("\n=== 项目文件结构 ===")
    
    def print_tree(directory, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        try:
            items = sorted(os.listdir(directory))
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                    
                path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item}")
                
                if os.path.isdir(path) and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_tree(path, next_prefix, max_depth, current_depth + 1)
                    
        except PermissionError:
            pass
    
    print_tree(".")

def main():
    """主函数"""
    print("账单查询与管理系统 - 测试和运行工具")
    print("=" * 50)
    
    # 显示文件结构
    show_file_structure()
    
    # 检查依赖
    has_full_deps = check_dependencies()
    
    # 测试数据库
    db_ok = test_database()
    
    # 如果数据库不存在或为空，生成测试数据
    if not db_ok:
        print("\n数据库不存在或为空，正在生成测试数据...")
        if generate_test_data():
            db_ok = test_database()
    
    # 测试API功能
    if db_ok:
        api_ok = test_api_functions()
    else:
        api_ok = False
    
    # 运行演示
    if api_ok:
        demo_ok = run_simple_demo()
    else:
        demo_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"依赖检查: {'[OK]' if has_full_deps else '[PARTIAL] (部分)'}")
    print(f"数据库: {'[OK]' if db_ok else '[ERROR]'}")
    print(f"API功能: {'[OK]' if api_ok else '[ERROR]'}")
    print(f"演示运行: {'[OK]' if demo_ok else '[ERROR]'}")
    
    if demo_ok:
        print("\n[SUCCESS] 系统运行正常！")
        print("\n可用的运行方式:")
        print("1. 简单演示: python test_api_simple.py")
        print("2. 完整服务器: python run_server.py (需要完整依赖)")
        print("3. 数据生成: python data/unified_data_generator.py")
    else:
        print("\n[ERROR] 系统存在问题，请检查错误信息")
    
    # 询问是否运行完整服务器
    if has_full_deps and api_ok:
        try:
            choice = input("\n是否运行完整服务器? (y/n): ").lower()
            if choice in ['y', 'yes', '是']:
                run_full_server()
        except KeyboardInterrupt:
            print("\n用户取消")

if __name__ == "__main__":
    main()
