"""
创建3个测试用户
"""
import sqlite3
from pathlib import Path
import hashlib

DB_PATH = Path(__file__).parent / 'data' / 'bill_db.sqlite'

def create_users():
    """创建3个测试用户"""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    
    # 创建 users 表（如果不存在）
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        password_hash TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建3个用户
    users = [
        {
            'username': 'user1',
            'email': 'user1@example.com',
            'phone': '13800138001',
            'password': 'demo123'
        },
        {
            'username': 'user2',
            'email': 'user2@example.com',
            'phone': '13800138002',
            'password': 'demo123'
        },
        {
            'username': 'user3',
            'email': 'user3@example.com',
            'phone': '13800138003',
            'password': 'demo123'
        }
    ]
    
    for user in users:
        password_hash = hashlib.md5(user['password'].encode()).hexdigest()
        # 先检查用户是否已存在
        cur.execute("SELECT id, username FROM users WHERE username=?", (user['username'],))
        existing = cur.fetchone()
        if existing:
            # 更新现有用户的密码和邮箱
            cur.execute("""
            UPDATE users SET email=?, phone=?, password_hash=?
            WHERE username=?
            """, (user['email'], user['phone'], password_hash, user['username']))
            print(f"更新用户: {user['username']} (ID: {existing[0]})")
        else:
            # 创建新用户
            try:
                cur.execute("""
                INSERT INTO users (username, email, phone, password_hash)
                VALUES (?, ?, ?, ?)
                """, (user['username'], user['email'], user['phone'], password_hash))
                print(f"创建用户: {user['username']} (ID: {cur.lastrowid})")
            except sqlite3.IntegrityError as e:
                print(f"创建失败: {user['username']}, 可能邮箱已存在")
    
    conn.commit()
    conn.close()
    print("\n用户创建完成！")
    print("可用用户名：user1, user2, user3")
    print("密码：demo123")

if __name__ == '__main__':
    create_users()

