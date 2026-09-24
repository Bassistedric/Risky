import sqlite3

db = sqlite3.connect("./database/risky.db")

rows = db.execute(
    """
    SELECT code, label
    FROM event_code_references
    WHERE category = 'INJURY_NATURE'
    ORDER BY code
    """
).fetchall()

for code, label in rows:
    if code.isdigit() and 60 <= int(code) <= 69:
        print(code, "-", label)

db.close()