"""检查数据库表结构"""
import sqlite3

conn = sqlite3.connect('data/bill_db.sqlite')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

for table in ['community_posts', 'bills']:
    if table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        print(f"\n{table} columns:")
        for col in columns:
            print(f"  {col[1]} {col[2]}")

conn.close()

