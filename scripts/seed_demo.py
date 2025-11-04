import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = str(BASE_DIR / 'data' / 'bill_db.sqlite')

CITIES = ['shanghai', 'beijing', 'suzhou']
CITY_NAME = {
    'shanghai': '上海',
    'beijing': '北京',
    'suzhou': '苏州',
}

USERS = [
    (101, 'userA', 'beijing'),
    (102, 'userB_premium', 'shanghai'),
    (103, 'userC', 'suzhou'),
    (104, 'userD_catering', 'shanghai'),
]

GROUPS = [
    ('上海餐饮群', 'city', 'shanghai', 'catering', '上海美食与餐饮交流'),
    ('北京餐饮群', 'city', 'beijing', 'catering', '北京美食与餐饮交流'),
    ('苏州餐饮群', 'city', 'suzhou', 'catering', '苏州美食与餐饮交流'),
    ('综合理财群', 'city', 'shanghai', 'finance', '理财交流'),
    ('北京教育群', 'city', 'beijing', 'education', '教育话题交流'),
    ('上海亲子群', 'city', 'shanghai', 'parenting', '亲子活动交流'),
    ('苏州通勤族群', 'city', 'suzhou', 'commute', '通勤经验分享'),
    ('北京美食探店群', 'city', 'beijing', 'catering', '探店分享'),
]

CATEGORIES_A = ['餐饮','交通','其他']
CATEGORIES_B = ['购物','交通','出行','餐饮']
CATEGORIES_C = ['教育','医疗','其他','餐饮']

random.seed(42)

def ensure_users(conn):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT)")
    for uid, uname, _ in USERS:
        cur.execute("INSERT OR IGNORE INTO users(id, username, email) VALUES(?,?,?)", (uid, uname, f"{uname}@example.com"))
    conn.commit()


def ensure_groups(conn):
    cur = conn.cursor()
    # ensure tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level TEXT,
            province TEXT,
            city TEXT,
            district TEXT,
            type TEXT,
            cover_url TEXT,
            description TEXT,
            is_public INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TEXT DEFAULT (datetime('now')),
            UNIQUE(group_id, user_id)
        )
    """)
    for name, level, city, gtype, desc in GROUPS:
        cover = f"/groups/{city}-{gtype}.jpg"
        cur.execute(
            "INSERT INTO groups(name, level, city, type, cover_url, description) SELECT ?,?,?,?,?,? WHERE NOT EXISTS(SELECT 1 FROM groups WHERE name=?)",
            (name, level, CITY_NAME[city], gtype, cover, desc, name)
        )
    conn.commit()


def join_members(conn):
    cur = conn.cursor()
    # B(102) -> 综合理财群；D(104) -> 上海餐饮群
    # 查群ID
    def gid(name):
        c2 = conn.cursor()
        c2.execute("SELECT id FROM groups WHERE name=?", (name,))
        row = c2.fetchone()
        return row[0] if row else None
    mapping = [
        (gid('综合理财群'), 102),
        (gid('上海餐饮群'), 104),
    ]
    for g_id, u_id in mapping:
        if not g_id:
            continue
        cur.execute("INSERT OR IGNORE INTO group_members(group_id, user_id) VALUES(?,?)", (g_id, u_id))
    conn.commit()


def rand_amount(base, spread):
    return round(max(1, random.gauss(base, spread)), 2)


def ensure_bills(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consume_time TEXT NOT NULL,
            amount REAL NOT NULL,
            merchant TEXT NOT NULL,
            category TEXT,
            payment_method TEXT,
            location TEXT,
            description TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    now = datetime.now()
    for uid, uname, city in USERS:
        # 模板选择
        if uid == 102:
            cats = CATEGORIES_B
        elif uid == 103:
            cats = CATEGORIES_C
        elif uid == 104:
            cats = ['餐饮','餐饮','餐饮','交通','其他']
        else:
            cats = CATEGORIES_A
        # 生成 60~120 笔
        n = random.randint(60, 120)
        for i in range(n):
            days_ago = random.randint(0, 89)
            t = now - timedelta(days=days_ago, hours=random.randint(0,23), minutes=random.randint(0,59))
            cat = random.choice(cats)
            if cat == '餐饮':
                amount = rand_amount(45, 20)
                merchant = random.choice(['星巴克','麦当劳','海底捞','本帮菜','兰州拉面'])
            elif cat in ('购物','出行'):
                amount = rand_amount(200, 120)
                merchant = random.choice(['天猫','京东','高铁','滴滴'])
            elif cat in ('教育','医疗'):
                amount = rand_amount(300, 150)
                merchant = random.choice(['培训机构','医院'])
            else:
                amount = rand_amount(60, 60)
                merchant = random.choice(['便利店','超市','其他'])
            cur.execute(
                """
                INSERT INTO bills(user_id, consume_time, amount, merchant, category, payment_method, location, description, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (uid, t.strftime('%Y-%m-%d %H:%M:%S'), amount, merchant, cat, random.choice(['微信','支付宝','银行卡']), CITY_NAME.get(city,''), '', t.strftime('%Y-%m-%d %H:%M:%S'), t.strftime('%Y-%m-%d %H:%M:%S'))
            )
    conn.commit()


