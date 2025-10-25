-- 创建贷款产品数据库 loan_db
USE loan_db;

-- 创建贷款产品表 loan_products
CREATE TABLE loan_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '贷款产品名称',
    description TEXT COMMENT '产品描述',
    interest_rate DECIMAL(5,2) NOT NULL COMMENT '年利率（%）',
    term_min INT NOT NULL COMMENT '最短期限（月）',
    term_max INT NOT NULL COMMENT '最长期限（月）',
    amount_min DECIMAL(12,2) NOT NULL COMMENT '最小可贷金额',
    amount_max DECIMAL(12,2) NOT NULL COMMENT '最大可贷金额',
    eligibility_criteria JSON COMMENT '申请条件（如信用分、收入等）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_interest_rate (interest_rate),
    INDEX idx_amount_range (amount_min, amount_max)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='贷款产品表';

-- 插入测试数据
INSERT INTO loan_products 
(name, description, interest_rate, term_min, term_max, amount_min, amount_max, eligibility_criteria)
VALUES 
('个人消费贷', '用于日常消费的信用贷款', 6.50, 12, 60, 10000.00, 500000.00, '{"credit_score_min": 600, "income_proof_required": true}'),
('房屋抵押贷', '以房产为抵押的长期贷款', 4.90, 60, 360, 100000.00, 10000000.00, '{"property_type": "residential", "ltv_ratio_max": 70}'),
('小微企业贷', '支持小微企业的经营贷款', 8.00, 6, 36, 50000.00, 2000000.00, '{"business_age_min": 1, "annual_revenue_min": 500000}'),
('公务员专享贷', '针对公务员和事业单位员工的低利率信用贷款', 4.50, 12, 60, 50000.00, 800000.00, '{"employment_type": "public_sector", "credit_score_min": 620}'),
('汽车消费贷', '用于购买新车或二手车的专项贷款', 5.80, 24, 60, 30000.00, 1000000.00, '{"down_payment_ratio_min": 20, "vehicle_age_max": 5}'),
('教育助学贷', '支持高等教育学费与生活费的贷款产品', 3.90, 12, 120, 5000.00, 500000.00, '{"student_status": "enrolled", "co_signer_required": true}'),
('农户惠农贷', '支持农业种植、养殖的低息贷款', 3.50, 6, 36, 10000.00, 300000.00, '{"land_owned": true, "purpose": "agriculture"}'),
('高净值客户尊享贷', '面向高净值客户的定制化大额信用贷款', 5.00, 12, 120, 1000000.00, 50000000.00, '{"asset_proof_required": true, "credit_score_min": 700}'),
('灵活还款贷', '支持前几个月只还利息，后期还本的灵活产品', 7.20, 6, 48, 20000.00, 300000.00, '{"income_stability": "medium", "repayment_style": "interest_first"}'),
('数字经济创业贷', '支持电商、直播、IT创业的专项贷款', 6.80, 12, 60, 50000.00, 2000000.00, '{"business_type": "digital_economy", "platform_merchandise_count_min": 10}'),
('绿色能源贷', '用于安装太阳能、充电桩等绿色项目的贷款', 4.00, 24, 120, 50000.00, 5000000.00, '{"project_type": "renewable_energy", "government_subsidy_eligible": true}');

-- 查询示例
SELECT * FROM loan_products;