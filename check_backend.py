"""检查后端服务状态"""
import urllib.request
import json
import sys

try:
    response = urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=3)
    data = json.loads(response.read().decode())
    print('[OK] 后端服务运行正常！')
    print('状态:', data.get('status', 'unknown'))
    print('版本:', data.get('version', 'unknown'))
    sys.exit(0)
except Exception as e:
    print('[X] 后端服务未运行或未就绪')
    print('错误:', str(e))
    print('\n请运行: python run_server.py')
    sys.exit(1)

