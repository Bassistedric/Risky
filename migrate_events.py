import sqlite3

DB_PATH = "database/risky.db"

columns = [
    ("person_category", "TEXT"),
    ("victim_last_name", "TEXT"),
    ("victim_first_name", "TEXT"),
    ("project_manager", "TEXT"),
    ("site_supervisor", "TEXT"),
    ("material_damage", "BOOLEAN NOT NULL DEFAULT 0"),
    ("material_damage_details", "TEXT"),
    ("material_damage_cost", "REAL"),
    ("environmental_damage", "BOOLEAN NOT NULL DEFAULT 0"),
    ("environmental_damage_type", "TEXT"),
    ("environmental_damage_details", "TEXT"),
    ("environmental_quantity", "REAL"),
    ("environmental_unit", "TEXT"),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

existing_columns = {
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(events)"
    )
}

for name, sql_type in columns:
    if name in existing_columns:
        print(f"Déjà présente : {name}")
    else:
        cursor.execute(
            f"ALTER TABLE events "
            f"ADD COLUMN {name} {sql_type}"
        )
        print(f"Ajout : {name}")

conn.commit()
conn.close()

print("Migration terminée.")