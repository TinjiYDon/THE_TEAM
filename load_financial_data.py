"""
从已有SQL文件加载金融产品和贷款产品数据
优先使用SQL文件中的数据，如果不够则补充虚拟数据
"""
import sqlite3
import json
import re
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent / 'data' / 'bill_db.sqlite'

def parse_financial_products_from_sql(sql_file: Path) -> List[Dict[str, Any]]:
    """从SQL文件解析理财产品数据"""
    products = []
    
    if not sql_file.exists():
        print(f"文件不存在: {sql_file}")
        return products
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取INSERT语句
    insert_match = re.search(r"INSERT INTO financial_products[^;]+VALUES\s*(.+?);", content, re.DOTALL | re.IGNORECASE)
    if not insert_match:
        print("未找到INSERT语句")
        return products
    
    # 解析每一行数据
    rows_text = insert_match.group(1)
    # 移除注释行
    rows_text = re.sub(r'--[^\n]*\n', '\n', rows_text)
    
    # 解析每个括号内的数据
    row_pattern = r"\(([^)]+)\)"
    for row_match in re.finditer(row_pattern, rows_text):
        row = row_match.group(1)
        
        # 处理字段值（考虑引号内的逗号）
        fields = []
        current_field = ""
        in_quotes = False
        quote_char = None
        
        for char in row:
            if char in ["'", '"'] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_field += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_field += char
            elif char == ',' and not in_quotes:
                fields.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        
        if current_field:
            fields.append(current_field.strip())
        
        # 解析字段
        if len(fields) >= 10:
            try:
                # 字段顺序：product_name, display_name, product_type, issuer, product_code, 
                # risk_level, benchmark_min, benchmark_max, historical_return, ...
                display_name = fields[1].strip("'\"") if len(fields) > 1 else fields[0].strip("'\"")
                product_type = fields[2].strip("'\"") if len(fields) > 2 else '理财'
                
                # 风险等级转换 R1-R5 -> low/medium/high
                risk_level_str = fields[5].strip("'\"") if len(fields) > 5 else 'R2'
                risk_map = {'R1': 'low', 'R2': 'low', 'R3': 'medium', 'R4': 'high', 'R5': 'high'}
                risk_level = risk_map.get(risk_level_str, 'medium')
                
                # 解析收益率（取中间值或历史收益率）
                benchmark_min = float(fields[6]) if len(fields) > 6 and fields[6] != 'NULL' else 0.0
                benchmark_max = float(fields[7]) if len(fields) > 7 and fields[7] != 'NULL' else 0.0
                historical_return = float(fields[8]) if len(fields) > 8 and fields[8] != 'NULL' else 0.0
                interest_rate = historical_return if historical_return > 0 else (benchmark_min + benchmark_max) / 2
                
                # 转换为百分比（如果小于1则乘以100）
                if interest_rate < 1:
                    interest_rate = interest_rate * 100
                
                purchase_threshold = float(fields[9]) if len(fields) > 9 and fields[9] != 'NULL' else 100.0
                lock_period = int(float(fields[11])) if len(fields) > 11 and fields[11] != 'NULL' else 0
                term_months = max(lock_period // 30, 12) if lock_period > 0 else 12
                
                description = fields[18].strip("'\"") if len(fields) > 18 else display_name
                
                products.append({
                    'product_type': product_type,
                    'product_name': display_name,
                    'interest_rate': round(interest_rate, 2),
                    'min_amount': purchase_threshold,
                    'max_amount': purchase_threshold * 10000,  # 估算最大金额
                    'term_months': term_months,
                    'risk_level': risk_level,
                    'description': description
                })
            except Exception as e:
                print(f"解析失败: {fields[0][:50] if fields else '未知'}, 错误: {e}")
                continue
    
    return products

def parse_loan_products_from_sql(sql_file: Path) -> List[Dict[str, Any]]:
    """从SQL文件解析贷款产品数据"""
    products = []
    
    if not sql_file.exists():
        print(f"文件不存在: {sql_file}")
        return products
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取INSERT语句
    insert_match = re.search(r"INSERT INTO loan_products[^;]+VALUES\s*(.+?);", content, re.DOTALL | re.IGNORECASE)
    if not insert_match:
        print("未找到INSERT语句")
        return products
    
    # 解析每一行
    rows_text = insert_match.group(1)
    row_pattern = r"\(([^)]+)\)"
    
    for row_match in re.finditer(row_pattern, rows_text):
        row = row_match.group(1)
        
        # 处理字段值
        fields = []
        current_field = ""
        in_quotes = False
        quote_char = None
        
        for char in row:
            if char in ["'", '"'] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_field += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_field += char
            elif char == ',' and not in_quotes:
                fields.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        
        if current_field:
            fields.append(current_field.strip())
        
        if len(fields) >= 7:
            try:
                eligibility = fields[7].strip("'\"") if len(fields) > 7 else '{}'
                # 验证JSON格式
                try:
                    json.loads(eligibility)
                except:
                    eligibility = '{}'
                
                products.append({
                    'name': fields[0].strip("'\""),
                    'description': fields[1].strip("'\""),
                    'interest_rate': float(fields[2]) if fields[2] != 'NULL' else 6.0,
                    'term_min': int(float(fields[3])) if fields[3] != 'NULL' else 12,
                    'term_max': int(float(fields[4])) if fields[4] != 'NULL' else 60,
                    'amount_min': float(fields[5]) if fields[5] != 'NULL' else 10000.0,
                    'amount_max': float(fields[6]) if fields[6] != 'NULL' else 500000.0,
                    'eligibility_criteria': eligibility
                })
            except Exception as e:
                print(f"解析失败: {fields[0][:50] if fields else '未知'}, 错误: {e}")
                continue
    
    return products

def get_default_financial_products() -> List[Dict[str, Any]]:
    """默认理财产品（当SQL解析失败时使用）"""
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
        }
    ]

