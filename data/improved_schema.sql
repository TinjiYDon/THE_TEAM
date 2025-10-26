-- 三表数据库设计：用户表、账单表、发票表

-- 1. 用户表（为每个用户维护独立数据）
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,           -- 用户名
    email TEXT UNIQUE,                      -- 邮箱
    phone TEXT,                             -- 手机号
    password_hash TEXT,                     -- 密码哈希
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 账单表（基于您提供的结构优化）
CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,               -- 关联用户ID
    consume_time TEXT NOT NULL,              -- 消费时间（如2024-10-01 08:30）
    amount REAL NOT NULL CHECK(amount > 0), -- 消费金额（如35.5）
    merchant TEXT NOT NULL,                  -- 商家（如星巴克）
    category TEXT DEFAULT '未知',            -- 消费类别（餐饮/交通/购物）
    payment_method TEXT NOT NULL,            -- 支付方式（微信/支付宝/银行卡）
    description TEXT,                        -- 备注
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. 发票表（基于您提供的结构优化）
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,               -- 关联用户ID
    bill_id INTEGER,                         -- 关联账单ID（可选）
    invoice_time TEXT NOT NULL,              -- 发票时间
    amount REAL NOT NULL CHECK(amount > 0),  -- 发票金额
    merchant TEXT NOT NULL,                  -- 商家
    invoice_type TEXT DEFAULT '未知',        -- 发票类型（餐饮/交通/办公）
    ocr_text TEXT,                           -- OCR识别的原始文本
    image_path TEXT,                         -- 发票图片路径
    confidence REAL,                         -- OCR识别置信度
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE SET NULL
);

-- 添加索引提高查询性能
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_bills_user_id ON bills(user_id);
CREATE INDEX idx_bills_time ON bills(consume_time);
CREATE INDEX idx_bills_category ON bills(category);
CREATE INDEX idx_bills_merchant ON bills(merchant);
CREATE INDEX idx_invoices_user_id ON invoices(user_id);
CREATE INDEX idx_invoices_time ON invoices(invoice_time);
CREATE INDEX idx_invoices_bill_id ON invoices(bill_id);

-- 创建视图方便查询
CREATE VIEW user_bill_summary AS
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
