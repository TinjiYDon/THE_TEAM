"""生成更多金融产品数据"""
import sqlite3
import random
from src.config import DATABASE_PATH

def generate_financial_products():
    """生成更多金融产品"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    # 检查当前数量
    cursor.execute("SELECT COUNT(*) FROM financial_products")
    current_count = cursor.fetchone()[0]
    
    if current_count >= 100:
        print(f"金融产品数量已充足: {current_count} 条")
        conn.close()
        return
    
    # 生成产品
    product_types = ['货币基金', '债券基金', '混合基金', '股票基金', '银行理财', '保险理财', '定期存款', '结构性存款']
    risk_levels = ['R1', 'R2', 'R3', 'R4', 'R5']
    
    products = []
    for i in range(100 - current_count):
        product_type = random.choice(product_types)
        risk_level = random.choice(risk_levels)
        
        # 根据风险级别调整利率
        if risk_level == 'R1':
            interest_rate = round(random.uniform(2.0, 4.0), 2)
            min_amount = random.choice([100, 1000, 5000])
        elif risk_level == 'R2':
            interest_rate = round(random.uniform(3.5, 5.5), 2)
            min_amount = random.choice([1000, 5000, 10000])
        elif risk_level == 'R3':
            interest_rate = round(random.uniform(4.5, 7.0), 2)
            min_amount = random.choice([5000, 10000, 50000])
        elif risk_level == 'R4':
            interest_rate = round(random.uniform(6.0, 9.0), 2)
            min_amount = random.choice([10000, 50000, 100000])
        else:  # R5
            interest_rate = round(random.uniform(8.0, 15.0), 2)
            min_amount = random.choice([50000, 100000, 500000])
        
        product_name = f"{product_type}{random.randint(100, 999)}号"
        max_amount = min_amount * random.randint(10, 100)
        term_months = random.choice([3, 6, 12, 24, 36])
        
        description = f"适合{risk_level}风险等级投资者的{product_type}产品，预期年化收益率{interest_rate}%"
        
        products.append((
            product_type,
            product_name,
            interest_rate / 100,  # 转换为小数
            min_amount,
            max_amount,
            term_months,
            risk_level,
            description
        ))
    
    # 批量插入
    cursor.executemany("""
        INSERT INTO financial_products 
        (product_type, product_name, interest_rate, min_amount, max_amount, term_months, risk_level, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, products)
    
    conn.commit()
    new_count = cursor.execute("SELECT COUNT(*) FROM financial_products").fetchone()[0]
    print(f"成功生成 {len(products)} 条金融产品")
    print(f"当前金融产品总数: {new_count} 条")
    conn.close()

if __name__ == "__main__":
    generate_financial_products()

