"""
生成测试数据脚本
"""
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data.test_data_generator import main

if __name__ == "__main__":
    print("开始生成测试数据...")
    main()
    print("测试数据生成完成！")
