import sqlite3
import os

def init_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "voting.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # جدول الأصوات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        voter_id TEXT,
        vote TEXT
    )
    """)

    # جدول لمنع التكرار
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voted (
        voter_id TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()

def has_voted(voter_id):
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "voting.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM voted WHERE voter_id=?", (voter_id,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def save_vote(voter_id, vote):
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "voting.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO votes VALUES (?, ?)", (voter_id, vote))
    cursor.execute("INSERT INTO voted VALUES (?)", (voter_id,))

    conn.commit()
    conn.close()

def get_results():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "voting.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT vote, COUNT(*) FROM votes GROUP BY vote")
    results = cursor.fetchall()

    conn.close()
    return results