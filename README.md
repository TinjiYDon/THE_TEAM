# 账单查询与管理系统

用于深圳国际金融大赛的智能账单查询与管理系统，解决用户"账单查得慢、消费看不懂、票据难管理"的痛点。

## 项目特色

### 🎯 核心功能
- **智能查询**：支持自然语言查询，如"今天餐饮花了多少"
- **消费分析**：多维度数据分析，生成可视化图表
- **发票管理**：OCR自动识别发票信息并分类
- **用户画像**：基于消费行为生成个性化画像
- **智能推荐**：推荐合适的金融产品和服务
- **即时预警 + 后台巡检（新增）**：账单创建时即时风险评估（高/中/低+证据），每2小时后台巡检补发通知（尊重阈值、通道开关、静默与频控）
- **联邦学习（MVP骨架，新增）**：本地更新+服务端FedAvg聚合，支持差分隐私占位与模型版本记录

### 🤖 AI技术集成
- **自然语言处理**：jieba分词 + 意图识别
- **机器学习**：朴素贝叶斯分类 + 协同过滤推荐
- **数据清洗**：智能数据预处理和质量检测
- **智能分析**：消费模式识别和异常检测

### 📊 可视化图表
- 饼图、柱状图、折线图、散点图
- 雷达图、漏斗图、箱线图
- 交互式图表（Plotly）
- 实时数据更新

## 技术架构

### 后端技术栈
- **框架**：FastAPI（高性能异步框架）
- **数据库**：SQLite（开发） + PostgreSQL（生产）
- **数据处理**：Pandas + NumPy
- **可视化**：Matplotlib + Plotly
- **AI/ML**：scikit-learn + jieba
- **联邦学习（新增）**：FedAvg 聚合器 + 客户端模拟骨架，差分隐私与灰度发布预留
- **数据清洗**：自定义清洗算法

### 前端技术栈
- **框架**：React 18
- **UI组件**：Ant Design
- **图表**：Recharts + Plotly.js
- **状态管理**：React Hooks
- **路由**：React Router

### 系统架构
```
前端层 (React + Ant Design)
    ↓
API层 (FastAPI)
    ↓
业务层 (模块化设计)
    ↓
数据层 (SQLite + 文件存储)
```

## 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd bill-management-system