def get_default_loan_products() -> List[Dict[str, Any]]:
    """默认贷款产品（当SQL解析失败时使用）"""
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
        }
    ]

def load_financial_data():
    """加载金融产品数据到数据库"""
    base_dir = Path(__file__).parent
    
    # 查找SQL文件
    wealth_sql = base_dir / 'wealth_management_db.sql'
    loan_sql = base_dir / 'loan_db.sql'
    
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # 检查现有数据
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
    financial_products = []
    loan_products = []
    
    if wealth_sql.exists() and existing_financial < 20:
        print(f"\n从 {wealth_sql.name} 加载理财产品...")
        financial_products = parse_financial_products_from_sql(wealth_sql)
        print(f"解析到 {len(financial_products)} 条理财产品")
    
    if loan_sql.exists() and existing_loan < 20:
        print(f"\n从 {loan_sql.name} 加载贷款产品...")
        loan_products = parse_loan_products_from_sql(loan_sql)
        print(f"解析到 {len(loan_products)} 条贷款产品")
    
    # 如果解析失败或数据不够，使用默认数据
    if not financial_products and existing_financial < 10:
        print("\n使用默认理财产品数据...")
        financial_products = get_default_financial_products()
    
    if not loan_products and existing_loan < 10:
        print("\n使用默认贷款产品数据...")
        loan_products = get_default_loan_products()
    
    # 导入理财产品
    if financial_products and existing_financial < 20:
        print(f"\n导入理财产品...")
        imported = 0
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
                if cur.rowcount > 0:
                    imported += 1
            except Exception as e:
                print(f"导入失败: {product.get('product_name', '未知')}, 错误: {e}")
        
        conn.commit()
        print(f"成功导入 {imported} 条理财产品")
    else:
        print(f"\n理财产品已有 {existing_financial} 条，无需导入")
    
    # 导入贷款产品
    if loan_products and existing_loan < 20:
        print(f"\n导入贷款产品...")
        imported = 0
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
                if cur.rowcount > 0:
                    imported += 1
            except Exception as e:
                print(f"导入失败: {product.get('name', '未知')}, 错误: {e}")
        
        conn.commit()
        print(f"成功导入 {imported} 条贷款产品")
    else:
        print(f"\n贷款产品已有 {existing_loan} 条，无需导入")
    
    # 最终统计
    cur.execute("SELECT COUNT(*) FROM financial_products")
    final_financial = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM loan_products")
    final_loan = cur.fetchone()[0]
    
    print(f"\n最终数据统计:")
    print(f"  理财产品: {final_financial} 条")
    print(f"  贷款产品: {final_loan} 条")
    print(f"  账单数据: {existing_bills} 条")
    
    if existing_bills < 100:
        print(f"\n提示: 账单数据较少，可运行以下命令生成更多测试数据:")
        print(f"  python data/unified_data_generator.py")
    
    conn.close()
    print("\n数据加载完成！")

if __name__ == '__main__':
    load_financial_data()

