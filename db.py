import aiosqlite
import datetime
import logging

DB_NAME = "bot.db"
logger = logging.getLogger(__name__)

async def init_db():
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    joined_at TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER,
                    sender_id INTEGER,
                    message_type TEXT,
                    file_id TEXT,
                    caption TEXT,
                    created_at TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('bot_status', 'active')")
            await db.commit()
    except Exception as e:
        logger.error(f"Database init error: {e}")

async def add_user(user_id: int, full_name: str, username: str):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("""
                INSERT INTO users (user_id, full_name, username, joined_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    username = excluded.username
            """, (user_id, full_name, username, now))
            await db.commit()
    except Exception as e:
        logger.error(f"Error adding user {user_id}: {e}")

async def get_user_open_tickets_count(user_id: int) -> int:
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT COUNT(*) FROM tickets WHERE user_id = ? AND status = 'Open'", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    except Exception as e:
        logger.error(f"Error getting open tickets count for {user_id}: {e}")
        return 0

async def create_ticket(user_id: int, title: str) -> int:
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = await db.execute("""
                INSERT INTO tickets (user_id, title, status, created_at)
                VALUES (?, ?, 'Open', ?)
            """, (user_id, title, now))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating ticket for {user_id}: {e}")
        raise

async def add_message(ticket_id: int, sender_id: int, message_type: str, file_id: str, caption: str):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("""
                INSERT INTO messages (ticket_id, sender_id, message_type, file_id, caption, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ticket_id, sender_id, message_type, file_id, caption, now))
            await db.commit()
    except Exception as e:
        logger.error(f"Error adding message to ticket {ticket_id}: {e}")

async def get_ticket(ticket_id: int):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)) as cursor:
                return await cursor.fetchone()
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        return None

async def get_ticket_messages(ticket_id: int):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM messages WHERE ticket_id = ? ORDER BY id ASC", (ticket_id,)) as cursor:
                return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting messages for ticket {ticket_id}: {e}")
        return []

async def update_ticket_status(ticket_id: int, status: str):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("UPDATE tickets SET status = ? WHERE ticket_id = ?", (status, ticket_id))
            await db.commit()
    except Exception as e:
        logger.error(f"Error updating ticket status {ticket_id}: {e}")

async def get_all_tickets(status: str = None, limit: int = 5, offset: int = 0):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            if status:
                async with db.execute("SELECT * FROM tickets WHERE status = ? ORDER BY ticket_id DESC LIMIT ? OFFSET ?", (status, limit, offset)) as cursor:
                    return await cursor.fetchall()
            else:
                async with db.execute("SELECT * FROM tickets ORDER BY ticket_id DESC LIMIT ? OFFSET ?", (limit, offset)) as cursor:
                    return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting all tickets: {e}")
        return []

async def count_tickets(status: str = None) -> int:
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            if status:
                async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = ?", (status,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
            else:
                async with db.execute("SELECT COUNT(*) FROM tickets") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
    except Exception as e:
        logger.error(f"Error counting tickets: {e}")
        return 0

async def get_user_tickets(user_id: int):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY ticket_id DESC", (user_id,)) as cursor:
                return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting user tickets for {user_id}: {e}")
        return []

async def get_bot_status() -> str:
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT value FROM settings WHERE key = 'bot_status'") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 'active'
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return 'active'

async def set_bot_status(status: str):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('bot_status', ?)", (status,))
            await db.commit()
    except Exception as e:
        logger.error(f"Error setting bot status: {e}")

async def get_stats():
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                users_count = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Open'") as c:
                open_tickets = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Closed'") as c:
                closed_tickets = (await c.fetchone())[0]
            async with db.execute("SELECT COUNT(*) FROM messages") as c:
                messages_count = (await c.fetchone())[0]
            return users_count, open_tickets, closed_tickets, messages_count
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return 0, 0, 0, 0