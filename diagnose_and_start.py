"""诊断和启动助手"""
import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("1. 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   [警告] 建议使用Python 3.8+")
    else:
        print("   [OK] Python版本符合要求")
    print()

def check_dependencies():
    """检查依赖"""
    print("2. 检查依赖包...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pandas',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   [OK] {package}")
        except ImportError:
            print(f"   [X] {package} - 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n   [警告] 缺少依赖: {', '.join(missing)}")
        print(f"   请运行: pip install {' '.join(missing)}")
    else:
        print("   [OK] 所有依赖已安装")
    print()

def check_database():
    """检查数据库"""
    print("3. 检查数据库...")
    db_path = Path("data/bill_db.sqlite")
    
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"   [OK] 数据库文件存在: {db_path.absolute()}")
        print(f"   文件大小: {size / 1024 / 1024:.2f} MB")
    else:
        print(f"   [警告] 数据库文件不存在: {db_path}")
        print("   服务器启动时会自动创建")
    print()

def check_config():
    """检查配置"""
    print("4. 检查配置...")
    try:
        sys.path.insert(0, 'src')
        from src.config import HOST, PORT, DATABASE_PATH
        print(f"   [OK] 配置文件正常")
        print(f"   服务器地址: http://{HOST}:{PORT}")
        print(f"   数据库路径: {DATABASE_PATH}")
    except Exception as e:
        print(f"   [X] 配置文件错误: {e}")
    print()

def check_syntax():
    """检查语法"""
    print("5. 检查代码语法...")
    try:
        import py_compile
        py_compile.compile('src/main.py', doraise=True)
        print("   [OK] 语法检查通过")
    except py_compile.PyCompileError as e:
        print(f"   [X] 语法错误: {e}")
        return False
    except Exception as e:
        print(f"   [警告] 语法检查失败: {e}")
        return False
    print()
    return True

def check_port():
    """检查端口占用"""
    print("6. 检查端口占用...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        if result == 0:
            print("   [警告] 端口8000已被占用")
            print("   请停止占用该端口的程序，或修改src/config.py中的PORT")
        else:
            print("   [OK] 端口8000可用")
    except Exception as e:
        print(f"   [警告] 端口检查失败: {e}")
    print()

def main():
    """主函数"""
    print("=" * 60)
    print("账单查询与管理系统 - 诊断工具")
    print("=" * 60)
    print()
    
    # 运行所有检查
    check_python_version()
    check_dependencies()
    check_database()
    check_config()
    syntax_ok = check_syntax()
    check_port()
    
    # 总结
    print("=" * 60)
    print("诊断完成")
    print("=" * 60)
    
    if not syntax_ok:
        print("\n[X] 发现语法错误，请先修复后再启动服务器")
        return
    
    print("\n[OK] 所有检查通过，可以启动服务器")
    print("\n启动命令:")
    print("  python run_server.py")
    print("\n启动后访问:")
    print("  API文档: http://localhost:8000/docs")
    print("  健康检查: http://localhost:8000/api/v1/health")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n诊断已取消")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()

