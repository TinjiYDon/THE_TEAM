"""安全启动服务器脚本（带错误处理和诊断）"""
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_and_start():
    """检查并启动服务器"""
    print("=" * 60)
    print("账单查询与管理系统 - 启动检查")
    print("=" * 60)
    print()
    
    # 检查语法
    print("1. 检查代码语法...")
    try:
        import py_compile
        py_compile.compile('src/main.py', doraise=True)
        print("   [OK] 语法检查通过")
    except py_compile.PyCompileError as e:
        print(f"   [X] 语法错误: {e}")
        print("\n请先修复语法错误后再启动服务器")
        return False
    except Exception as e:
        print(f"   [警告] 语法检查失败: {e}")
    
    # 检查数据库目录
    print("\n2. 检查数据库目录...")
    db_dir = Path("data")
    db_dir.mkdir(exist_ok=True)
    print(f"   [OK] 数据库目录已准备: {db_dir.absolute()}")
    
    # 检查配置
    print("\n3. 检查配置...")
    try:
        from src.config import HOST, PORT
        print(f"   [OK] 配置正常")
        print(f"   服务器地址: http://{HOST}:{PORT}")
    except Exception as e:
        print(f"   [X] 配置错误: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("检查完成，正在启动服务器...")
    print("=" * 60)
    print()
    
    # 启动服务器
    try:
        import uvicorn
        from src.config import HOST, PORT
        
        print("启动账单查询与管理系统...")
        print(f"服务器地址: http://{HOST}:{PORT}")
        print(f"API文档: http://{HOST}:{PORT}/docs")
        print(f"ReDoc文档: http://{HOST}:{PORT}/redoc")
        print("\n按 Ctrl+C 停止服务器\n")
        
        uvicorn.run(
            "src.main:app",
            host=HOST,
            port=PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
    except Exception as e:
        print(f"\n[错误] 启动失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n请检查:")
        print("1. 端口8000是否被占用")
        print("2. 依赖是否已安装: pip install -r requirements.txt")
        print("3. 运行诊断工具: python diagnose_and_start.py")
        return False
    
    return True

if __name__ == "__main__":
    check_and_start()

