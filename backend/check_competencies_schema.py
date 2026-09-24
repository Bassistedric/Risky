import sqlite3

connection = sqlite3.connect("database/risky.db")

columns = connection.execute(
    "PRAGMA table_info(competencies)"
).fetchall()

print("Colonnes de la table competencies :")

for column in columns:
    print("-", column[1])

connection.close()