"""
从已有SQL文件加载金融产品和贷款产品数据到SQLite数据库
如果数据不够，补充虚拟数据
"""
import sqlite3
import json
import re
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent / 'data' / 'bill_db.sqlite'

def parse_wealth_management_sql(sql_file: Path) -> List[Dict[str, Any]]:
    """解析理财产品SQL文件（MySQL格式转SQLite）"""
    products = []
    
    if not sql_file.exists():
        print(f"文件不存在: {sql_file}")
        return products
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取INSERT语句中的数据
    insert_pattern = r"INSERT INTO financial_products\s*\([^)]+\)\s*VALUES\s*(.+?);"
    matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        # 解析每一行数据
        rows = re.findall(r"\(([^)]+)\)", match)
        for row in rows:
            try:
                # 简单的字段解析（需要根据实际SQL调整）
                fields = [f.strip().strip("'\"") for f in row.split(',')]
                if len(fields) >= 10:
                    products.append({
                        'product_type': fields[2] if len(fields) > 2 else '理财',
                        'product_name': fields[1] if len(fields) > 1 else fields[0],
                        'interest_rate': float(fields[7]) if len(fields) > 7 and fields[7] else None,
                        'min_amount': float(fields[9]) if len(fields) > 9 else 100.0,
                        'max_amount': float(fields[10]) if len(fields) > 10 else 1000000.0,
                        'term_months': int(fields[12]) // 30 if len(fields) > 12 else 12,
                        'risk_level': fields[5].lower() if len(fields) > 5 else 'medium',
                        'description': fields[0] if len(fields) > 0 else ''
                    })
            except Exception as e:
                print(f"解析行失败: {row[:50]}... 错误: {e}")
                continue
    
    return products

def parse_loan_sql(sql_file: Path) -> List[Dict[str, Any]]:
    """解析贷款产品SQL文件（MySQL格式转SQLite）"""
    products = []
    
    if not sql_file.exists():
        print(f"文件不存在: {sql_file}")
        return products
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取INSERT语句中的数据
    insert_pattern = r"INSERT INTO loan_products\s*\([^)]+\)\s*VALUES\s*(.+?);"
    matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        rows = re.findall(r"\(([^)]+)\)", match)
        for row in rows:
            try:
                # 解析字段
                fields = [f.strip().strip("'\"") for f in row.split(',')]
                if len(fields) >= 7:
                    # eligibility_criteria 可能是JSON字符串
                    eligibility = fields[7] if len(fields) > 7 else '{}'
                    try:
                        json.loads(eligibility)
                    except:
                        eligibility = '{}'
                    
                    products.append({
                        'name': fields[0],
                        'description': fields[1] if len(fields) > 1 else '',
                        'interest_rate': float(fields[2]) if len(fields) > 2 else 6.0,
                        'term_min': int(fields[3]) if len(fields) > 3 else 12,
                        'term_max': int(fields[4]) if len(fields) > 4 else 60,
                        'amount_min': float(fields[5]) if len(fields) > 5 else 10000.0,
                        'amount_max': float(fields[6]) if len(fields) > 6 else 500000.0,
                        'eligibility_criteria': eligibility
                    })
            except Exception as e:
                print(f"解析行失败: {row[:50]}... 错误: {e}")
                continue
    
    return products

def load_from_sql_files() -> tuple[List[Dict], List[Dict]]:
    """从SQL文件加载数据"""
    base_dir = Path(__file__).parent
    
    # 尝试多个可能的路径
    wealth_sql_paths = [
        base_dir / 'wealth_management_db.sql',
        base_dir / 'data' / 'wealth_management_db.sql',
    ]
    
    loan_sql_paths = [
        base_dir / 'loan_db.sql',
        base_dir / 'data' / 'loan_db.sql',
    ]
    
    financial_products = []
    loan_products = []
    
    # 加载理财产品
    for path in wealth_sql_paths:
        if path.exists():
            print(f"从 {path} 加载理财产品...")
            financial_products = parse_wealth_management_sql(path)
            if financial_products:
                break
    
    # 加载贷款产品
    for path in loan_sql_paths:
        if path.exists():
            print(f"从 {path} 加载贷款产品...")
            loan_products = parse_loan_sql(path)
            if loan_products:
                break
    
    return financial_products, loan_products

def get_default_financial_products() -> List[Dict[str, Any]]:
    """生成默认理财产品数据（如果SQL文件解析失败）"""
    return [
        {
            'product_type': '货币基金',
            'product_name': '余额宝',
            'interest_rate': 2.5,
            'min_amount': 1.0,
            'max_amount': 1000000.0,
            'term_months': 0,
            'risk_level': 'low',
            'description': '面向个人用户的货币市场基金，流动性极佳'
        },
        {
            'product_type': '债券基金',
            'product_name': '稳健理财A',
            'interest_rate': 4.5,
            'min_amount': 100.0,
            'max_amount': 500000.0,
            'term_months': 12,
            'risk_level': 'low',
            'description': '主要投资高信用等级债券，追求稳健回报'
        },
        {
            'product_type': '混合基金',
            'product_name': '成长基金B',
            'interest_rate': 6.8,
            'min_amount': 100.0,
            'max_amount': 1000000.0,
            'term_months': 36,
            'risk_level': 'medium',
            'description': '适合中等风险承受能力投资者'
        },
        {
            'product_type': '股票基金',
            'product_name': '成长股票基金',
            'interest_rate': 8.5,
            'min_amount': 100.0,
            'max_amount': 2000000.0,
            'term_months': 60,
            'risk_level': 'high',
            'description': '投资成长型股票，追求长期收益'
        },
        {
            'product_type': '银行理财',
            'product_name': '月月宝',
            'interest_rate': 3.5,
            'min_amount': 1000.0,
            'max_amount': 500000.0,
            'term_months': 1,
            'risk_level': 'low',
            'description': '月度开放理财产品'
        }
    ]

