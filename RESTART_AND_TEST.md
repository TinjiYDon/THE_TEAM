# 重启服务器并测试指南

## ⚠️ 重要提示

修复的代码需要**重启后端服务器**才能生效。

## 🔄 重启步骤

### 1. 停止当前服务器

在运行后端的终端窗口中按 `Ctrl+C`

### 2. 重新启动后端

```bash
python run_server.py
```

或使用 uvicorn（支持自动重载）：
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 等待服务启动

等待几秒钟让服务器完全启动

### 4. 验证修复

运行测试脚本：
```bash
python test_specific_apis.py
```

或运行完整测试：
```bash
python test_features_fixed.py
```

## ✅ 重启后会修复的功能

1. **社区帖子API** (`/api/v1/community/posts`)
   - ✅ 已改用直接SQL查询
   - ✅ 避免SQLAlchemy会话问题

2. **金融产品推荐API** (`/api/v1/ai/recommendations/financial/enhanced/{user_id}`)
   - ✅ 已改用直接SQL查询获取产品
   - ✅ 已修复用户画像生成时的会话问题
   - ✅ 支持最多15个推荐

## 🧪 测试验证

### 重启前
- ⚠️ 社区帖子API: 500错误
- ⚠️ 金融产品推荐: 500错误

### 重启后（预期）
- ✅ 社区帖子API: 200正常
- ✅ 金融产品推荐: 200正常，返回15个推荐

## 📋 完整启动流程

### 终端1：后端服务
```bash
python run_server.py
```

### 终端2：前端服务
```bash
cd frontend
npm run dev
```

### 终端3：测试验证
```bash
python test_features_fixed.py
```

## 🎯 访问地址

- **前端**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **健康消费**: http://localhost:3000/health
- **社区**: http://localhost:3000/community
- **金融产品推荐**: http://localhost:3000/recommendations

## ✅ 测试账号

- **用户名**: user1 / user2 / user3
- **密码**: demo123

---

**重要**: 重启后端服务器后，所有12个API端点都应该正常工作！

