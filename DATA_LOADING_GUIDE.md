# 数据加载指南

## 数据来源说明

系统优先使用已有数据库中的数据：
- **理财产品**：从 `wealth_management_db.sql` 加载
- **贷款产品**：从 `loan_db.sql` 加载  
- **账单数据**：从已有数据库或通过 `data/unified_data_generator.py` 生成

## 使用方法

### 方法一：自动加载（推荐）

```bash
python load_financial_data.py
```

该脚本会：
1. 检查数据库中现有数据量
2. 如果数据不足（理财产品<20条，贷款产品<20条），从SQL文件加载
3. 如果SQL文件解析失败或仍不够，使用默认虚拟数据补充
4. 账单数据不足时会提示运行生成脚本

### 方法二：手动生成数据

如果需要生成更多账单测试数据：

```bash
python data/unified_data_generator.py
```

## 数据统计

运行后可以查看当前数据量：
```bash
python -c "import sqlite3; conn = sqlite3.connect('data/bill_db.sqlite'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM financial_products'); print('理财产品:', cur.fetchone()[0]); cur.execute('SELECT COUNT(*) FROM loan_products'); print('贷款产品:', cur.fetchone()[0]); cur.execute('SELECT COUNT(*) FROM bills'); print('账单:', cur.fetchone()[0]); conn.close()"
```

## 注意事项

1. **数据优先级**：
   - 优先使用已有数据库数据
   - 其次从SQL文件加载
   - 最后使用默认虚拟数据

2. **数据量要求**：
   - 理财产品：建议至少10条，当前已有25条 ✓
   - 贷款产品：建议至少10条，当前已有25条 ✓
   - 账单数据：建议至少100条，当前已有2150条 ✓

3. **SQL文件格式**：
   - `wealth_management_db.sql`：MySQL格式的理财产品数据
   - `loan_db.sql`：MySQL格式的贷款产品数据
   - 脚本会自动转换为SQLite兼容格式

## 故障排除

### SQL文件解析失败
- 检查文件编码是否为UTF-8
- 确认文件路径正确
- 脚本会自动使用默认数据

### 数据未导入
- 检查数据库中是否已有足够数据（超过阈值则跳过导入）
- 检查表结构是否正确
- 查看错误日志

