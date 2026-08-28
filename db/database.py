import sqlite3
import config
from datetime import datetime

class Database:
    def __init__(self, db_path="bot_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                author_id INTEGER,
                author_name TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                author_id INTEGER,
                fact TEXT,
                PRIMARY KEY (author_id, fact)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_channels (
                channel_id INTEGER PRIMARY KEY,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                author_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 1,
                last_warning DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                arguments TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_message(self, guild_id, channel_id, author_id, author_name, content):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (guild_id, channel_id, author_id, author_name, content) VALUES (?, ?, ?, ?, ?)",
            (guild_id, channel_id, author_id, author_name, content)
        )
        cursor.execute(
            "INSERT OR REPLACE INTO active_channels (channel_id, last_activity) VALUES (?, CURRENT_TIMESTAMP)",
            (channel_id,)
        )
        self.conn.commit()

    def get_recent_channel_messages(self, channel_id, limit=50):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT author_name, content FROM messages WHERE channel_id=? ORDER BY id DESC LIMIT ?",
            (channel_id, limit)
        )
        rows = cursor.fetchall()
        rows.reverse()
        return rows

    def add_user_fact(self, author_id, fact):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO user_facts (author_id, fact) VALUES (?, ?)",
            (author_id, fact)
        )
        self.conn.commit()

    def get_user_facts(self, author_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT fact FROM user_facts WHERE author_id=?", (author_id,))
        rows = cursor.fetchall()
        return [r[0] for r in rows]

    def cleanup_old_messages(self, ttl_seconds=900):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM messages WHERE timestamp < datetime('now', '-' || ? || ' seconds')",
            (ttl_seconds,)
        )
        self.conn.commit()

    def get_most_active_channels(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT channel_id FROM active_channels ORDER BY last_activity DESC LIMIT ?",
            (limit,)
        )
        return [row[0] for row in cursor.fetchall()]

    def add_warning(self, author_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO warnings (author_id, count, last_warning) VALUES (?, 1, CURRENT_TIMESTAMP) "
            "ON CONFLICT(author_id) DO UPDATE SET count = count + 1, last_warning = CURRENT_TIMESTAMP",
            (author_id,)
        )
        self.conn.commit()

    def get_warnings(self, author_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT count, last_warning FROM warnings WHERE author_id=?", (author_id,))
        row = cursor.fetchone()
        if row:
            return {"count": row[0], "last_warning": row[1]}
        return {"count": 0, "last_warning": None}

    def reset_warnings(self, author_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM warnings WHERE author_id=?", (author_id,))
        self.conn.commit()

    def is_muted(self, author_id):
        warnings = self.get_warnings(author_id)
        if warnings["count"] >= config.MAX_WARNINGS:
            last = warnings["last_warning"]
            if last:
                last_dt = datetime.fromisoformat(last)
                if (datetime.now() - last_dt).seconds < config.MUTE_MINUTES * 60:
                    return True
                else:
                    self.reset_warnings(author_id)
        return False

    def add_command_history(self, command, arguments, result):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO command_history (command, arguments, result) VALUES (?, ?, ?)",
            (command, arguments, result)
        )
        self.conn.commit()

db = Database()