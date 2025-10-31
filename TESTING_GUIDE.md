# 测试和运行指南

## 快速测试

运行完整测试脚本：
```bash
python test_and_run_full.py
```

该脚本会检查：
1. Python依赖是否完整
2. 数据库是否存在和数据量
3. 后端服务是否运行
4. 前端服务是否运行
5. API端点是否可用（如果后端运行）

## 启动服务

### 后端服务

```bash
# 方法1（推荐）
python run_server.py

# 方法2
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 `http://localhost:8000` 启动

### 前端服务

```bash
cd frontend
npm install  # 首次需要
npm run dev
```

前端将在 `http://localhost:3000` 启动

## 访问地址

### 前端页面
- **主页**: http://localhost:3000
- **账单小助手**: http://localhost:3000/dashboard
- **账单管理**: http://localhost:3000/bills
- **消费分析**: http://localhost:3000/analysis
- **AI助手**: http://localhost:3000/ai-assistant
- **金融产品推荐**: http://localhost:3000/recommendations
- **社区**: http://localhost:3000/community

### 后端API
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/health

## 测试账号

- **用户名**: user1 / user2 / user3
- **密码**: demo123

## 数据统计

当前数据库状态：
- **用户**: 5个
- **账单**: 2150条
- **理财产品**: 25条
- **贷款产品**: 25条

## 功能测试

### 1. 账单管理测试
1. 访问 http://localhost:3000/bills
2. 查看账单列表
3. 测试搜索和筛选
4. 尝试上传发票

### 2. AI助手测试
1. 访问 http://localhost:3000/ai-assistant
2. 输入："今日消费分析"
3. 输入："消费趋势分析"
4. 输入："好商家推荐"
5. 输入："消费预警"

### 3. 消费分析测试
1. 访问 http://localhost:3000/analysis
2. 查看分类分析图表
3. 查看趋势分析图表
4. 查看雷达图

### 4. 金融产品推荐测试
1. 访问 http://localhost:3000/recommendations
2. 查看推荐的产品
3. 查看推荐理由和风险提示

### 5. 社区功能测试
1. 访问 http://localhost:3000/community
2. 发布新帖子
3. 点赞和评论

### 6. API测试

使用API文档页面测试：
1. 访问 http://localhost:8000/docs
2. 尝试以下端点：
   - GET /api/v1/health - 健康检查
   - GET /api/v1/bills - 获取账单列表
   - GET /api/v1/analysis/summary - 消费汇总
   - GET /api/v1/merchants/top - 商家推荐
   - POST /api/v1/ai/advice/1 - AI建议
   - GET /api/v1/ai/recommendations/financial/enhanced/1 - 金融产品推荐

## 故障排除

### 后端启动失败
1. 检查端口8000是否被占用
2. 检查Python依赖是否完整
3. 查看错误日志

### 前端启动失败
1. 检查Node.js版本（需要 >= 16）
2. 删除 node_modules，重新运行 npm install
3. 检查端口3000是否被占用

### API请求失败
1. 确保后端服务正在运行
2. 检查浏览器控制台错误
3. 确认后端CORS配置正确

## 数据生成

如果需要更多测试数据：
```bash
# 生成测试数据
python data/unified_data_generator.py

# 加载金融产品数据
python load_financial_data.py

# 创建用户
python create_users.py
```

