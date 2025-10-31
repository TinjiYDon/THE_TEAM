# 重启服务器指南

## ⚠️ 重要提示

修复的代码需要重启后端服务器才能生效。

## 🔄 重启步骤

### 1. 停止当前服务器
如果后端服务正在运行，按 `Ctrl+C` 停止它。

### 2. 重新启动后端
```bash
python run_server.py
```

或使用 uvicorn：
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 验证服务
等待几秒后，访问 http://localhost:8000/docs 验证服务是否正常。

### 4. 重新测试
运行测试脚本：
```bash
python test_features_fixed.py
```

## ✅ 重启后会生效的修复

1. **社区帖子API** - 已改用直接SQL查询，避免SQLAlchemy会话问题
2. **金融产品推荐API** - 已增强错误处理和产品获取逻辑

## 🚀 完整启动流程

### 终端1：启动后端
```bash
python run_server.py
```

### 终端2：启动前端
```bash
cd frontend
npm run dev
```

### 访问
- 前端: http://localhost:3000
- 后端API文档: http://localhost:8000/docs

## 📝 测试建议

重启后，测试以下功能：
1. 访问 http://localhost:8000/api/v1/community/posts
2. 访问 http://localhost:8000/api/v1/ai/recommendations/financial/enhanced/1
3. 访问前端各个页面
4. 测试新功能（健康消费、预警等）

