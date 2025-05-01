
import sqlite3
import uuid
from telegram import Bot

DB_PATH = "data/bot_db.sqlite"

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_user(user_id, username, first_name):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )

def get_channels():
    with get_connection() as conn:
        return [row[0] for row in conn.execute("SELECT channel_username FROM channels")]

async def is_user_in_channels(bot: Bot, user_id: int):
    channels = get_channels()
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=f"@{channel}", user_id=user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

def save_file(file_id, file_name, uploader_id):
    short_code = str(uuid.uuid4())[:8]
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO files (telegram_file_id, file_name, uploader_id, short_code) VALUES (?, ?, ?, ?)",
            (file_id, file_name, uploader_id, short_code)
        )
    return short_code

def get_file_by_code(code):
    with get_connection() as conn:
        result = conn.execute("SELECT telegram_file_id, file_name FROM files WHERE short_code=?", (code,)).fetchone()
    return result

def get_all_files():
    with get_connection() as conn:
        return conn.execute("SELECT short_code, file_name FROM files").fetchall()

def delete_file_by_code(code):
    with get_connection() as conn:
        conn.execute("DELETE FROM files WHERE short_code=?", (code,))
