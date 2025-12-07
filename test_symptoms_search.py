import pyodbc

conn = pyodbc.connect('''
    Driver={ODBC Driver 17 for SQL Server};
    Server=DESKTOP-V9NP2C3;
    Database=QuanLyKhamBenhDB;
    Trusted_Connection=yes;
''')
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16-le')
conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')

cursor = conn.cursor()
print("Sample symptoms in database:")
cursor.execute('SELECT TOP 5 symptom_id, name FROM SYMPTOMS')
for row in cursor:
    try:
        name_safe = row[1].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    except:
        name_safe = "[ERROR]"
    print(f"ID: {row[0]}, Name: '{name_safe}'")

print("\n\nSearching for 'Sốt' (fever):")
cursor.execute("SELECT symptom_id, name FROM SYMPTOMS WHERE name LIKE ?", ('%Sốt%',))
results = cursor.fetchall()
print(f"Found {len(results)} results")
for row in results:
    try:
        name_safe = row[1].encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    except:
        name_safe = "[ERROR]"
    print(f"  - ID: {row[0]}, Name: '{name_safe}'")

print("\nSearching for 'Ho' (cough):")
cursor.execute("SELECT symptom_id, name FROM SYMPTOMS WHERE name LIKE ?", ('%Ho%',))
results = cursor.fetchall()
print(f"Found {len(results)} results")

print("\nSearching for 'đau' (pain):")
cursor.execute("SELECT symptom_id, name FROM SYMPTOMS WHERE name LIKE ?", ('%đau%',))
results = cursor.fetchall()
print(f"Found {len(results)} results")

cursor.close()
conn.close()