def ensure_posts(conn):
    cur = conn.cursor()
    # 确保表结构包含新字段
    try:
        cur.execute("ALTER TABLE community_posts ADD COLUMN group_id INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE community_posts ADD COLUMN visibility TEXT DEFAULT 'public'")
    except:
        pass
    try:
        cur.execute("ALTER TABLE community_posts ADD COLUMN attached_bill_id INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE community_posts ADD COLUMN location_city TEXT")
    except:
        pass
    
    # 获取群组ID
    def gid(name):
        c2 = conn.cursor()
        c2.execute("SELECT id FROM groups WHERE name=?", (name,))
        row = c2.fetchone()
        return row[0] if row else None
    
    # 获取账单ID
    def bid(user_id, category=None, limit=1):
        c2 = conn.cursor()
        if category:
            c2.execute("SELECT id FROM bills WHERE user_id=? AND category=? ORDER BY consume_time DESC LIMIT ?", (user_id, category, limit))
        else:
            c2.execute("SELECT id FROM bills WHERE user_id=? ORDER BY consume_time DESC LIMIT ?", (user_id, limit))
        rows = c2.fetchall()
        return [r[0] for r in rows]
    
    # 帖子数据：不同用户在不同群组发帖
    posts_data = [
        # 上海餐饮群 - D(104) 发帖
        (104, '今晚这家太香了！', '推荐一家上海本帮菜，性价比高～', gid('上海餐饮群'), 'public', bid(104, '餐饮', 1)[0] if bid(104, '餐饮', 1) else None, '上海'),
        (104, '周末聚餐好去处', '和朋友一起去了这家店，环境不错，菜品也很棒！', gid('上海餐饮群'), 'public', bid(104, '餐饮', 1)[0] if bid(104, '餐饮', 1) else None, '上海'),
        
        # 综合理财群 - B(102) 发帖
        (102, '理财心得分享', '最近尝试了一些理财产品，收益还不错，分享给大家', gid('综合理财群'), 'public', None, '上海'),
        (102, '投资建议', '建议新手先从稳健型产品开始，不要盲目追求高收益', gid('综合理财群'), 'public', None, '上海'),
        
        # 北京餐饮群 - 其他用户发帖（模拟）
        (101, '北京美食推荐', '今天发现一家不错的餐厅，推荐给大家', gid('北京餐饮群'), 'same_city', bid(101, '餐饮', 1)[0] if bid(101, '餐饮', 1) else None, '北京'),
        (101, '周末探店', '周末去了一家新开的餐厅，味道不错价格也合理', gid('北京餐饮群'), 'same_city', None, '北京'),
        
        # 北京教育群 - C(103) 发帖（虽然是苏州用户，但可以跨城查看）
        (103, '教育支出规划', '分享一下孩子的教育支出规划，希望能帮助到大家', gid('北京教育群'), 'public', bid(103, '教育', 1)[0] if bid(103, '教育', 1) else None, '苏州'),
        
        # 广场帖子（不指定群组）
        (104, '分享今日消费', '今天消费有点多，大家有什么省钱建议吗？', None, 'public', bid(104, None, 1)[0] if bid(104, None, 1) else None, '上海'),
        (102, '购物心得', '双十一购物分享，哪些值得买哪些不值得', None, 'public', bid(102, '购物', 1)[0] if bid(102, '购物', 1) else None, '上海'),
        (103, '医疗支出记录', '记录一下本月的医疗支出，提醒大家注意健康', None, 'public', bid(103, '医疗', 1)[0] if bid(103, '医疗', 1) else None, '苏州'),
        
        # 同城可见帖子
        (101, '北京交通出行', '分享北京出行经验，希望能帮助到同城的朋友', None, 'same_city', bid(101, '交通', 1)[0] if bid(101, '交通', 1) else None, '北京'),
        (104, '上海本地推荐', '上海本地人推荐的好去处，仅同城可见', None, 'same_city', None, '上海'),
    ]
    
    # 插入帖子
    for user_id, title, content, group_id, visibility, bill_id, city in posts_data:
        # 检查是否已存在
        cur.execute("SELECT COUNT(*) FROM community_posts WHERE user_id=? AND title=?", (user_id, title))
        if cur.fetchone()[0] > 0:
            continue
        
        likes = random.randint(0, 10)
        comments = random.randint(0, 5)
        cur.execute(
            """INSERT INTO community_posts(user_id, title, content, bill_id, group_id, visibility, attached_bill_id, location_city, likes_count, comments_count, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,datetime('now', '-' || (random() % 7) || ' days'))""",
            (user_id, title, content, bill_id, group_id, visibility, bill_id, city, likes, comments)
        )
    
    conn.commit()


def main():
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_users(conn)
    ensure_groups(conn)
    join_members(conn)
    ensure_bills(conn)
    ensure_posts(conn)
    conn.close()
    print('Demo data seeded.')


if __name__ == '__main__':
    main()
