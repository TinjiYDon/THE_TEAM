# 附录：数据库、接口与算法参数（润色稿）

本附录对本发明实施例涉及的数据库结构、接口定义及算法参数进行补充说明，以便于理解系统实现细节。

## A. 数据库表结构

### 表 A1 `users`
- `id` (INTEGER, PK)
- `username` (VARCHAR, 唯一)
- `email` (VARCHAR)
- `hashed_password` (VARCHAR)
- `created_at` (DATETIME)

### 表 A2 `bills`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK → `users.id`)
- `consume_time` (DATETIME)
- `amount` (DECIMAL(12,2))
- `merchant` (VARCHAR)
- `category` (VARCHAR)
- `payment_method` (VARCHAR)
- `city` (VARCHAR)
- `note` (TEXT)
- `created_at` (DATETIME)
- `source` (VARCHAR) — web / mobile / import 标记来源渠道

### 表 A3 `budgets`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK)
- `category` (VARCHAR)
- `monthly_budget` (DECIMAL(12,2))
- `alert_threshold` (DECIMAL(5,2)) — 超限比例，默认 0.8
- `created_at` (DATETIME)

### 表 A4 `user_profiles`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK)
- `spending_pattern` (JSON)
- `risk_tolerance` (VARCHAR) — conservative/moderate/aggressive
- `investment_preference` (JSON) — 类别偏好等
- `updated_at` (DATETIME)

### 表 A5 `user_preferences`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, 唯一)
- `city` (VARCHAR)
- `job` (VARCHAR)
- `budget_cycle` (VARCHAR) — daily/weekly/monthly
- `notify_budget` (BOOLEAN)
- `notify_insight` (BOOLEAN)
- `notify_community` (BOOLEAN)
- `updated_at` (DATETIME)

### 表 A6 `user_request_logs`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK)
- `request_type` (VARCHAR) — export/deactivate
- `status` (VARCHAR) — pending/done/rejected
- `detail` (TEXT)
- `created_at` (DATETIME)

### 表 A7 `community_posts`
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK)
- `title` (VARCHAR)
- `content` (TEXT)
- `bill_id` (INTEGER, FK → `bills.id`, 可空)
- `invoice_id` (INTEGER, 可空)
- `group_id` (INTEGER, 可空)
- `visibility` (VARCHAR) — public/same_city/private
- `attached_bill_id` (INTEGER)
- `location_city` (VARCHAR)
- `likes_count` (INTEGER)
- `comments_count` (INTEGER)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

### 表 A8 `groups`
- `id` (INTEGER, PK)
- `name` (VARCHAR)
- `level` (VARCHAR) — national/provincial/city
- `province` (VARCHAR)
- `city` (VARCHAR)
- `district` (VARCHAR)
- `type` (VARCHAR) — catering/finance/parenting 等
- `cover_url` (VARCHAR)
- `description` (TEXT)
- `created_at` (DATETIME)
- `max_members` (INTEGER, 默认 1000)

### 表 A9 `group_members`
- `id` (INTEGER, PK)
- `group_id` (INTEGER, FK → `groups.id`)
- `user_id` (INTEGER, FK)
- `joined_at` (DATETIME)
- `role` (VARCHAR) — owner/admin/member

### 表 A10 `financial_products`
- `id` (INTEGER, PK)
- `product_name` (VARCHAR)
- `product_type` (VARCHAR)
- `interest_rate` (DECIMAL(5,2))
- `min_amount` (DECIMAL(12,2))
- `max_amount` (DECIMAL(12,2))
- `risk_level` (VARCHAR)
- `description` (TEXT)

## B. API 接口说明

### B1 账单相关

| 接口 | 方法 | 必填参数 | 可选参数 | 描述 |
| --- | --- | --- | --- | --- |
| `/api/v1/bills` | GET | `page`, `pageSize` | `category`, `merchant`, `dateRange`, `minAmount`, `maxAmount` | 查询账单（分页、筛选） |
| `/api/v1/bills` | POST | `consume_time`, `amount` | `merchant`, `category`, `payment_method`, `city`, `note`, `source` | 创建账单 |
| `/api/v1/bills/{id}` | PUT | `id` | 与 POST 字段一致 | 更新账单 |
| `/api/v1/bills/{id}` | DELETE | `id` |  | 删除账单 |
| `/api/v1/bills/export/excel` | GET | `user_id` | `from`, `to`, `category` | 导出 Excel |
| `/api/v1/bills/export/image` | GET | `user_id`, `type` | `period`, `category` | 导出长图（`type`: list/comparison） |

