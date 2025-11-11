-- 账单查询与管理系统 - 统一数据库架构
-- 包含：用户表、账单表、发票表、金融产品表、贷款产品表

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    password_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 账单表
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    consume_time TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    merchant TEXT NOT NULL,
    category TEXT DEFAULT '未知',
    payment_method TEXT NOT NULL,
    location TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 发票表
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_id INTEGER,
    invoice_time TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    merchant TEXT NOT NULL,
    invoice_type TEXT DEFAULT '未知',
    ocr_text TEXT,
    image_path TEXT,
    confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE SET NULL
);

-- 4. 金融产品表（理财产品）
CREATE TABLE IF NOT EXISTS financial_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_type TEXT NOT NULL,
    product_name TEXT NOT NULL,
    interest_rate REAL,
    min_amount REAL,
    max_amount REAL,
    term_months INTEGER,
    risk_level TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. 贷款产品表
CREATE TABLE IF NOT EXISTS loan_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    interest_rate REAL NOT NULL,
    term_min INTEGER NOT NULL,
    term_max INTEGER NOT NULL,
    amount_min REAL NOT NULL,
    amount_max REAL NOT NULL,
    eligibility_criteria TEXT, -- JSON格式存储申请条件
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. 用户画像表
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    income_level TEXT,
    spending_pattern TEXT, -- JSON格式存储消费模式
    risk_tolerance TEXT,
    investment_preference TEXT, -- JSON格式存储投资偏好
    credit_score INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_time ON bills(consume_time);
CREATE INDEX IF NOT EXISTS idx_bills_category ON bills(category);
CREATE INDEX IF NOT EXISTS idx_bills_merchant ON bills(merchant);
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_time ON invoices(invoice_time);
CREATE INDEX IF NOT EXISTS idx_invoices_bill_id ON invoices(bill_id);
CREATE INDEX IF NOT EXISTS idx_loan_products_interest ON loan_products(interest_rate);
CREATE INDEX IF NOT EXISTS idx_loan_products_amount ON loan_products(amount_min, amount_max);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- 7. 商家表
CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, -- 关联用户ID（商家账号）
    merchant_name TEXT NOT NULL,
    business_license TEXT, -- 经营许可证号
    license_image_path TEXT, -- 许可证图片路径
    category TEXT, -- 商家类别
    status TEXT DEFAULT 'pending', -- pending/approved/rejected
    verified_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id) -- 一个用户只能认证一个商家
);

-- 8. 商家详细信息表
CREATE TABLE IF NOT EXISTS merchant_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    description TEXT, -- 店铺说明
    address TEXT, -- 详细地址
    latitude REAL, -- 纬度
    longitude REAL, -- 经度
    phone TEXT,
    business_hours TEXT, -- 营业时间（JSON格式）
    images TEXT, -- 配图路径（JSON数组）
    avg_rating REAL DEFAULT 0.0, -- 平均评分
    review_count INTEGER DEFAULT 0, -- 评论数
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    UNIQUE(merchant_id)
);

-- 9. 商家排名数据表（定时更新）
CREATE TABLE IF NOT EXISTS merchant_rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    merchant_name TEXT NOT NULL,
    category TEXT,
    total_consumption_count INTEGER DEFAULT 0, -- 消费次数
    total_consumption_amount REAL DEFAULT 0.0, -- 消费总金额
    ranking_score REAL DEFAULT 0.0, -- 综合排名分数
    ranking_position INTEGER, -- 排名位置
    period_start DATETIME, -- 统计周期开始
    period_end DATETIME, -- 统计周期结束
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE
);

-- 10. 商家赞助记录表
CREATE TABLE IF NOT EXISTS merchant_sponsorships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    sponsorship_type TEXT DEFAULT 'bidding', -- bidding/cpc
    bid_amount REAL DEFAULT 0.0, -- 竞价金额（第一周）
    cpc_price REAL DEFAULT 0.0, -- CPC单价（第二周起）
    daily_budget REAL DEFAULT 0.0, -- 每日预算上限
    total_spent REAL DEFAULT 0.0, -- 总花费
    start_date DATETIME NOT NULL,
    end_date DATETIME,
    status TEXT DEFAULT 'active', -- active/paused/expired
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE
);

