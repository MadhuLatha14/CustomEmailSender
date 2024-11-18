import sqlite3

def setup_db():
    conn = sqlite3.connect('email_data.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()
