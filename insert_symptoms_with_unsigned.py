"""
Insert symptoms data with Vietnamese unsign (không dấu) + English support
Hỗ trợ tìm kiếm bằng:
1. Tiếng Việt có dấu (Sốt, đau đầu)
2. Tiếng Việt không dấu (Sot, dau dau)
3. Tiếng Anh (fever, headache)
"""

import pyodbc
import unicodedata
import re

conn_str = """
    Driver={ODBC Driver 17 for SQL Server};
    Server=DESKTOP-V9NP2C3;
    Database=QuanLyKhamBenhDB;
    Trusted_Connection=yes;
"""

def remove_vietnamese_accents(text):
    """
    Convert Vietnamese with accents to without accents (không dấu)
    Examples:
    - "Sốt" → "Sot"
    - "đau đầu" → "dau dau"
    - "chóng mặt" → "chong mat"
    """
    if not text:
        return text
    
    # Normalize to NFD (decompose characters)
    nfd = unicodedata.normalize('NFD', text)
    
    # Remove combining marks (accents)
    result = []
    for char in nfd:
        if unicodedata.category(char) != 'Mn':  # Mn = Mark, nonspacing
            result.append(char)
    
    return ''.join(result)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Sample symptoms with Vietnamese names and keywords
    symptoms_data = [
        # Internal Medicine (Specialty ID = 1)
        ("Sốt", "fever, high fever, sot, sot cao, sot keo dai", 1),
        ("Ho", "cough, coughing, ho, ho khan, ho co dam", 1),
        ("Đau đầu", "headache, dau dau, head pain, dau nua dau, nhuc dau", 1),
        ("Huyết áp cao", "high blood pressure, huyet ap cao, cao mau, blood pressure", 1),
        ("Khó thở", "dyspnea, shortness of breath, kho tho, hut hoi, doan hoi", 1),
        ("Chóng mặt", "vertigo, dizziness, chong mat, buon non, mat thang bang", 1),
        ("Tức ngực", "chest pain, tuc nguc, dau long nguc", 1),
        ("Đau lưng", "back pain, dau lung, dau vung that lung", 1),
        ("Đau bụng", "abdominal pain, dau bung, dau vung bung", 1),
        
        # Surgery (Specialty ID = 2)
        ("Chấn thương", "trauma, injury, chan thuong, va cham, bi thuong", 2),
        ("Gãy xương", "fracture, bone break, gay xuong, xuong gay, vo xuong", 2),
        ("Chảy máu", "bleeding, hemorrhage, chay mau, mau chay", 2),
        ("Viêm vết mổ", "infection, surgical site infection, viem vet mo", 2),
        ("Phù nề", "swelling, edema, phu ne, sung phu, tich nuoc", 2),
        
        # Obstetrics (Specialty ID = 3)
        ("Đau bụng kỳ kinh", "dysmenorrhea, period pain, dau bung ky kinh", 3),
        ("Rong kinh", "menorrhagia, heavy bleeding, rong kinh, chay mau bat thuong", 3),
        ("Vô sinh", "infertility, vo sinh, khong co con", 3),
        ("Khí hư bất thường", "abnormal discharge, ki hu bat thuong, viem phu khoa", 3),
        
        # Pediatrics (Specialty ID = 4)
        ("Sốt cao ở trẻ", "fever in children, high fever, sot cao o tre, chay sot", 4),
        ("Tiêu chảy", "diarrhea, diarrheal, tieu chay, phan long, roi loan tieu hoa", 4),
        ("Nôn", "vomiting, nausea, non, buon non, tro sua", 4),
        ("Viêm đường hô hấp", "respiratory infection, respiratory, viem duong ho hap", 4),
        
        # Dermatology (Specialty ID = 5)
        ("Mụn", "acne, pimple, mun, mun trung ca, mun viem", 5),
        ("Viêm da", "dermatitis, inflammation, viem da, viem da di ung, eczema", 5),
        ("Khô da", "dry skin, dryness, kho da, da kho, chung kho", 5),
        ("Nám da", "melasma, dark spots, nam da, tan nhang, lao hoa da", 5),
        ("Lang ben", "tinea versicolor, fungal, lang ben, benh nam", 5),
        
        # Dentistry-Maxillofacial (Specialty ID = 6)
        ("Đau răng", "toothache, tooth pain, dau rang, sau rang, viem nuou", 6),
        ("Viêm nướu", "gingivitis, gum inflammation, viem nuou, chay mau chan rang", 6),
        ("Cao răng", "tartar, plaque, cao rang, manh bam, voi rang", 6),
        ("Hôi miệng", "bad breath, halitosis, hoi mieng, mui tu mieng", 6),
        
        # ENT (Specialty ID = 7)
        ("Viêm họng", "sore throat, pharyngitis, viem hong, dau hong, throat pain", 7),
        ("Viêm amidan", "tonsillitis, tonsil infection, viem amidan, amidan sung to", 7),
        ("Viêm xoang", "sinusitis, sinus infection, viem xoang, xoang sung, chung xoang", 7),
        ("Ù tai", "hearing loss, deafness, u tai, nang tai, diec mot tai", 7),
        ("Sổi mũi", "rhinitis, runny nose, soi mui, cam lanh, chay nuoc mui", 7),
    ]
    
    print(f"[*] Deleting old data...")
    cursor.execute("DELETE FROM SYMPTOMS")
    conn.commit()
    
    print(f"[*] Inserting {len(symptoms_data)} symptoms with Vietnamese (no accent) + English support...")
    
    inserted_count = 0
    for name, keywords, specialty_id in symptoms_data:
        try:
            # Generate Vietnamese không dấu version
            name_unsigned = remove_vietnamese_accents(name)
            
            # Combine keywords: Vietnamese dấu, Vietnamese không dấu, English
            # Format: "vietnamese_signed, vietnamese_unsigned, english1, english2, ..."
            enhanced_keywords = f"{name}, {name_unsigned}, {keywords}"
            
            query = """
            INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active)
            VALUES (?, ?, ?, 1)
            """
            cursor.execute(query, (name, enhanced_keywords, specialty_id))
            inserted_count += 1
            
        except Exception as e:
            print(f"❌ Error inserting '{name}': {e}")
    
    conn.commit()
    
    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM SYMPTOMS")
    count = cursor.fetchone()[0]
    print(f"[OK] Inserted {count} symptoms successfully!")
    
    # Show sample with keywords
    print("\n[Sample data with keywords]:")
    cursor.execute("SELECT TOP 5 name, keywords FROM SYMPTOMS")
    for row in cursor:
        print(f"  Name: {row[0]}")
        print(f"  Keywords: {row[1]}")
        print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
