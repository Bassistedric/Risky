import sqlite3

db = sqlite3.connect("database/risky.db")

row = db.execute(
    """
    SELECT
        id,
        action,
        entity_type,
        entity_id,
        before_data,
        after_data,
        details
    FROM audit_logs
    WHERE entity_type = ?
    ORDER BY id DESC
    LIMIT 1
    """,
    ("EVENT_CLASSIFICATION",),
).fetchone()

db.close()

if row is None:
    print("Aucun audit EVENT_CLASSIFICATION trouvé.")
else:
    print("ID :", row[0])
    print("ACTION :", row[1])
    print("ENTITY_TYPE :", row[2])
    print("ENTITY_ID :", row[3])
    print("BEFORE :", row[4])
    print("AFTER :", row[5])
    print("DETAILS :", row[6])