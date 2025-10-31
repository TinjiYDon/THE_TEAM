# 🚀 快速启动指南

## 第一步：启动后端服务器

### 方法1：使用启动脚本（推荐）
```bash
python run_server.py
```

### 方法2：使用uvicorn直接启动
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 验证服务器启动
服务器启动后，您应该看到：
- 服务器地址: http://0.0.0.0:8000
- API文档: http://0.0.0.0:8000/docs

打开浏览器访问 http://localhost:8000/docs 验证API文档是否正常显示。

## 第二步：运行测试

### 快速测试（推荐）
```bash
python start_and_test.py
```

### 完整测试
```bash
python test_features_fixed.py
```

### 测试特定API
```bash
python test_specific_apis.py
```

## 第三步：启动前端服务（可选）

### 进入前端目录
```bash
cd frontend
```

### 安装依赖（首次运行）
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

前端服务启动后，访问 http://localhost:3000

## ✅ 完整启动流程

### 终端1：后端服务
```bash
python run_server.py
```
保持此终端窗口运行。

### 终端2：前端服务（可选）
```bash
cd frontend
npm run dev
```
保持此终端窗口运行。

### 终端3：测试验证
```bash
python start_and_test.py
```

## 📋 系统访问地址

- **前端主页**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **健康消费**: http://localhost:3000/health
- **社区**: http://localhost:3000/community
- **AI助手**: http://localhost:3000/ai-assistant
- **金融产品推荐**: http://localhost:3000/recommendations

## 🔐 测试账号

- **用户名**: user1 / user2 / user3
- **密码**: demo123

## 🧪 测试清单

### 后端测试
- [ ] 服务器启动成功
- [ ] API文档可访问
- [ ] 健康检查API正常
- [ ] 账单列表API正常
- [ ] AI助手API正常
- [ ] 社区帖子API正常
- [ ] 金融产品推荐API正常

### 前端测试
- [ ] 前端页面可访问
- [ ] 登录功能正常
- [ ] 账单管理页面正常
- [ ] AI助手页面正常
- [ ] 社区页面正常
- [ ] 健康消费页面正常

## ⚠️ 常见问题

### 1. 服务器启动失败
- 检查端口8000是否被占用
- 检查数据库文件是否存在：`data/bill_db.sqlite`
- 查看错误日志

### 2. API返回500错误
- **重要**：如果刚刚修改了代码，请重启服务器
- 检查数据库连接
- 查看控制台错误信息

### 3. 前端无法连接后端
- 确认后端服务器正在运行
- 检查后端地址：http://localhost:8000
- 查看浏览器控制台错误

### 4. 前端构建失败
- 确保已安装Node.js和npm
- 运行 `npm install` 安装依赖
- 检查 `package.json` 配置

## 📊 测试结果预期

### 完整测试通过后应显示：
```
测试完成: 12/12 通过
✅ 所有API测试通过！系统运行正常。
```

### API测试列表：
1. ✅ 健康检查
2. ✅ 账单列表
3. ✅ 消费汇总
4. ✅ 商家推荐
5. ✅ AI今日消费分析
6. ✅ AI消费趋势分析
7. ✅ AI好商家推荐
8. ✅ 金融产品推荐
9. ✅ 社区帖子列表
10. ✅ 预算列表
11. ✅ 预算预警
12. ✅ 大额交易检测

## 🎯 下一步

1. 启动后端服务器
2. 运行测试验证
3. 启动前端服务
4. 访问系统进行功能测试

---

**提示**: 如果遇到任何问题，请查看错误日志或运行测试脚本诊断问题。
