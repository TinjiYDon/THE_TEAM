"""
SQLite 迁移：添加索引与唯一约束（不重建表的安全版本）
- 为高频查询字段创建索引
- 为 PostLike 与 UserBudget 添加唯一约束（通过唯一索引实现）
- 去重策略：PostLike 保留最早一条记录

注意：外键约束需要重建表才能彻底生效，后续可增加“重建表版”迁移。
"""
import shutil
import sqlite3
from pathlib import Path

DB_FILE = Path("data/bill_db.sqlite")

def backup_db() -> Path:
    backup_dir = DB_FILE.parent
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"bill_db_backup_indexes_{Path(DB_FILE).stat().st_mtime_ns}.sqlite"
    shutil.copy2(DB_FILE, backup_path)
    return backup_path

def ensure_pragmas(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("PRAGMA journal_mode=WAL")
    cur.close()

def create_indexes(conn):
    cur = conn.cursor()
    stmts = [
        # bills
        "CREATE INDEX IF NOT EXISTS ix_bills_user_time ON bills(user_id, consume_time)",
        "CREATE INDEX IF NOT EXISTS ix_bills_category ON bills(category)",
        "CREATE INDEX IF NOT EXISTS ix_bills_merchant ON bills(merchant)",
        "CREATE INDEX IF NOT EXISTS ix_bills_payment_method ON bills(payment_method)",
        # community_posts
        "CREATE INDEX IF NOT EXISTS ix_posts_created_at ON community_posts(created_at)",
    ]
    for s in stmts:
        cur.execute(s)
    conn.commit()
    cur.close()

def deduplicate_post_likes(conn):
    cur = conn.cursor()
    # 找出重复(post_id,user_id)并删除 id 较大的
    cur.execute(
        """
        DELETE FROM post_likes
        WHERE id IN (
          SELECT pl1.id FROM post_likes pl1
          JOIN post_likes pl2
            ON pl1.post_id = pl2.post_id
           AND pl1.user_id = pl2.user_id
           AND pl1.id > pl2.id
        )
        """
    )
    conn.commit()
    cur.close()

def create_unique_indexes(conn):
    cur = conn.cursor()
    stmts = [
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_post_likes_post_user ON post_likes(post_id, user_id)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_budget_user_category ON user_budgets(user_id, category)",
    ]
    for s in stmts:
        cur.execute(s)
    conn.commit()
    cur.close()

def main():
    if not DB_FILE.exists():
        print("[X] 数据库不存在: ", DB_FILE)
        return 1
    backup = backup_db()
    print("[OK] 已备份数据库到:", backup)
    conn = sqlite3.connect(str(DB_FILE))
    try:
        ensure_pragmas(conn)
        create_indexes(conn)
        deduplicate_post_likes(conn)
        create_unique_indexes(conn)
        print("[OK] 索引与唯一约束处理完成")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())


