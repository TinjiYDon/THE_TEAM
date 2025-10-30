# 前端启动指南

## 快速启动

### 方法一：一键启动（推荐）

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次需要）
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 方法二：手动启动

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动前端**
   ```bash
   npm run dev
   ```

3. **确保后端运行**
   后端应运行在 `http://localhost:8000`

## 页面路由

访问以下路径查看不同页面：

- `http://localhost:3000/dashboard` - 账单小助手
- `http://localhost:3000/bills` - 账单管理
- `http://localhost:3000/analysis` - 消费分析
- `http://localhost:3000/ai-assistant` - AI助手
- `http://localhost:3000/recommendations` - 金融产品推荐
- `http://localhost:3000/community` - 社区

## 注意事项

1. **后端必须先启动**：前端依赖后端 API，确保后端运行在 `http://localhost:8000`
2. **端口冲突**：如果 3000 端口被占用，Vite 会自动使用下一个可用端口
3. **代理配置**：前端已配置代理，API 请求会自动转发到后端

## 构建生产版本

```bash
npm run build
```

构建产物在 `frontend/dist` 目录

## 预览生产版本

```bash
npm run preview
```

