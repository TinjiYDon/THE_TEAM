# 账单查询与管理系统 - 测试和运行指南

## 项目概述

这是一个智能账单查询与管理系统，支持自然语言查询、消费分析、发票管理、用户画像和金融产品推荐等功能。

## 文件结构

```
project/
├── src/                           # 源代码目录
│   ├── main.py                    # FastAPI主应用
│   ├── config.py                  # 配置文件
│   ├── models.py                  # 数据模型
│   ├── database.py                # 数据库操作
│   ├── bill_query.py              # 账单查询模块
│   ├── cost_analysis.py           # 消费分析模块
│   ├── invoice_ocr.py             # 发票OCR模块
│   ├── ai_services.py             # AI服务模块
│   └── data_cleaning.py           # 数据清洗模块
├── data/                          # 数据目录
│   ├── bill_db.sqlite             # 主数据库
│   ├── database_schema.sql        # 数据库架构
│   ├── unified_data_generator.py  # 统一数据生成器
│   ├── exports/                   # 导出文件
│   ├── models/                    # AI模型文件
│   └── uploads/                   # 上传文件
├── docs/                          # 文档目录
├── test_and_run.py                # 统一测试和运行脚本
├── test_api_simple.py             # 简化API测试
├── test_simple.py                 # 简化数据库测试
├── run_server.py                  # 服务器启动脚本
├── requirements.txt               # Python依赖
└── README.md                      # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- SQLite3 (内置)
- 可选：完整依赖包 (见requirements.txt)

### 2. 一键测试和运行

```bash
# 运行统一测试和运行脚本
python test_and_run.py
```

这个脚本会：
- 检查依赖包
- 测试数据库连接
- 测试API功能
- 运行简单演示
- 提供运行选项

### 3. 分步测试

#### 3.1 测试数据库
```bash
python test_simple.py
```

#### 3.2 测试API功能
```bash
python test_api_simple.py
```

#### 3.3 生成测试数据
```bash
python data/unified_data_generator.py
```

#### 3.4 运行完整服务器
```bash
# 需要先安装依赖
pip install -r requirements.txt
python run_server.py
```

## 详细使用说明

### 1. 数据管理

#### 生成测试数据
```python
from data.unified_data_generator import UnifiedDataGenerator

generator = UnifiedDataGenerator()
generator.generate_all_data(
    user_count=5,        # 用户数量
    bills_per_user=100,  # 每用户账单数
    invoices_per_user=30 # 每用户发票数
)
```

#### 查看数据统计
```python
import sqlite3

conn = sqlite3.connect('data/bill_db.sqlite')
cursor = conn.cursor()

# 查看表结构
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库表:", [table[0] for table in tables])

# 查看数据统计
cursor.execute("SELECT COUNT(*) FROM bills")
bill_count = cursor.fetchone()[0]
print(f"账单数量: {bill_count}")

conn.close()
```

### 2. API使用

#### 2.1 基础查询
```python
from test_api_simple import SimpleBillManager

manager = SimpleBillManager()

# 获取账单列表
bills = manager.get_bills(limit=10)

# 获取消费汇总
summary = manager.get_spending_summary()

# 搜索账单
results = manager.search_bills("餐饮")

# 分类分析
analysis = manager.get_category_analysis()
```

#### 2.2 智能查询示例
```python
# 模拟自然语言查询
queries = [
    "今天花了多少钱",
    "餐饮消费多少", 
    "微信支付了多少",
    "星巴克消费"
]

for query in queries:
    print(f"查询: {query}")
    # 这里会调用智能查询处理
```

### 3. 服务器运行

#### 3.1 安装依赖
```bash
pip install -r requirements.txt
```

#### 3.2 启动服务器
```bash
python run_server.py
```

#### 3.3 访问服务
- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

#### 3.4 API端点
```
GET  /api/v1/bills                    # 获取账单列表
POST /api/v1/bills                    # 创建账单
GET  /api/v1/bills/{id}               # 获取账单详情
PUT  /api/v1/bills/{id}               # 更新账单
DELETE /api/v1/bills/{id}             # 删除账单

