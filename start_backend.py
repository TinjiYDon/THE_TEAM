"""简化的后端启动脚本"""
import sys
import os

# 将src目录添加到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    # 使用绝对导入启动
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

