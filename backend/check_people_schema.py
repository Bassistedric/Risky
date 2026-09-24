import sqlite3

connection = sqlite3.connect("database/risky.db")

columns = connection.execute(
    "PRAGMA table_info(people)"
).fetchall()

print("Colonnes de la table people :")

for column in columns:
    print("-", column[1])

connection.close()