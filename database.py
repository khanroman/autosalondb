#database
import sqlite3
from config import DB_NAME

def get_table_columns(table_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cur.fetchall()]
    conn.close()
    return columns

def load_table_data(table_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    conn.close()
    return rows

def execute_query(query, params=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    conn.commit()
    conn.close()

def fetch_one(query, params=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    result = cur.fetchone()
    conn.close()
    return result

def fetch_all(query, params=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result