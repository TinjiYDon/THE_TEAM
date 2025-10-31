# 快速测试指南

## 🚀 快速启动

### 1. 检查后端服务

在PowerShell中运行：
```powershell
python check_backend.py
```

或使用PowerShell脚本：
```powershell
powershell -ExecutionPolicy Bypass -File start_test.ps1
```

### 2. 启动后端服务（如果未运行）

```bash
python run_server.py
```

### 3. 启动前端服务（如果未运行）

```bash
cd frontend
npm run dev
```

### 4. 访问系统

- **前端**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs

## ✅ 测试功能

### 基础功能测试
1. **账单小助手**: http://localhost:3000/dashboard
   - 查看消费统计
   - 查看饼图和趋势图

2. **账单管理**: http://localhost:3000/bills
   - 测试搜索功能
   - 测试筛选功能
   - 测试查看详情

3. **消费分析**: http://localhost:3000/analysis
   - 查看各种图表

### AI功能测试
4. **AI助手**: http://localhost:3000/ai-assistant
   - 输入："今日消费分析"
   - 输入："消费趋势分析"
   - 输入："好商家推荐"
   - 输入："消费预警"
   - ✅ 验证不再显示"抱歉"消息

### 新功能测试
5. **健康消费**: http://localhost:3000/health
   - 设置月度预算
   - 查看消费进度
   - 接收超额预警

6. **社区**: http://localhost:3000/community
   - 发布帖子
   - 关联账单数据
   - 查看关联信息

7. **金融产品推荐**: http://localhost:3000/recommendations
   - 查看推荐产品（最多15个）
   - 查看推荐理由
   - 查看风险提示

## 🔐 登录信息

- **用户名**: user1 / user2 / user3
- **密码**: demo123

## ⚠️ 重要提示

如果某些API返回500错误，请**重启后端服务器**：
1. 停止当前服务（Ctrl+C）
2. 重新启动：`python run_server.py`

重启后以下功能将正常工作：
- 社区帖子API
- 金融产品推荐API（增强版）

## 📝 测试清单

- [ ] 后端服务运行
- [ ] 前端服务运行
- [ ] 登录系统
- [ ] 账单列表显示
- [ ] 搜索功能正常
- [ ] AI助手不显示"抱歉"
- [ ] 健康消费页面可访问
- [ ] 社区发帖可关联账单
- [ ] 金融产品推荐显示

完成以上测试后，系统即可正常使用！

