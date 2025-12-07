"""
Insert symptoms data with proper Unicode handling
Using direct parameter binding instead of encoding tricks
"""

import pyodbc

conn_str = """
    Driver={ODBC Driver 17 for SQL Server};
    Server=DESKTOP-V9NP2C3;
    Database=QuanLyKhamBenhDB;
    Trusted_Connection=yes;
"""

try:
    conn = pyodbc.connect(conn_str)
    # Don't set encoding - let pyodbc handle it naturally
    # conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16-le')
    
    cursor = conn.cursor()
    
    # Sample symptoms with Vietnamese names and keywords
    # The key is to use proper Unicode strings and let pyodbc handle encoding
    symptoms_data = [
        # Internal Medicine (Specialty ID = 1)
        ("Sốt", "fever, high fever, sot", 1),
        ("Ho", "cough, coughing, ho", 1),
        ("Đau đầu", "headache, dau dau, head pain", 1),
        ("Huyết áp cao", "high blood pressure, huyet ap cao", 1),
        ("Khó thở", "dyspnea, shortness of breath, kho tho", 1),
        ("Chóng mặt", "vertigo, dizziness, chong mat", 1),
        
        # Surgery (Specialty ID = 2)
        ("Chấn thương", "trauma, injury, chan thuong", 2),
        ("Gãy xương", "fracture, bone break, gay xuong", 2),
        ("Chảy máu", "bleeding, hemorrhage, chay mau", 2),
        ("Viêm vết mổ", "infection, surgical site infection, viem vet mo", 2),
        ("Phù nề", "swelling, edema, phu ne", 2),
        
        # Obstetrics (Specialty ID = 3)
        ("Đau bụng kỳ kinh", "dysmenorrhea, period pain, dau bung", 3),
        ("Rong kinh", "menorrhagia, heavy bleeding, rong kinh", 3),
        ("Vô sinh", "infertility, vo sinh", 3),
        ("Khí hư bất thường", "abnormal discharge, ki hu", 3),
        
        # Pediatrics (Specialty ID = 4)
        ("Sốt cao ở trẻ", "fever in children, high fever", 4),
        ("Tiêu chảy", "diarrhea, diarrheal, tieu chay", 4),
        ("Nôn", "vomiting, nausea, non", 4),
        ("Viêm đường hô hấp", "respiratory infection, respiratory, viem", 4),
        
        # Dermatology (Specialty ID = 5)
        ("Mụn", "acne, pimple, mun", 5),
        ("Viêm da", "dermatitis, inflammation, viem da", 5),
        ("Khô da", "dry skin, dryness, kho da", 5),
        ("Nám da", "melasma, dark spots, nam da", 5),
        ("Lang ben", "tinea versicolor, fungal, lang ben", 5),
        
        # Dentistry-Maxillofacial (Specialty ID = 6)
        ("Đau răng", "toothache, tooth pain, dau rang", 6),
        ("Viêm nướu", "gingivitis, gum inflammation, viem nuou", 6),
        ("Cao răng", "tartar, plaque, cao rang", 6),
        ("Hôi miệng", "bad breath, halitosis, hoi mieng", 6),
        
        # ENT (Specialty ID = 7)
        ("Viêm họng", "sore throat, pharyngitis, viem hong", 7),
        ("Viêm amidan", "tonsillitis, tonsil infection, viem amidan", 7),
        ("Viêm xoang", "sinusitis, sinus infection, viem xoang", 7),
        ("Ù tai", "hearing loss, deafness, u tai", 7),
        ("Sổi mũi", "rhinitis, runny nose, soi mui", 7),
    ]
    
    print(f"[*] Inserting {len(symptoms_data)} symptoms...")
    
    for name, keywords, specialty_id in symptoms_data:
        try:
            query = """
            INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active)
            VALUES (?, ?, ?, 1)
            """
            cursor.execute(query, (name, keywords, specialty_id))
        except Exception as e:
            print(f"❌ Error inserting '{name}': {e}")
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM SYMPTOMS")
    count = cursor.fetchone()[0]
    print(f"[OK] Inserted {count} symptoms!")
    
    # Show sample
    print("\n[Sample data]:")
    cursor.execute("SELECT TOP 5 name FROM SYMPTOMS")
    for row in cursor:
        print(f"  - {row[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