**请求示例（POST /bills）**
```json
{
  "consume_time": "2025-11-09T12:30:00",
  "amount": 128.5,
  "merchant": "盒马鲜生",
  "category": "餐饮",
  "payment_method": "支付宝",
  "city": "上海"
}
```

### B2 智能助手 & 分析

| 接口 | 方法 | 必填参数 | 可选参数 | 描述 |
| --- | --- | --- | --- | --- |
| `/api/v1/analytics/trend` | GET | `period` (day/week/month/year/all) | `user_id`, `category` | 获取趋势数据 |
| `/api/v1/analytics/forecast` | GET | `period`, `horizon` | `user_id`, `category` | 获取趋势预测及误差 |
| `/api/v1/analytics/health-score` | GET | `window_days` | `user_id` | 财务健康评分（含分项） |
| `/api/v1/analytics/anomaly` | GET | `window_days` | `user_id`, `threshold_multiplier`, `limit` | 异常检测结果 |
| `/api/v1/insight/dining-bias` | GET | `user_id` | `city`, `period_days`, `share_threshold` | 餐饮偏好洞察 |
| `/api/v1/ai/profile` | GET | `user_id` |  | 获取用户画像 |

### B3 社群模块

| 接口 | 方法 | 必填参数 | 可选参数 | 描述 |
| --- | --- | --- | --- | --- |
| `/api/v1/community/posts` | GET | `page`, `pageSize` | `group_id`, `keyword`, `visibility` | 帖子列表 |
| `/api/v1/community/posts` | POST | `title`, `content` | `bill_id`, `group_id`, `attached_bill_id`, `visibility`, `city` | 创建帖子，可附账单摘要 |
| `/api/v1/community/posts/{id}/like` | POST | `id`, `user_id` | | 点赞 |
| `/api/v1/community/posts/{id}/comments` | POST | `id`, `user_id`, `content` | | 评论 |
| `/api/v1/community/feed` | GET | `scope` | `city`, `group_id`, `visibility`, `limit`, `offset` | 信息流聚合 |
| `/api/v1/groups` | GET |  | `city`, `type`, `level`, `q`, `limit`, `offset` | 群组列表 |
| `/api/v1/groups/{id}` | GET | `id` | `user_id` | 群组详情（含是否已加入） |
| `/api/v1/groups/{id}/join` | POST | `id`, `user_id` | | 加入群组 |
| `/api/v1/groups/{id}/leave` | POST | `id`, `user_id` | | 退出群组 |

### B4 个人中心 / 偏好

| 接口 | 方法 | 必填参数 | 可选参数 | 描述 |
| --- | --- | --- | --- | --- |
| `/api/v1/account/settings` | GET | `user_id` | | 获取偏好配置 |
| `/api/v1/account/settings` | PUT | `user_id` | `city`, `job`, `budget_cycle`, `notify_budget`, `notify_insight`, `notify_community` | 更新偏好 |
| `/api/v1/account/export` | POST | `user_id` | `reason`, `date_range` | 申请账单导出 |
| `/api/v1/account/deactivate` | POST | `user_id` | `reason`, `schedule_date` | 申请账号注销 |

**请求示例（PUT /account/settings）**
```json
{
  "city": "上海",
  "job": "产品经理",
  "budget_cycle": "monthly",
  "notify_budget": true,
  "notify_insight": true,
  "notify_community": false
}
```

## C. 核心算法参数

### C1 用户画像
- `spending_pattern.level`：阈值 5000 / 10000（低/中/高消费水平）
- `spending_pattern.stability`：变异系数阈值 0.5（稳定）、1.0（波动）
- `category_preference.prefer_level`：类别金额占比阈值 10% / 30%
- `consumption_habits.frequency`：日均次数阈值 1 / 3
- `consumption_habits.consistency`：周度金额稳定度阈值 0.4 / 0.7
- `risk_profile`：金额波动系数 >1.0 且单笔>均值3倍判定 aggressive
- `financial_health`：基础分 50，平均金额 <100 +20分，>1000 -20分，多样性>5 +15 分
- `recommendation_tags`：  
  - 总金额 >10000 → `high_spender`  
  - 餐饮占比 >40% → `food_lover`  
  - 微信支付占比 >70% → `wechat_user`

### C2 异常检测
- 均值 + 2.5 σ 作为默认异常阈值，可通过参数 `threshold_multiplier` 动态调整
- 异常比例 ×2 作为扣分因子
- 支持 `limit` 参数控制返回条数，默认输出前 20 条异常记录，并统计类别/商家 Top3

### C3 健康评分
- 综合权重：平衡 0.3、稳定 0.3、预算 0.25、异常 0.15
- 无预算数据时预算基线 0.7

### C4 预测模型
- 移动平均窗口：  
  - 日/周周期取 3  
  - 月周期取 6  
  - 年周期取 3