# 安装依赖
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
# 生成测试数据
python generate_test_data.py
```

### 3. 启动服务
```bash
# 启动后端服务
python run_server.py
```

### 4. 访问系统
- **API文档**：http://localhost:8000/docs
- **ReDoc文档**：http://localhost:8000/redoc
- **系统首页**：http://localhost:8000

## 核心模块

### 1. 账单管理 (`src/bill_query.py`)
- 智能查询处理
- 自然语言理解
- 多条件组合查询
- 查询结果优化

### 2. 消费分析 (`src/cost_analysis.py`)
- 统计分析算法
- 多维度数据挖掘
- 可视化图表生成
- 趋势预测分析

### 3. 发票管理 (`src/invoice_ocr.py`)
- OCR文本处理
- 智能信息提取
- 自动分类识别
- 数据质量验证

### 4. AI服务 (`src/ai_services.py`)
- 用户画像生成
- 推荐算法引擎
- 智能分析报告
- 个性化建议

### 5. 数据清洗 (`src/data_cleaning.py`)
### 6. 预警模块（新增）
- `src/services/alert_service.py`：统一风险评估（规则打分→高/中/低）、证据结构与事件落库
- `src/services/notify_service.py`：通知通道（邮件/企业微信机器人）与发送日志
- `src/api/v1/alerts.py`：预警列表查询、标记已读/忽略
- `src/api/v1/settings.py`：用户级预警偏好（阈值、通道开关、静默、频控）
- 后台巡检（每2小时）：`src/main.py` 启动时注册后台任务，扫描新事件并触发通知

### 7. 联邦学习模块（新增）
- `src/fl/aggregator.py`：FedAvg 聚合器，模型版本记录（哈希+指标）
- `src/fl/client_sim.py`：本机多客户端模拟更新（可替换为真实端）
- 数据质量检测
- 异常值识别
- 数据标准化
- 清洗报告生成

## API接口

### 账单管理
- `POST /api/v1/bills` - 创建账单
- `GET /api/v1/bills` - 获取账单列表
- `GET /api/v1/bills/{id}` - 获取账单详情
- `PUT /api/v1/bills/{id}` - 更新账单
- `DELETE /api/v1/bills/{id}` - 删除账单

### 智能查询
- `POST /api/v1/query` - 自然语言查询
- `GET /api/v1/analysis/summary` - 消费汇总
- `POST /api/v1/analysis/comprehensive` - 综合分析

### AI服务
- `GET /api/v1/ai/profile/{user_id}` - 用户画像
- `GET /api/v1/ai/recommendations/financial/{user_id}` - 金融推荐
- `GET /api/v1/ai/recommendations/spending/{user_id}` - 消费建议

### 发票管理
- `POST /api/v1/invoices/process` - 处理发票
- `GET /api/v1/invoices` - 获取发票列表
- `GET /api/v1/invoices/statistics` - 发票统计

### 预警与设置（新增）
- `GET /api/v1/alerts` - 预警列表（支持按level筛选、分页）
- `POST /api/v1/alerts/{event_id}/status` - 标记已读或忽略
- `GET /api/v1/settings/alert_prefs` - 获取用户预警偏好
- `POST /api/v1/settings/alert_prefs` - 保存用户预警偏好（阈值、通道开关、静默、频控）

## 使用示例

### 1. 智能查询示例
```python
# 查询今天餐饮消费
query = "今天餐饮花了多少"
response = requests.post("/api/v1/query", json={"query": query})
```

### 2. 创建账单示例
```python
bill_data = {
    "consume_time": "2024-01-15 12:30:00",
    "amount": 35.50,
    "merchant": "星巴克",
    "category": "餐饮",
    "payment_method": "微信"
}
response = requests.post("/api/v1/bills", json=bill_data)
print(response.json()["risk"])  # 返回 { level, score, title, reason, evidence, event_id }
```

### 3. 获取分析报告示例
```python
# 获取综合分析报告
response = requests.post("/api/v1/analysis/comprehensive", json={
    "user_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
})
```

## 项目结构

```
project/
├── src/                    # 源代码
│   ├── main.py            # FastAPI主应用
│   ├── config.py          # 配置文件
│   ├── models.py          # 数据模型
│   ├── database.py        # 数据库操作
│   ├── bill_query.py      # 账单查询
│   ├── cost_analysis.py   # 消费分析
│   ├── invoice_ocr.py     # 发票OCR
│   ├── ai_services.py     # AI服务
│   ├── data_cleaning.py   # 数据清洗
│   ├── services/
│   │   ├── alert_service.py    # 预警服务（新增）
│   │   └── notify_service.py   # 通知服务（新增）
│   ├── api/
│   │   └── v1/
│   │       ├── alerts.py       # 预警API（新增）
│   │       └── settings.py     # 设置API（新增）
│   └── fl/
│       ├── aggregator.py       # 联邦聚合器（新增）
│       └── client_sim.py       # 客户端模拟（新增）
├── data/                  # 数据存储
│   ├── bill_db.sqlite     # 数据库文件
│   ├── models/            # AI模型
│   └── test_data_generator.py  # 测试数据生成
├── frontend/              # 前端代码
├── requirements.txt       # Python依赖
├── run_server.py         # 启动脚本
└── generate_test_data.py # 数据生成脚本
```

## 开发计划

### 已完成功能 ✅
- [x] 数据库设计和创建
- [x] 账单CRUD操作
- [x] 智能查询处理
- [x] 消费分析算法
- [x] 数据可视化
- [x] 发票OCR处理
- [x] 用户画像生成
- [x] 推荐系统
- [x] 数据清洗
- [x] API接口开发
- [x] 即时预警与后台巡检、预警中心/设置页、联邦学习MVP骨架

### 待开发功能 🚧
- [ ] 前端界面开发（移动端适配、更多交互与图表）
- [ ] 用户认证系统
- [ ] 数据导入导出
- [ ] 移动端适配
- [ ] 性能优化
- [ ] 单元测试
- [ ] 部署配置

## 通知与联邦学习配置（新增）

### 通知配置
- 环境变量：
  - SMTP：`SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS`、`FROM_EMAIL`
  - 企业微信机器人：`WECOM_WEBHOOK`
- 前端“预警设置”：开启邮件/企业微信通道、设置静默时段与频控上限

### 联邦学习（MVP）
- 训练：使用 `src/fl/client_sim.py` 在本机模拟多客户端更新
- 聚合：使用 `src/fl/aggregator.py` 执行 FedAvg 并记录模型版本（哈希与指标）
- 隐私：预留差分隐私与梯度裁剪开关，支持灰度发布与回滚

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目发起人：[唐竟涵]
- 邮箱：[2225476840@qq.com]
- 项目地址：[https://github.com/TinjiYDon/THE_TEAM/]
-项目成员[王韵诗，詹江叶煜，李子萌，张倩]

---

**注意**：本项目为深圳国际金融大赛参赛作品，仅供学习和比赛使用。
