# 一键启动指南

## 快速启动（推荐）

### 第一步：运行测试脚本

```bash
python test_and_run_full.py
```

这会检查所有依赖和服务状态。

### 第二步：启动后端

在新的终端窗口中运行：

```bash
python run_server.py
```

或使用 uvicorn：
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 第三步：确认前端已运行

如果前端未运行，在新的终端窗口中运行：

```bash
cd frontend
npm run dev
```

## 访问应用

1. **打开浏览器访问**: http://localhost:3000
2. **登录**: 点击右上角"登录"按钮
   - 用户名: user1 (或 user2, user3)
   - 密码: demo123

## 系统状态

当前状态：
- ✅ 依赖：已安装
- ✅ 数据库：已初始化（5用户，2150账单，25理财产品，25贷款产品）
- ✅ 前端：运行中 (http://localhost:3000)
- ⚠️ 后端：需要启动 (http://localhost:8000)

## 测试检查清单

- [ ] 后端服务运行正常
- [ ] 前端页面可以访问
- [ ] 可以登录系统
- [ ] 账单列表可以显示
- [ ] AI助手可以对话
- [ ] 图表可以显示
- [ ] 金融产品推荐可以查看
- [ ] 社区功能可以使用

## 下一步

启动后端后，访问：
- **前端**: http://localhost:3000
- **API文档**: http://localhost:8000/docs

享受使用！

