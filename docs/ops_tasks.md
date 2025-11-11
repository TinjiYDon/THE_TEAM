# 运维任务与定时任务说明

本文档说明系统中的定时任务、后台巡检与运维相关配置。

## 一、定时任务概览

### 1.1 榜单更新任务（2小时周期）

**任务名称**：`update_rankings_task`

**执行频率**：每2小时执行一次

**功能说明**：
- 统计近30天（可配置）内各商家的消费次数与金额
- 计算热门商家排名分数（基于消费次数与金额加权）
- 更新 `merchant_rankings` 表
- 支持手动触发：`POST /api/v1/rankings/update?period_days=30`

**实现位置**：
- 服务层：`src/merchant_service.py` → `update_rankings()`
- API路由：`src/api/v1/rankings.py` → `update_rankings_task()`
- 定时调度：`src/main.py` → 后台线程（`BackgroundTasks`）

**配置项**：
```python
# src/config.py
RANKING_CONFIG = {
    "update_interval_hours": 2,  # 更新间隔（小时）
    # ...
}
```

---

### 1.2 预警巡检任务（2小时周期）

**任务名称**：`alert_scan_task`

**执行频率**：每2小时执行一次

**功能说明**：
- 扫描近2小时内创建的账单记录
- 对未生成预警的账单进行风险评估（调用 `alert_service.evaluate_bill()`）
- 对中高风险账单创建预警事件（写入 `alert_events` 表）
- 根据用户偏好（`alert_prefs`）发送通知（邮件/企业微信/短信/公众号）
- 尊重用户设置的静默时段与频率限制

**实现位置**：
- 服务层：`src/services/alert_service.py` → `evaluate_bill()`
- 通知服务：`src/services/notify_service.py` → `send_notification()`
- 定时调度：`src/main.py` → 后台线程（`BackgroundTasks`）

**配置项**：
```python
# src/config.py
ALERT_CONFIG = {
    "scan_interval_hours": 2,  # 巡检间隔（小时）
    "scan_window_hours": 2,    # 扫描时间窗口（小时）
    # ...
}
```

**通知通道配置**：
- **邮件（SMTP）**：通过环境变量配置
  ```bash
  SMTP_HOST=smtp.example.com
  SMTP_PORT=587
  SMTP_USER=alerts@example.com
  SMTP_PASS=your_password
  FROM_EMAIL=alerts@example.com
  ```
- **企业微信机器人**：通过环境变量配置
  ```bash
  WECOM_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
  ```
- **短信/公众号**：预留接口，需接入第三方服务

**用户偏好设置**：
- 用户可在前端“预警设置”页面配置：
  - 风险阈值（高/中/低）
  - 通知通道开关（邮件/短信/企业微信/公众号）
  - 静默时段（默认22:00-7:00）
  - 频率限制（同等级预警在窗口期内合并）

---

### 1.3 联邦学习训练任务（每日夜间）

**任务名称**：`federated_learning_task`

**执行频率**：每日凌晨2:00执行（可配置）

**功能说明**：
- 启动联邦学习训练流程（FedAvg聚合）
- 本机多客户端模拟训练（MVP阶段）
- 聚合模型权重并保存新版本
- 灰度发布新模型（10%-30%用户）
- 记录模型版本与指标到 `fl_model_versions` 表

**实现位置**：
- 聚合器：`src/fl/aggregator.py` → `FedAvgAggregator`
- 客户端模拟：`src/fl/client_sim.py` → `FederatedClientSimulator`
- 定时调度：`src/main.py` → 后台线程（`BackgroundTasks`）

**配置项**：
```python
# src/config.py
FL_CONFIG = {
    "training_schedule": "0 2 * * *",  # Cron表达式：每日2:00
    "num_clients": 5,                    # 模拟客户端数量
    "num_rounds": 3,                     # 训练轮次
    "differential_privacy": {
        "enabled": True,
        "epsilon": 1.0,                  # 隐私预算
        "delta": 1e-5
    },
    "model_rollout": {
        "gray_scale": 0.1,               # 灰度比例（10%）
        "rollback_threshold": 0.05       # 回滚阈值（准确率下降>5%）
    }
}
```

**差分隐私**：
- 启用时，在聚合前对梯度添加拉普拉斯噪声
- 隐私预算（ε）控制噪声强度，ε越小隐私保护越强但准确率可能下降

---

## 二、任务调度实现

### 2.1 后台线程调度（当前实现）

**实现方式**：使用 Python `threading` 与 `time.sleep()` 实现简单定时任务

**代码位置**：`src/main.py` → `start_background_tasks()`

**优点**：
- 实现简单，无需额外依赖
- 适合开发与演示环境

**缺点**：
- 不支持 Cron 表达式
- 任务失败后不会自动重试
- 不适合生产环境高可用场景

