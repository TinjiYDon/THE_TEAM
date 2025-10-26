"""
启动服务器脚本
"""
import uvicorn
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import HOST, PORT

if __name__ == "__main__":
    print("启动账单查询与管理系统...")
    print(f"服务器地址: http://{HOST}:{PORT}")
    print(f"API文档: http://{HOST}:{PORT}/docs")
    print(f"ReDoc文档: http://{HOST}:{PORT}/redoc")
    
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