-- 11. 商家点击统计表（埋点数据）
CREATE TABLE IF NOT EXISTS merchant_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    user_id INTEGER,
    click_type TEXT DEFAULT 'view', -- view/click/detail/navigate
    ip_address TEXT,
    user_agent TEXT,
    referrer TEXT,
    device_fingerprint TEXT, -- 设备指纹
    is_valid INTEGER DEFAULT 1, -- 是否有效（防刷检测后标记）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 12. 商家评论表
CREATE TABLE IF NOT EXISTS merchant_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5), -- 1-5星评分
    content TEXT,
    images TEXT, -- 评论配图（JSON数组）
    status TEXT DEFAULT 'pending', -- pending/approved/rejected
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 13. 支付记录表
CREATE TABLE IF NOT EXISTS merchant_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    sponsorship_id INTEGER,
    payment_type TEXT NOT NULL, -- wechat/alipay
    amount REAL NOT NULL,
    transaction_id TEXT, -- 第三方支付交易号
    status TEXT DEFAULT 'pending', -- pending/success/failed
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    FOREIGN KEY (sponsorship_id) REFERENCES merchant_sponsorships(id) ON DELETE SET NULL
);

-- 14. 用户反馈表
CREATE TABLE IF NOT EXISTS user_feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    feedback_type TEXT NOT NULL, -- function/merchant_info/shop_info/suggestion
    title TEXT,
    content TEXT NOT NULL,
    contact_email TEXT,
    status TEXT DEFAULT 'pending', -- pending/processing/resolved
    admin_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 15. 防刷检测记录表
CREATE TABLE IF NOT EXISTS fraud_detection_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER,
    detection_type TEXT NOT NULL, -- click_fraud/review_fraud/ranking_manipulation
    suspicious_count INTEGER DEFAULT 0,
    risk_score REAL DEFAULT 0.0, -- 0-1风险分数
    action_taken TEXT, -- blocked/flagged/reviewed
    details TEXT, -- JSON格式存储详细信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE
);

