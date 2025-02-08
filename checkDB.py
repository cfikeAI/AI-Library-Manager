import sqlite3

# Connect to the database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Check if the books table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)

# If the books table exists, show some data
if ('books',) in tables:
    cursor.execute("SELECT * FROM books LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
else:
    print("No 'books' table found!")

conn.close()