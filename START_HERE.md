# 🚀 账单查询与管理系统 - 快速启动指南

## ✅ 依赖已安装完成！

所有必需的Python包都已安装，现在您可以开始使用系统了。

## 📋 三种运行方式

### 方法1：一键测试和运行（推荐）⭐

```bash
python test_and_run.py
```

这个脚本会：
- ✅ 检查依赖包
- ✅ 测试数据库连接
- ✅ 测试所有功能模块
- ✅ 运行简单演示
- ✅ 提供服务器启动选项

---

### 方法2：分步运行

```bash
# 步骤1：生成测试数据
python data/unified_data_generator.py

# 步骤2：测试功能
python test_api_direct.py

# 步骤3：启动服务器
python run_server.py
```

---

### 方法3：直接启动服务器

```bash
python run_server.py
```

然后在浏览器中访问：
- 主页：http://localhost:8000
- API文档：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

---

## 🎯 快速测试

如果您想快速验证系统是否正常工作：

```bash
python test_api_direct.py
```

**预期输出**：
```
数据库连接: [OK]
查询功能: [OK]
消费分析: [OK]
智能搜索: [OK]
```

---

## 📊 系统功能

### 核心功能
- ✅ 账单管理（CRUD操作）
- ✅ 智能查询（自然语言处理）
- ✅ 消费分析（多维度统计）
- ✅ 数据可视化（多种图表）
- ✅ 发票管理（OCR识别）
- ✅ 用户画像（行为分析）
- ✅ 推荐系统（金融产品推荐）

### 测试数据
- 用户数量：3个
- 账单数量：150条
- 发票数量：60条
- 金融产品：5个
- 贷款产品：5个

---

## 🔧 常见问题

### 问题1：端口被占用
```bash
# 解决方案：停止Python进程
taskkill /f /im python.exe
```

### 问题2：数据库不存在
```bash
# 解决方案：重新生成数据库
python recreate_database_fixed.py
```

### 问题3：API返回500错误
```bash
# 解决方案：检查修复的会话问题
python fix_sqlalchemy_session.py
```

---

## 📱 API使用示例

### 获取账单列表
```bash
curl "http://localhost:8000/api/v1/bills?user_id=1&limit=10"
```

### 获取消费汇总
```bash
curl "http://localhost:8000/api/v1/analysis/summary?user_id=1"
```

### 健康检查
```bash
curl "http://localhost:8000/api/v1/health"
```

---

## 🎉 开始使用

**最简单的启动方式**：

```bash
python run_server.py
```

然后在浏览器访问：**http://localhost:8000**

系统会自动：
1. ✅ 初始化数据库
2. ✅ 加载AI模型（jieba分词）
3. ✅ 启动API服务器
4. ✅ 准备好所有API端点

---

## 📞 需要帮助？

如果遇到任何问题：
1. 检查错误信息
2. 查看终端输出
3. 运行 `python test_api_direct.py` 验证核心功能
4. 查看 `FINAL_TESTING_GUIDE.md` 获取详细文档

**祝您使用愉快！** 🚀