- MAPE 计算用于评估预测误差，结果写入响应 `mape`

### C5 洞察 & 推荐
- 餐饮偏好触发条件：  
  - `period_days` 默认 90 天  
  - 餐饮占比 ≥ 0.35  
  - 与次高类别差值占比 ≥ 0.2  
  - 交易次数 ≥ 10
- 推荐阈值：推荐评分 > 0.3 方进入结果集，评分由画像标签与产品/社群标签相似度计算。

### C6 反馈学习
- 点赞/评论/加入群组等行为计入偏好日志；默认每次行为增加标签权重 0.05，按周衰减 5%。  
- 行为可配置权重：点赞 0.03、评论 0.05、加入群组 0.08、发布帖子 0.10；衰减系数默认为 0.95。

## D. 接口返回示例

**`GET /api/v1/analytics/anomaly`**
```json
{
  "success": true,
  "data": {
    "anomalies": [
      {
        "id": 1024,
        "consume_time": "2025-10-28 19:21:00",
        "amount": 1899.0,
        "merchant": "Apple Store",
        "category": "数码",
        "dt": "2025-10-28T19:21:00"
      }
    ],
    "threshold": 1220.45,
    "explain": {
      "top_categories": [["数码", 3], ["旅行", 1], ["餐饮", 1]],
      "top_merchants": [["Apple Store", 2], ["国航", 1], ["海底捞", 1]]
    }
  }
}
```

**`GET /api/v1/ai/profile`**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "spending_pattern": {"type": "medium_value", "level": "medium", "stability": "moderate"},
    "category_preference": {"top_categories": ["餐饮", "出行", "数码"]},
    "payment_behavior": {"preferred_method": "微信"},
    "consumption_habits": {"frequency": "high", "time_preference": "evening"},
    "risk_profile": {"tolerance": "moderate"},
    "financial_health": {"score": 78, "level": "good"},
    "recommendation_tags": ["food_lover", "wechat_user"]
  }
}
```

## E. 字段与参数补充说明

### E1 关键字段说明表

| 字段 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| `bills.amount` | DECIMAL(12,2) | NOT NULL | 消费金额（元） |
| `bills.source` | VARCHAR | | 数据来源：web/mobile/import |
| `budgets.alert_threshold` | DECIMAL(5,2) | DEFAULT 0.8 | 预算预警比例 |
| `user_profiles.spending_pattern` | JSON | | 存储消费模式细分指标 |
| `community_posts.visibility` | VARCHAR | DEFAULT 'public' | 可见范围（public/same_city/private） |
| `group_members.role` | VARCHAR | DEFAULT 'member' | 成员角色 |

### E2 分析接口参数说明

| 参数 | 所属接口 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `period` | `/analytics/trend`, `/analytics/forecast` | STRING | `month` | 时间粒度 |
| `horizon` | `/analytics/forecast` | INTEGER | 1 | 预测期数 |
| `window_days` | `/analytics/health-score`, `/analytics/anomaly` | INTEGER | 90 | 统计窗口天数 |
| `threshold_multiplier` | `/analytics/anomaly` | FLOAT | 2.5 | 异常阈值倍数 |
| `scope` | `/community/feed` | STRING | `plaza` | 信息流范围（plaza/my_groups） |
| `visibility` | `/community/feed` | STRING | `all` | 可见性过滤 |
| `share_threshold` | `/insight/dining-bias` | FLOAT | 0.35 | 餐饮占比触发阈值 |

### E3 算法计算示例

1. **异常阈值计算**  
   - 输入金额序列：\[120, 150, 200, 135, 180, 210, 900\]  
   - 均值 μ = 270.7，标准差 σ ≈ 264.0  
   - 默认阈值 = μ + 2.5σ ≈ 930.7。若用户将 `threshold_multiplier` 调整为 2.0，则阈值 = μ + 2.0σ ≈ 798.7，900 将被标记为异常。  
   - 输出异常列表同时统计商家/类别贡献 Top3。

2. **健康评分示例**  
   - 平衡度 0.82、稳定度 0.75、预算得分 0.65、异常得分 0.90  
   - Score = (0.82×0.3 + 0.75×0.3 + 0.65×0.25 + 0.90×0.15) × 100 ≈ 78.8，健康等级为 `good`。

3. **反馈权重更新**  
   - 当周行为：点赞 3 次、评论 1 次、加入群组 1 次  
   - 增量 = 3×0.03 + 1×0.05 + 1×0.08 = 0.20  
   - 若上周标签权重为 0.60，则衰减后为 0.60×0.95 = 0.57，再加增量得到 0.77，写回 `user_preferences`。

