# 快速启动指南

## 完整启动流程

### 第一步：启动后端

```bash
# 方法1：使用 run_server.py（推荐）
python run_server.py

# 方法2：使用 uvicorn 直接启动
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 `http://localhost:8000` 启动

### 第二步：启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次需要）
npm install

# 启动前端
npm run dev
```

前端将在 `http://localhost:3000` 启动

## 访问应用

打开浏览器访问：`http://localhost:3000`

## 功能测试

### 后端 API 测试

访问 `http://localhost:8000/docs` 查看 API 文档

### 前端页面测试

- 账单小助手：`http://localhost:3000/dashboard`
- 账单管理：`http://localhost:3000/bills`
- 消费分析：`http://localhost:3000/analysis`
- AI助手：`http://localhost:3000/ai-assistant`
- 金融产品推荐：`http://localhost:3000/recommendations`
- 社区：`http://localhost:3000/community`

## 重要提示

1. **数据生成**：如果数据库为空，先运行 `python data/unified_data_generator.py` 生成测试数据
2. **依赖安装**：确保已安装所有 Python 依赖：`pip install -r requirements.txt`
3. **数据库初始化**：首次运行会自动创建数据库表

## 故障排除

### 后端启动失败

- 检查端口 8000 是否被占用
- 检查 Python 依赖是否完整安装
- 查看日志文件 `logs/app.log`

### 前端启动失败

- 检查 Node.js 版本（需要 >= 16）
- 删除 `node_modules` 和 `package-lock.json`，重新运行 `npm install`
- 检查端口 3000 是否被占用

### API 请求失败

- 确保后端正在运行
- 检查浏览器控制台的错误信息
- 确认后端 CORS 配置正确

