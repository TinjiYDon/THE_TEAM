-- 创建理财金融产品数据库
CREATE DATABASE wealth_management_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建理财金融产品表
CREATE TABLE financial_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) COMMENT '产品全称',
    display_name VARCHAR(50) NOT NULL COMMENT '展示名称（如“余额宝”）',
    product_type ENUM(
        '货币基金',
        '债券基金',
        '混合基金',
        '股票基金',
        '指数基金',
        'QDII基金',
        '银行理财',
        '保险理财',
        '券商集合理财',
        '信托产品'
    ) NOT NULL,
    issuer VARCHAR(100) NOT NULL COMMENT '发行机构',
    product_code VARCHAR(20) UNIQUE COMMENT '产品代码（如基金代码）',
    risk_level ENUM('R1', 'R2', 'R3', 'R4', 'R5') NOT NULL COMMENT '风险等级：R1-保守, R2-稳健, R3-平衡, R4-成长, R5-进取',
    benchmark_min DECIMAL(5,4) COMMENT '预期年化收益下限',
    benchmark_max DECIMAL(5,4) COMMENT '预期年化收益上限',
    historical_return DECIMAL(5,4) COMMENT '历史年化收益率',
    purchase_threshold DECIMAL(10,2) DEFAULT 1.00 NOT NULL COMMENT '首次购买最低金额',
    additional_purchase_min DECIMAL(10,2) DEFAULT 10.00 NOT NULL COMMENT '追加购买最低金额',
    lock_period INT DEFAULT 0 NOT NULL COMMENT '锁定期（天），0 表示无锁定期',
    redemption_settlement_days INT DEFAULT 1 NOT NULL COMMENT '赎回到账天数',
    service_fee_rate DECIMAL(5,4) DEFAULT 0.0000 NOT NULL COMMENT '销售服务费（年化）',
    management_fee_rate DECIMAL(5,4) DEFAULT 0.0000 NOT NULL COMMENT '管理费（年化）',
    custody_fee_rate DECIMAL(5,4) DEFAULT 0.0000 NOT NULL COMMENT '托管费（年化）',
    feature_tags JSON COMMENT '产品标签，如 ["灵活申赎", "保本"]',
    product_description TEXT COMMENT '产品描述',
    prospectus_url VARCHAR(255) COMMENT '产品说明书链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_code (product_code),
    INDEX idx_type (product_type),
    INDEX idx_risk (risk_level),
    INDEX idx_issuer (issuer)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='金融理财产品表';

