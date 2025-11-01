import sqlite3
conn = sqlite3.connect('q_ide.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(membership_tiers)")
print("Membership Tiers Columns:")
for row in cursor.fetchall():
    print(f'  {row[1]}: {row[2]}')
conn.close()
