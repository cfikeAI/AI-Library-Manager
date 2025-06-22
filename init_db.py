import os
import sqlite3

# init_db.py

import sqlite3
import os

DB_PATH = "library.db"

if os.path.exists(DB_PATH):
    print("'library.db' already exists. Delete it if you want to recreate.")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Core table your app expects
cursor.execute("""
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    year INTEGER,
    description TEXT,
    genre TEXT,
    rating REAL,
    date_added TEXT
)
""")

# You can add other tables if your app uses them

conn.commit()
conn.close()

print("Created empty library.db with schema.")
