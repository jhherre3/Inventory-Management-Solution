import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# === Attempt to add 'image' column to 'tools' table ===
try:
    cursor.execute("ALTER TABLE tools ADD COLUMN image TEXT")
    print("✅ 'image' column added to tools table.")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("ℹ️ Column 'image' already exists.")
    else:
        raise  # Re-raise any other unexpected errors

conn.commit()
conn.close()
