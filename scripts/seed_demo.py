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
    # 扩展字段：age, job
    try:
        cur.execute("ALTER TABLE users ADD COLUMN age INTEGER")
    except:
        pass
    try:
        cur.execute("ALTER TABLE users ADD COLUMN job TEXT")
    except:
        pass
    # 填充演示年龄/职业
    jobs = ['工程师','教师','销售','设计师','产品经理','运营','学生','医生']
    for uid, _, _ in USERS:
        cur.execute("UPDATE users SET age = COALESCE(age, ?), job = COALESCE(job, ?) WHERE id=?",
                    (random.randint(22, 48), random.choice(jobs), uid))
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
    # 群组成员映射（大幅增加，确保每个群都有成员）
    mapping = [
        # B(102) - 订购用户，加入综合理财群
        (gid('综合理财群'), 102),
        # D(104) - 餐饮Top1，加入上海餐饮群
        (gid('上海餐饮群'), 104),
        # A(101) - 北京用户，加入北京餐饮群
        (gid('北京餐饮群'), 101),
        # C(103) - 苏州用户，加入苏州本地生活群
        (gid('苏州本地生活群'), 103),
        # 让一些用户也加入综合理财群（多群）
        (gid('综合理财群'), 101),
        (gid('综合理财群'), 104),
        # 让一些用户也加入北京教育群
        (gid('北京教育群'), 103),
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
            # 餐饮Top1且领先≥20%：80%餐饮，10%交通，10%其他
            cats = ['餐饮','餐饮','餐饮','餐饮','餐饮','餐饮','餐饮','餐饮','交通','其他']
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
    
    # 帖子数据：大幅增加帖子数量，覆盖更多场景
    posts_data = [
        # === 上海餐饮群 - D(104) 发帖 ===
        (104, '今晚这家太香了！', '推荐一家上海本帮菜，性价比高～红烧肉入口即化！', gid('上海餐饮群'), 'public', bid(104, '餐饮', 1)[0] if bid(104, '餐饮', 1) else None, '上海'),
        (104, '周末聚餐好去处', '和朋友一起去了这家店，环境不错，菜品也很棒！人均150', gid('上海餐饮群'), 'public', bid(104, '餐饮', 1)[0] if bid(104, '餐饮', 1) else None, '上海'),
        (104, '早餐新发现', '今早路过一家早餐铺，生煎包真香！只要8块钱', gid('上海餐饮群'), 'public', bid(104, '餐饮', 1)[0] if bid(104, '餐饮', 1) else None, '上海'),
        (104, '午餐推荐', '公司附近新开的面馆，味道正宗价格实惠', gid('上海餐饮群'), 'public', None, '上海'),
        (104, '晚餐打卡', '今晚又去了那家日料，海鲜超新鲜！', gid('上海餐饮群'), 'public', None, '上海'),
        
        # === 综合理财群 - B(102) 发帖 ===
        (102, '理财心得分享', '最近尝试了一些理财产品，收益还不错，年化6%左右', gid('综合理财群'), 'public', None, '上海'),
        (102, '投资建议', '建议新手先从稳健型产品开始，不要盲目追求高收益', gid('综合理财群'), 'public', None, '上海'),
        (102, '基金定投经验', '坚持定投一年了，虽然收益不高但很稳定', gid('综合理财群'), 'public', None, '上海'),
        (102, '消费规划心得', '分享一下我的每月消费规划，30%储蓄很重要', gid('综合理财群'), 'public', None, '上海'),
        (102, '保险配置分享', '给家人配置了重疾险和意外险，分享一下我的经验', gid('综合理财群'), 'public', None, '上海'),
        
        # === 北京餐饮群 - A(101) 发帖 ===
        (101, '北京美食推荐', '今天发现一家不错的餐厅，烤鸭很正宗！', gid('北京餐饮群'), 'same_city', bid(101, '餐饮', 1)[0] if bid(101, '餐饮', 1) else None, '北京'),
        (101, '周末探店', '周末去了一家新开的餐厅，味道不错价格也合理', gid('北京餐饮群'), 'same_city', None, '北京'),
        (101, '工作日午餐', '公司楼下新开了一家快餐店，15块钱吃饱', gid('北京餐饮群'), 'same_city', None, '北京'),
        (101, '火锅推荐', '冬天就要吃火锅！推荐一家性价比超高的店', gid('北京餐饮群'), 'same_city', None, '北京'),
        
        # === 苏州本地生活群 - C(103) 发帖 ===
        (103, '教育支出规划', '分享一下孩子的教育支出规划，每年预留3万左右', gid('苏州本地生活群'), 'public', bid(103, '教育', 1)[0] if bid(103, '教育', 1) else None, '苏州'),
        (103, '医疗保健经验', '定期体检很重要，分享一下我的体检套餐选择', gid('苏州本地生活群'), 'public', None, '苏州'),
        (103, '苏州周边游', '周末带家人去周边玩，花费不多景色很美', gid('苏州本地生活群'), 'same_city', None, '苏州'),
        
        # === 广场帖子（不指定群组，公开可见） ===
        (104, '分享今日消费', '今天消费有点多，吃了顿大餐120块，大家有什么省钱建议吗？', None, 'public', bid(104, None, 1)[0] if bid(104, None, 1) else None, '上海'),
        (104, '消费反思', '这个月餐饮支出超标了，下个月要控制一下', None, 'public', None, '上海'),
        (102, '购物心得', '双十一购物分享，买了很多东西但其实有些不需要', None, 'public', bid(102, '购物', 1)[0] if bid(102, '购物', 1) else None, '上海'),
        (102, '理性消费建议', '冲动消费是大忌，建议大家列购物清单', None, 'public', None, '上海'),
        (103, '医疗支出记录', '记录一下本月的医疗支出，提醒大家注意健康', None, 'public', bid(103, '医疗', 1)[0] if bid(103, '医疗', 1) else None, '苏州'),
        (103, '家庭开支管理', '分享一下我的家庭开支管理经验', None, 'public', None, '苏州'),
        (101, '通勤成本优化', '每月通勤费用400+，有什么省钱办法吗', None, 'public', bid(101, '交通', 1)[0] if bid(101, '交通', 1) else None, '北京'),
        (101, '生活技巧分享', '分享一些生活小技巧，帮助大家节省开支', None, 'public', None, '北京'),
        
        # === 同城可见帖子（更多） ===
        (101, '北京交通出行', '分享北京出行经验，地铁+共享单车组合最划算', None, 'same_city', bid(101, '交通', 1)[0] if bid(101, '交通', 1) else None, '北京'),
        (101, '北京美食地图', '整理了一份北京美食地图，同城的朋友可以参考', None, 'same_city', None, '北京'),
        (104, '上海本地推荐', '上海本地人推荐的好去处，仅同城可见哦', None, 'same_city', None, '上海'),
        (104, '上海地铁攻略', '上海地铁出行省钱攻略，同城必看', None, 'same_city', None, '上海'),
        (102, '上海购物中心', '推荐几个上海性价比高的购物中心', None, 'same_city', None, '上海'),
        (103, '苏州生活指南', '苏州新人生活指南，衣食住行全攻略', None, 'same_city', None, '苏州'),
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


def ensure_indexes(conn):
    cur = conn.cursor()
    # bills 常用查询索引
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_bills_user_time ON bills(user_id, consume_time)")
    except:
        pass
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_bills_category ON bills(category)")
    except:
        pass
    # groups 与 members 索引
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_groups_city_type ON groups(city, type)")
    except:
        pass
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_group_members_gid_uid ON group_members(group_id, user_id)")
    except:
        pass
    # community_posts 常用筛选
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_posts_group ON community_posts(group_id)")
    except:
        pass
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_posts_visibility ON community_posts(visibility)")
    except:
        pass
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_posts_city ON community_posts(location_city)")
    except:
        pass
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS ix_posts_created ON community_posts(created_at)")
    except:
        pass
    conn.commit()


def ensure_truth_labels(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eval_truth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            label_type TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # 基于 user 104 的月度聚合，取均值+2σ以上的月份作为异常
    c2 = conn.cursor()
    c2.execute("SELECT consume_time, amount FROM bills WHERE user_id=104")
    monthly = {}
    for ts, amt in c2.fetchall():
        m = (ts or '')[:7]
        if not m:
            continue
        monthly[m] = monthly.get(m, 0.0) + float(amt or 0)
    vals = list(monthly.values())
    if vals:
        mean = sum(vals)/len(vals)
        var = sum((v-mean)**2 for v in vals)/len(vals)
        std = var ** 0.5
        thr = mean + 2*std
        anomalies = [k for k,v in monthly.items() if v > thr]
        cur.execute("DELETE FROM eval_truth WHERE user_id=104 AND label_type='monthly_anomaly'")
        if anomalies:
            cur.execute("INSERT INTO eval_truth(user_id, label_type, value) VALUES(?,?,?)", (104, 'monthly_anomaly', ','.join(sorted(anomalies))))
    conn.commit()


def main():
    os.makedirs(Path(DB_PATH).parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_users(conn)
    ensure_groups(conn)
    join_members(conn)
    ensure_bills(conn)
    ensure_posts(conn)
    ensure_indexes(conn)
    ensure_truth_labels(conn)
    conn.close()
    print('Demo data seeded.')


if __name__ == '__main__':
    main()
