"""Check the CHECK constraint for sender_type"""
import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=DESKTOP-V9NP2C3;Database=QuanLyKhamBenhDB;Trusted_Connection=yes;')
cursor = conn.cursor()

# Get the constraint definition
cursor.execute("""
SELECT cc.CHECK_CLAUSE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.CHECK_CONSTRAINTS cc 
    ON tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
WHERE tc.TABLE_NAME = 'CHAT_MESSAGES' 
AND tc.CONSTRAINT_TYPE = 'CHECK'
""")

print("=== CHECK CONSTRAINTS on CHAT_MESSAGES ===")
for row in cursor.fetchall():
    print(row[0])

# Also check what values are currently in the table
cursor.execute("SELECT DISTINCT sender_type FROM CHAT_MESSAGES")
print("\n=== DISTINCT sender_type VALUES ===")
for row in cursor.fetchall():
    print(f"  '{row[0]}'")

cursor.close()
conn.close()
