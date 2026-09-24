import sqlite3

connection = sqlite3.connect("database/risky.db")

cursor = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

print("Tables présentes dans RISKY :")
for table in tables:
    print("-", table[0])

connection.close()