"""Check the actual columns in CHAT_CONVERSATIONS and CHAT_MESSAGES tables"""
import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-V9NP2C3;Database=QuanLyKhamBenhDB;Trusted_Connection=yes;')
cursor = conn.cursor()

print("\n=== CHAT_CONVERSATIONS COLUMNS ===")
cursor.execute("""
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME='CHAT_CONVERSATIONS' 
ORDER BY ORDINAL_POSITION
""")
for row in cursor.fetchall():
    print(f"{row[0]:30} {row[1]}")

print("\n=== CHAT_MESSAGES COLUMNS ===")
cursor.execute("""
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME='CHAT_MESSAGES' 
ORDER BY ORDINAL_POSITION
""")
for row in cursor.fetchall():
    print(f"{row[0]:30} {row[1]}")

cursor.close()
conn.close()
