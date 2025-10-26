"""
简化服务器启动脚本 - 处理依赖问题
"""
import sys
import os
import subprocess

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("=== 检查依赖包 ===")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'numpy',
        'matplotlib',
        'plotly',
        'seaborn',
        'jieba',
        'scikit-learn',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖包...")
        
        try:
            # 安装依赖
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("依赖包安装完成！")
            return True
        except subprocess.CalledProcessError as e:
            print(f"依赖包安装失败: {e}")
            return False
    else:
        print("所有依赖包已安装")
        return True

def start_server():
    """启动服务器"""
    print("\n=== 启动服务器 ===")
    
    try:
        # 检查数据库
        if not os.path.exists("data/bill_db.sqlite"):
            print("数据库不存在，正在生成测试数据...")
            from data.unified_data_generator import UnifiedDataGenerator
            generator = UnifiedDataGenerator()
            generator.generate_all_data(user_count=3, bills_per_user=50, invoices_per_user=20)
        
        # 启动服务器
        print("启动FastAPI服务器...")
        print("服务器地址: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务器")
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动服务器失败: {e}")

def main():
    """主函数"""
    print("账单查询与管理系统 - 简化启动脚本")
    print("=" * 50)
    
    # 检查并安装依赖
    if check_and_install_dependencies():
        # 启动服务器
        start_server()
    else:
        print("依赖安装失败，请手动安装:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
