import sqlite3
from datetime import datetime, timezone

DB_FILE = "timecapsule.db"

def init_db():
    """Create the capsules table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS capsules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            reveal_at TEXT NOT NULL,
            revealed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_capsule(user_id, username, channel_id, message, reveal_at):
    """Store a new time capsule."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO capsules (user_id, username, channel_id, message, created_at, reveal_at, revealed)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (user_id, username, channel_id, message, datetime.now(timezone.utc).isoformat(), reveal_at.isoformat()))
    capsule_id = c.lastrowid
    conn.commit()
    conn.close()
    return capsule_id

def get_due_capsules():
    """Return all capsules that are due to be revealed."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, user_id, username, channel_id, message, created_at, reveal_at
        FROM capsules
        WHERE revealed = 0 AND reveal_at <= ?
    """, (datetime.now(timezone.utc).isoformat(),))
    rows = c.fetchall()
    conn.close()
    return rows

def mark_revealed(capsule_id):
    """Mark a capsule as revealed so it doesn't fire again."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE capsules SET revealed = 1 WHERE id = ?", (capsule_id,))
    conn.commit()
    conn.close()

def get_user_capsules(user_id):
    """Return all pending capsules for a specific user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, message, created_at, reveal_at
        FROM capsules
        WHERE user_id = ? AND revealed = 0
        ORDER BY reveal_at ASC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_capsule(capsule_id, user_id):
    """Delete a capsule — only if it belongs to the requesting user."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM capsules WHERE id = ? AND user_id = ? AND revealed = 0",
              (capsule_id, user_id))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted > 0