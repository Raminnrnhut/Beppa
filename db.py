import sqlite3, os, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "beppa.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn

def now_iso():
    return datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z"