**示例代码**：
```python
def start_background_tasks():
    """启动后台定时任务"""
    import threading
    import time
    
    def ranking_update_loop():
        while True:
            time.sleep(2 * 3600)  # 2小时
            try:
                merchant_service.update_rankings(period_days=30)
            except Exception as e:
                logger.error(f"榜单更新任务失败: {e}")
    
    def alert_scan_loop():
        while True:
            time.sleep(2 * 3600)  # 2小时
            try:
                alert_service.scan_recent_bills_for_alerts()
            except Exception as e:
                logger.error(f"预警巡检任务失败: {e}")
    
    # 启动线程
    threading.Thread(target=ranking_update_loop, daemon=True).start()
    threading.Thread(target=alert_scan_loop, daemon=True).start()
```

---

### 2.2 生产环境推荐方案

**方案一：APScheduler（推荐）**

```python
# 安装：pip install apscheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    merchant_service.update_rankings,
    'interval',
    hours=2,
    id='ranking_update'
)
scheduler.add_job(
    alert_service.scan_recent_bills_for_alerts,
    'interval',
    hours=2,
    id='alert_scan'
)
scheduler.add_job(
    fl_aggregator.run_training_round,
    'cron',
    hour=2,
    minute=0,
    id='fl_training'
)
scheduler.start()
```

**方案二：Celery + Redis（分布式场景）**

```python
# 安装：pip install celery redis
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def update_rankings():
    merchant_service.update_rankings(period_days=30)

@app.task
def scan_alerts():
    alert_service.scan_recent_bills_for_alerts()

# 定时配置（celerybeat）
app.conf.beat_schedule = {
    'update-rankings': {
        'task': 'update_rankings',
        'schedule': 7200.0,  # 2小时（秒）
    },
    'scan-alerts': {
        'task': 'scan_alerts',
        'schedule': 7200.0,
    },
}
```

**方案三：系统 Cron（Linux/Mac）**

```bash
# /etc/cron.d/bill-system
0 */2 * * * cd /path/to/project && python -c "from src.merchant_service import merchant_service; merchant_service.update_rankings()"
0 */2 * * * cd /path/to/project && python -c "from src.services.alert_service import alert_service; alert_service.scan_recent_bills_for_alerts()"
0 2 * * * cd /path/to/project && python -c "from src.fl.aggregator import FedAvgAggregator; FedAvgAggregator().run_training_round()"
```

---

## 三、监控与日志

### 3.1 任务执行日志

所有定时任务执行情况记录在：
- **应用日志**：`logs/app.log`（通过 `src/utils/logger.py` 统一管理）
- **数据库日志**：
  - 榜单更新：`merchant_rankings.updated_at`
  - 预警事件：`alert_events.created_at`
  - 通知发送：`notify_logs.sent_at`、`notify_logs.status`、`notify_logs.error`
  - 联邦学习：`fl_model_versions.created_at`、`fl_client_updates.accepted`

### 3.2 健康检查接口

**接口**：`GET /api/v1/health`

**返回示例**：
```json
{
  "status": "healthy",
  "database": "connected",
  "tasks": {
    "ranking_update": {
      "last_run": "2024-01-15T10:00:00",
      "next_run": "2024-01-15T12:00:00",
      "status": "success"
    },
    "alert_scan": {
      "last_run": "2024-01-15T10:00:00",
      "next_run": "2024-01-15T12:00:00",
      "status": "success"
    }
  }
}
```

---

## 四、故障处理

### 4.1 任务失败处理

- **榜单更新失败**：
  - 记录错误日志
  - 下次调度时继续执行
  - 手动触发：`POST /api/v1/rankings/update`

- **预警巡检失败**：
  - 记录错误日志
  - 下次调度时继续执行
  - 可通过数据库查询遗漏的账单并手动补评

- **联邦学习训练失败**：
  - 记录错误日志
  - 保留上一版本模型
  - 下次调度时重新训练

### 4.2 通知发送失败

- **邮件发送失败**：
  - 记录到 `notify_logs` 表（`status='failed'`，`error` 字段）
  - 支持重试（`retry_count` 字段）
  - 超过最大重试次数后标记为 `failed`

- **企业微信发送失败**：
  - 记录到 `notify_logs` 表
  - 检查 Webhook URL 是否有效
  - 检查网络连接

---

## 五、性能优化建议

1. **数据库索引**：确保 `bills.created_at`、`alert_events.created_at` 等字段有索引
2. **批量处理**：巡检任务使用批量查询，避免逐条处理
3. **异步通知**：通知发送使用异步任务队列（如 Celery），避免阻塞主流程
4. **缓存策略**：用户偏好（`alert_prefs`）可缓存到 Redis，减少数据库查询

---

## 六、环境变量配置

详见项目根目录 `.env.example` 文件。

---

**最后更新**：2024-01-15