def get_default_loan_products() -> List[Dict[str, Any]]:
    """生成默认贷款产品数据（如果SQL文件解析失败）"""
    return [
        {
            'name': '个人消费贷',
            'description': '用于日常消费的信用贷款',
            'interest_rate': 6.50,
            'term_min': 12,
            'term_max': 60,
            'amount_min': 10000.0,
            'amount_max': 500000.0,
            'eligibility_criteria': json.dumps({"credit_score_min": 600, "income_proof_required": True})
        },
        {
            'name': '房屋抵押贷',
            'description': '以房产为抵押的长期贷款',
            'interest_rate': 4.90,
            'term_min': 60,
            'term_max': 360,
            'amount_min': 100000.0,
            'amount_max': 10000000.0,
            'eligibility_criteria': json.dumps({"property_type": "residential", "ltv_ratio_max": 70})
        },
        {
            'name': '小微企业贷',
            'description': '支持小微企业的经营贷款',
            'interest_rate': 8.00,
            'term_min': 6,
            'term_max': 36,
            'amount_min': 50000.0,
            'amount_max': 2000000.0,
            'eligibility_criteria': json.dumps({"business_age_min": 1, "annual_revenue_min": 500000})
        },
        {
            'name': '公务员专享贷',
            'description': '针对公务员和事业单位员工的低利率信用贷款',
            'interest_rate': 4.50,
            'term_min': 12,
            'term_max': 60,
            'amount_min': 50000.0,
            'amount_max': 800000.0,
            'eligibility_criteria': json.dumps({"employment_type": "public_sector", "credit_score_min": 620})
        },
        {
            'name': '汽车消费贷',
            'description': '用于购买新车或二手车的专项贷款',
            'interest_rate': 5.80,
            'term_min': 24,
            'term_max': 60,
            'amount_min': 30000.0,
            'amount_max': 1000000.0,
            'eligibility_criteria': json.dumps({"down_payment_ratio_min": 20, "vehicle_age_max": 5})
        }
    ]

def load_to_database():
    """加载数据到数据库"""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # 检查现有数据量
    cur.execute("SELECT COUNT(*) FROM financial_products")
    existing_financial = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM loan_products")
    existing_loan = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM bills")
    existing_bills = cur.fetchone()[0]
    
    print(f"\n当前数据库状态:")
    print(f"  理财产品: {existing_financial} 条")
    print(f"  贷款产品: {existing_loan} 条")
    print(f"  账单数据: {existing_bills} 条")
    
    # 从SQL文件加载数据
    financial_products, loan_products = load_from_sql_files()
    
    # 如果SQL文件解析失败或数据不够，使用默认数据
    if not financial_products:
        print("\n未找到或无法解析理财产品SQL文件，使用默认数据...")
        financial_products = get_default_financial_products()
    
    if not loan_products:
        print("\n未找到或无法解析贷款产品SQL文件，使用默认数据...")
        loan_products = get_default_loan_products()
    
    print(f"\n准备导入:")
    print(f"  理财产品: {len(financial_products)} 条")
    print(f"  贷款产品: {len(loan_products)} 条")
    
    # 导入理财产品（如果现有数据少于10条，则导入）
    if existing_financial < 10:
        print(f"\n导入理财产品（现有 {existing_financial} 条，目标至少 10 条）...")
        for product in financial_products:
            try:
                cur.execute("""
                INSERT OR IGNORE INTO financial_products 
                (product_type, product_name, interest_rate, min_amount, max_amount, term_months, risk_level, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['product_type'],
                    product['product_name'],
                    product['interest_rate'],
                    product['min_amount'],
                    product['max_amount'],
                    product['term_months'],
                    product['risk_level'],
                    product['description']
                ))
            except Exception as e:
                print(f"导入理财产品失败: {product.get('product_name', '未知')}, 错误: {e}")
        
        conn.commit()
        print(f"理财产品导入完成")
    else:
        print(f"\n理财产品已有 {existing_financial} 条，跳过导入")
    
    # 导入贷款产品（如果现有数据少于10条，则导入）
    if existing_loan < 10:
        print(f"\n导入贷款产品（现有 {existing_loan} 条，目标至少 10 条）...")
        for product in loan_products:
            try:
                cur.execute("""
                INSERT OR IGNORE INTO loan_products
                (name, description, interest_rate, term_min, term_max, amount_min, amount_max, eligibility_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['name'],
                    product['description'],
                    product['interest_rate'],
                    product['term_min'],
                    product['term_max'],
                    product['amount_min'],
                    product['amount_max'],
                    product['eligibility_criteria']
                ))
            except Exception as e:
                print(f"导入贷款产品失败: {product.get('name', '未知')}, 错误: {e}")
        
        conn.commit()
        print(f"贷款产品导入完成")
    else:
        print(f"\n贷款产品已有 {existing_loan} 条，跳过导入")
    
    # 检查账单数据
    if existing_bills < 100:
        print(f"\n警告: 账单数据较少（{existing_bills} 条），建议运行 data/unified_data_generator.py 生成更多测试数据")
    
    # 最终统计
    cur.execute("SELECT COUNT(*) FROM financial_products")
    final_financial = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM loan_products")
    final_loan = cur.fetchone()[0]
    
    print(f"\n最终数据统计:")
    print(f"  理财产品: {final_financial} 条")
    print(f"  贷款产品: {final_loan} 条")
    print(f"  账单数据: {existing_bills} 条")
    
    conn.close()
    print("\n数据加载完成！")

if __name__ == '__main__':
    load_to_database()

