# shared/database.py
import psycopg2
from config import DATABASE_URL

def initialize_db():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            is_premium INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id SERIAL PRIMARY KEY,
            author_id INTEGER,
            name TEXT,
            description TEXT,
            premium_only INTEGER DEFAULT 0,
            file_path TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS photo_uploads (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            last_upload_ts INTEGER
        )
        """)
        
        cursor.execute("""
        INSERT INTO admin_accounts (username, password)
        VALUES ('admin', 'pass123')
        ON CONFLICT (username) DO NOTHING
        """)

        conn.commit()
        conn.close()
        print("[+] База данных создана.")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()
