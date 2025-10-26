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