POST /api/v1/query                    # 智能查询
GET  /api/v1/analysis/summary         # 消费汇总
POST /api/v1/analysis/comprehensive   # 综合分析
GET  /api/v1/analysis/category        # 分类分析
GET  /api/v1/analysis/trend           # 趋势分析

GET  /api/v1/ai/profile/{user_id}     # 用户画像
GET  /api/v1/ai/recommendations/financial/{user_id}  # 金融推荐
GET  /api/v1/ai/recommendations/spending/{user_id}   # 消费建议

POST /api/v1/invoices/process         # 处理发票
GET  /api/v1/invoices                 # 获取发票列表
GET  /api/v1/invoices/statistics      # 发票统计
```

## 功能特性

### 1. 核心功能
- ✅ 账单管理 (CRUD操作)
- ✅ 智能查询 (自然语言处理)
- ✅ 消费分析 (多维度统计)
- ✅ 数据可视化 (多种图表)
- ✅ 发票管理 (OCR识别)
- ✅ 用户画像 (行为分析)
- ✅ 推荐系统 (金融产品推荐)

### 2. AI功能
- ✅ 自然语言查询处理
- ✅ 数据清洗和验证
- ✅ 消费模式识别
- ✅ 异常检测
- ✅ 智能推荐算法

### 3. 数据管理
- ✅ SQLite数据库
- ✅ 数据导入导出
- ✅ 批量数据处理
- ✅ 数据质量检测

## 测试数据说明

### 1. 用户数据
- 默认生成5个用户
- 包含用户名、邮箱、手机号等信息

### 2. 账单数据
- 每用户100条账单记录
- 包含6个消费类别：餐饮、交通、购物、娱乐、医疗、教育
- 时间范围：最近90天
- 金额范围：根据类别调整

### 3. 发票数据
- 每用户30条发票记录
- 包含OCR识别文本
- 自动分类和置信度评分

### 4. 金融产品数据
- 理财产品：3个
- 保险产品：2个
- 贷款产品：5个
- 包含详细的申请条件

## 故障排除

### 1. 常见问题

#### 问题：ModuleNotFoundError
```
解决方案：
pip install -r requirements.txt
```

#### 问题：数据库连接失败
```
解决方案：
1. 检查data目录是否存在
2. 运行 python test_simple.py 重新创建数据库
```

#### 问题：Unicode编码错误
```
解决方案：
1. 确保终端支持UTF-8编码
2. 在Windows上使用chcp 65001命令
```

### 2. 调试模式

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 数据库调试
```python
import sqlite3
conn = sqlite3.connect('data/bill_db.sqlite')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(bills)")
print(cursor.fetchall())
```

## 性能优化

### 1. 数据库优化
- 已创建必要的索引
- 使用外键约束
- 定期清理无用数据

### 2. 查询优化
- 使用LIMIT限制结果集
- 添加WHERE条件过滤
- 使用JOIN优化关联查询

### 3. 内存优化
- 分批处理大量数据
- 及时关闭数据库连接
- 使用生成器处理大数据集

## 扩展开发

### 1. 添加新功能
1. 在`src/`目录下创建新模块
2. 在`main.py`中添加API路由
3. 更新数据库架构
4. 添加测试用例

### 2. 自定义配置
1. 修改`src/config.py`
2. 添加环境变量支持
3. 创建配置文件

### 3. 部署建议
1. 使用生产级数据库 (PostgreSQL)
2. 配置反向代理 (Nginx)
3. 使用容器化部署 (Docker)
4. 添加监控和日志

## 联系信息

- 项目发起人：唐竟涵
- 邮箱：2225476840@qq.com
- 项目地址：https://github.com/TinjiYDon/THE_TEAM/
- 项目成员：王韵诗，詹江叶煜，李子萌，张倩

---

**注意**：本项目为深圳国际金融大赛参赛作品，仅供学习和比赛使用。