-- 插入测试数据
INSERT INTO financial_products (
    product_name, display_name, product_type, issuer, product_code, 
    risk_level, benchmark_min, benchmark_max, historical_return,
    purchase_threshold, additional_purchase_min, lock_period, redemption_settlement_days,
    service_fee_rate, management_fee_rate, custody_fee_rate,
    feature_tags, product_description, prospectus_url
) VALUES
-- 货币基金类 (低风险)
('余额宝货币市场基金', '余额宝', '货币基金', '天弘基金', '000198', 'R1', 0.0180, 0.0250, 0.0220, 1.00, 1.00, 0, 1, 0.0025, 0.0030, 0.0010, '["灵活申赎", "实时赎回", "消费支付"]', '面向个人用户的货币市场基金，流动性极佳', 'http://example.com/000198'),
('微信零钱通货币基金', '零钱通', '货币基金', '华夏基金', '000343', 'R1', 0.0190, 0.0260, 0.0235, 0.01, 0.01, 0, 1, 0.0020, 0.0028, 0.0008, '["灵活存取", "消费抵扣", "自动理财"]', '微信平台货币基金，便捷的零钱管理工具', 'http://example.com/000343'),
-- 债券基金类 (中低风险)
('易方达安心回报债券A', '安心回报债A', '债券基金', '易方达基金', '110027', 'R2', 0.0350, 0.0450, 0.0380, 10.00, 10.00, 30, 2, 0.0040, 0.0060, 0.0015, '["稳健收益", "信用债", "利率债"]', '主要投资高信用等级债券，追求稳健回报', 'http://example.com/110027'),
('招商双债增强债券', '招商双债', '债券基金', '招商基金', '161716', 'R2', 0.0400, 0.0500, 0.0420, 100.00, 10.00, 90, 2, 0.0035, 0.0055, 0.0012, '["可转债", "公司债", "增强收益"]', '通过可转债和公司债配置增强收益', 'http://example.com/161716'),
-- 混合基金类 (中风险)
('富国天惠成长混合', '富国天惠', '混合基金', '富国基金', '161005', 'R3', 0.0800, 0.1200, 0.0950, 100.00, 10.00, 180, 3, 0.0080, 0.0150, 0.0020, '["成长股", "价值投资", "长期持有"]', '侧重成长性股票投资，兼顾价值发现', 'http://example.com/161005'),
('景顺长城新兴成长', '景顺新兴成长', '混合基金', '景顺长城基金', '260108', 'R3', 0.0850, 0.1300, 0.1050, 100.00, 10.00, 365, 3, 0.0075, 0.0140, 0.0025, '["消费升级", "新兴产业", "龙头公司"]', '聚焦消费升级和新兴产业投资机会', 'http://example.com/260108'),
-- 股票基金类 (中高风险)
('华夏上证50ETF联接', '上证50ETF', '指数基金', '华夏基金', '001051', 'R4', 0.0900, 0.1500, 0.1250, 100.00, 10.00, 30, 2, 0.0050, 0.0080, 0.0010, '["大盘蓝筹", "指数投资", "低费率"]', '跟踪上证50指数，投资大盘蓝筹股', 'http://example.com/001051'),
('易方达消费行业股票', '易方达消费', '股票基金', '易方达基金', '110022', 'R4', 0.1000, 0.1800, 0.1550, 100.00, 10.00, 365, 3, 0.0120, 0.0180, 0.0025, '["消费行业", "品牌公司", "长期增长"]', '专注消费行业优质公司投资', 'http://example.com/110022'),
-- QDII基金类 (高风险)
('嘉实美国成长股票', '嘉实美国成长', 'QDII基金', '嘉实基金', '000043', 'R5', 0.1200, 0.2000, 0.1680, 100.00, 100.00, 730, 5, 0.0150, 0.0200, 0.0030, '["美股投资", "科技龙头", "全球配置"]', '投资美国成长型上市公司股票', 'http://example.com/000043'),
('华夏全球股票', '华夏全球', 'QDII基金', '华夏基金', '000041', 'R5', 0.1000, 0.1800, 0.1420, 100.00, 100.00, 365, 5, 0.0140, 0.0190, 0.0028, '["全球配置", "分散风险", "多元市场"]', '全球范围内精选优质上市公司', 'http://example.com/000041'),
-- 银行理财类
('招行月月宝', '月月宝', '银行理财', '招商银行', 'CMB001', 'R2', 0.0320, 0.0380, 0.0350, 1000.00, 100.00, 30, 2, 0.0020, 0.0030, 0.0005, '["月度开放", "稳健收益", "银行信用"]', '招商银行月度开放理财产品', 'http://example.com/CMB001'),
('工行安心回报', '工行安心', '银行理财', '工商银行', 'ICBC002', 'R2', 0.0280, 0.0350, 0.0310, 10000.00, 1000.00, 90, 3, 0.0018, 0.0025, 0.0004, '["季度开放", "保本策略", "大行风控"]', '工商银行中短期稳健理财产品', 'http://example.com/ICBC002'),
-- 保险理财类
('平安盛世金生', '盛世金生', '保险理财', '平安保险', 'PA001', 'R2', 0.0300, 0.0400, 0.0350, 5000.00, 1000.00, 1080, 5, 0.0100, 0.0120, 0.0010, '["养老规划", "终身保障", "复利计息"]', '兼具保障和理财功能的养老保险产品', 'http://example.com/PA001'),
('太平财富成长', '财富成长', '保险理财', '太平保险', 'TP002', 'R3', 0.0450, 0.0650, 0.0550, 10000.00, 5000.00, 1825, 7, 0.0120, 0.0150, 0.0015, '["财富传承", "身故保障", "投资连结"]', '投资连结型保险理财产品', 'http://example.com/TP002'),
-- 券商理财类
('中信证券收益增强', '中信收益增强', '券商集合理财', '中信证券', 'ZX001', 'R3', 0.0500, 0.0700, 0.0580, 50000.00, 10000.00, 180, 3, 0.0060, 0.0100, 0.0012, '["绝对收益", "量化策略", "券商资管"]', '券商集合资产管理计划', 'http://example.com/ZX001'),
('海通证券量化对冲', '海通量化', '券商集合理财', '海通证券', 'HT002', 'R3', 0.0400, 0.0600, 0.0480, 100000.00, 50000.00, 365, 4, 0.0080, 0.0120, 0.0015, '["市场中性", "量化对冲", "低波动"]', '采用量化对冲策略的券商产品', 'http://example.com/HT002'),
-- 信托产品类
('中融信托基建项目', '中融基建信托', '信托产品', '中融信托', 'ZR001', 'R4', 0.0700, 0.0850, 0.0780, 1000000.00, 100000.00, 1095, 10, 0.0150, 0.0200, 0.0020, '["基础设施","政府合作", "高净值"]', '投资于基础设施建设的信托计划', 'http://example.com/ZR001'),
('华润信托地产基金', '华润地产信托', '信托产品', '华润信托', 'HR002', 'R4', 0.0800, 0.1000, 0.0890, 2000000.00, 500000.00, 1825, 15, 0.0180, 0.0250, 0.0025, '["房地产", "项目融资", "抵押担保"]', '房地产项目投资信托', 'http://example.com/HR002'),
-- 补充2条热门产品
('蚂蚁战略配售基金', '蚂蚁配售', '混合基金', '易方达基金', '001603', 'R4', 0.0800, 0.1500, 0.1200, 1.00, 1.00, 180, 3, 0.0100, 0.0150, 0.0020, '["战略配售", "新股投资", "科技创新"]', '参与战略配售的创新型基金', 'http://example.com/001603'),
('南方科创板基金', '南方科创板', '股票基金', '南方基金', '007340', 'R5', 0.1200, 0.2500, 0.1880, 10.00, 10.00, 730, 4, 0.0120, 0.0180, 0.0022, '["科创板", "科技创新", "高成长"]', '专注科创板上市公司投资', 'http://example.com/007340');

-- 查询测试
SELECT 
    display_name AS '产品名称',
    issuer AS '发行机构',
    product_code AS '产品代码',
    risk_level AS '风险等级',
    CONCAT(ROUND(benchmark_min * 100, 2), '% - ', ROUND(benchmark_max * 100, 2), '%') AS '预期年化收益',
    CONCAT('¥', purchase_threshold) AS '起投金额',
    lock_period AS '锁定期(天)'
FROM financial_products;