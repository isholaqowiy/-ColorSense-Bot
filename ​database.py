import aiosqlite

DB_NAME = "colorsense.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Settings structure mapping table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                palette_size INTEGER DEFAULT 5,
                sort_by TEXT DEFAULT 'Dominant'
            )
        ''')
        # Favorites logging metrics record mapping table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                palette_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def get_settings(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT palette_size, sort_by FROM settings WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"palette_size": row[0], "sort_by": row[1]}
            await db.execute("INSERT INTO settings (user_id) VALUES (?)", (user_id,))
            await db.commit()
            return {"palette_size": 5, "sort_by": "Dominant"}

async def update_setting(user_id: int, column: str, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f"UPDATE settings SET {column} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

