DATABASE = "music.db"

def init_db():
    database = sqlite3.connect(DATABASE)
    cursor = database.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        artist TEXT,
        audio TEXT,
        cover TEXT
    )
    """)

    database.commit()
    database.close()

init_db()