-- 创建索引提高查询性能
CREATE INDEX IF NOT EXISTS idx_merchants_user_id ON merchants(user_id);
CREATE INDEX IF NOT EXISTS idx_merchants_status ON merchants(status);
CREATE INDEX IF NOT EXISTS idx_merchant_info_merchant_id ON merchant_info(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_rankings_merchant_id ON merchant_rankings(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_rankings_category ON merchant_rankings(category);
CREATE INDEX IF NOT EXISTS idx_merchant_rankings_score ON merchant_rankings(ranking_score DESC);
CREATE INDEX IF NOT EXISTS idx_merchant_sponsorships_merchant_id ON merchant_sponsorships(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_sponsorships_status ON merchant_sponsorships(status);
CREATE INDEX IF NOT EXISTS idx_merchant_clicks_merchant_id ON merchant_clicks(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_clicks_created_at ON merchant_clicks(created_at);
CREATE INDEX IF NOT EXISTS idx_merchant_clicks_user_id ON merchant_clicks(user_id);
CREATE INDEX IF NOT EXISTS idx_merchant_reviews_merchant_id ON merchant_reviews(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_reviews_status ON merchant_reviews(status);
CREATE INDEX IF NOT EXISTS idx_merchant_payments_merchant_id ON merchant_payments(merchant_id);
CREATE INDEX IF NOT EXISTS idx_merchant_payments_status ON merchant_payments(status);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_user_id ON user_feedbacks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedbacks_type ON user_feedbacks(feedback_type);
CREATE INDEX IF NOT EXISTS idx_fraud_detection_merchant_id ON fraud_detection_logs(merchant_id);

-- 创建视图方便查询
CREATE VIEW IF NOT EXISTS user_bill_summary AS
SELECT 
    u.username,
    DATE(b.consume_time) as date,
    b.category,
    COUNT(*) as count,
    SUM(b.amount) as total_amount,
    AVG(b.amount) as avg_amount
FROM users u
JOIN bills b ON u.id = b.user_id
GROUP BY u.id, DATE(b.consume_time), b.category;

-- 商家统计视图
CREATE VIEW IF NOT EXISTS merchant_stats_view AS
SELECT 
    m.id as merchant_id,
    m.merchant_name,
    m.category,
    COUNT(DISTINCT mc.user_id) as unique_visitors,
    COUNT(mc.id) as total_clicks,
    COUNT(CASE WHEN mc.click_type = 'detail' THEN 1 END) as detail_views,
    COUNT(CASE WHEN mc.click_type = 'navigate' THEN 1 END) as navigations,
    COALESCE(AVG(mr.rating), 0) as avg_rating,
    COUNT(mr.id) as review_count,
    COALESCE(SUM(mp.amount), 0) as total_payment
FROM merchants m
LEFT JOIN merchant_clicks mc ON m.id = mc.merchant_id
LEFT JOIN merchant_reviews mr ON m.id = mr.merchant_id AND mr.status = 'approved'
LEFT JOIN merchant_payments mp ON m.id = mp.merchant_id AND mp.status = 'success'
WHERE m.status = 'approved'
GROUP BY m.id, m.merchant_name, m.category;

-- 16. 预警事件表
CREATE TABLE IF NOT EXISTS alert_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_id INTEGER,
    level TEXT NOT NULL, -- high/medium/low
    event_type TEXT NOT NULL, -- large_amount/frequent_transactions/ocr_anomaly/anti_fraud/other
    title TEXT,
    reason TEXT, -- 简要原因
    evidence TEXT, -- JSON 结构化证据
    status TEXT DEFAULT 'new', -- new/read/ignored
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE SET NULL
);

-- 17. 用户预警偏好表
CREATE TABLE IF NOT EXISTS alert_prefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    threshold_high REAL DEFAULT 0.8,
    threshold_medium REAL DEFAULT 0.5,
    channel_email INTEGER DEFAULT 1,
    channel_sms INTEGER DEFAULT 0,
    channel_wecom INTEGER DEFAULT 1, -- 企业微信机器人
    channel_wechat_mp INTEGER DEFAULT 0, -- 公众号模板消息
    quiet_hours_start TEXT DEFAULT '22:00',
    quiet_hours_end TEXT DEFAULT '07:00',
    break_quiet_for_high INTEGER DEFAULT 1,
    rate_limit_per_hour INTEGER DEFAULT 5,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 18. 通知发送日志
CREATE TABLE IF NOT EXISTS notify_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    channel TEXT NOT NULL, -- email/sms/wecom/wechat_mp
    status TEXT NOT NULL, -- success/failed/skipped
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES alert_events(id) ON DELETE CASCADE
);

-- 19. 联邦学习 - 模型版本
CREATE TABLE IF NOT EXISTS fl_model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_hash TEXT UNIQUE NOT NULL,
    metrics TEXT, -- JSON: auc/f1/precision/recall
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active INTEGER DEFAULT 0
);

-- 20. 联邦学习 - 客户端更新元数据
CREATE TABLE IF NOT EXISTS fl_client_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round INTEGER NOT NULL,
    client_id TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    dp_used INTEGER DEFAULT 0,
    accepted INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_alert_events_user_time ON alert_events(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alert_events_level ON alert_events(level);
CREATE INDEX IF NOT EXISTS idx_notify_logs_event ON notify_logs(event_id, channel);
CREATE INDEX IF NOT EXISTS idx_fl_models_active ON fl_model_versions(active, created_at DESC);
