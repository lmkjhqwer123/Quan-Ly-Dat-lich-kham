"""
Thêm dữ liệu mẫu vào bảng SYMPTOMS
"""

import pyodbc
from config import MSSQL_SERVER, MSSQL_DATABASE, MSSQL_DRIVER

# Kết nối database
conn_str = f"""
    Driver={{{MSSQL_DRIVER}}};
    Server={MSSQL_SERVER};
    Database={MSSQL_DATABASE};
    Trusted_Connection=yes;
"""

try:
    conn = pyodbc.connect(conn_str)
    # For SQL Server NVARCHAR, use UTF-16LE encoding which SQL Server uses internally
    conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16-le')
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    conn.setencoding(encoding='utf-8')
    
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ
    print("[*] Deleting old data...")
    cursor.execute("DELETE FROM SYMPTOMS")
    conn.commit()
    
    # Dữ liệu mẫu
    symptoms_data = [
        # Khoa Nội tổng hợp (Specialty ID = 1)
        ("Sốt", "sốt, sốt cao, sốt kéo dài, fever, cảm cúm", 1),
        ("Ho", "ho, cough, ho có đờm, ho khan, ho lâu ngày", 1),
        ("Đau đầu", "đau đầu, migraine, đau nửa đầu, nhức đầu", 1),
        ("Huyết áp cao", "huyết áp cao, cao máu, blood pressure, huyết áp", 1),
        ("Khó thở", "khó thở, dyspnea, hụt hơi, đoạn hơi", 1),
        ("Chóng mặt", "chóng mặt, buồn nôn, mất thăng bằng, vertigo", 1),
        
        # Khoa Ngoại tổng quát (Specialty ID = 2)
        ("Chấn thương", "chấn thương, injury, va chạm, bị thương", 2),
        ("Gãy xương", "gãy xương, fracture, xương gãy, vỡ xương", 2),
        ("Chảy máu", "chảy máu, bleeding, máu chảy, hemorrhage", 2),
        ("Viêm vết mổ", "viêm vết mổ, infection, vết mổ bị nhiễm", 2),
        ("Phù nề", "phù nề, swelling, sưng phù, tích nước", 2),
        
        # Khoa Sản (Specialty ID = 3)
        ("Đau bụng kỳ kinh", "đau bụng kỳ kinh, dysmenorrhea, đau kinh nguyệt", 3),
        ("Rong kinh", "rong kinh, menorrhagia, chảy máu bất thường", 3),
        ("Vô sinh", "vô sinh, infertility, không có con", 3),
        ("Khí hư bất thường", "khí hư bất thường, abnormal discharge, viêm phụ khoa", 3),
        
        # Khoa Nhi (Specialty ID = 4)
        ("Sốt cao ở trẻ", "sốt cao ở trẻ, fever in children, cháy sốt", 4),
        ("Tiêu chảy", "tiêu chảy, diarrhea, phân lỏng, rối loạn tiêu hóa", 4),
        ("Nôn", "nôn, vomiting, buồn nôn, trớ sữa", 4),
        ("Viêm đường hô hấp", "viêm đường hô hấp, respiratory infection, cảm lạnh", 4),
        
        # Khoa Da liễu (Specialty ID = 5)
        ("Mụn", "mụn, acne, mụn trứng cá, mụn viêm", 5),
        ("Viêm da", "viêm da, dermatitis, viêm da dị ứng, eczema", 5),
        ("Khô da", "khô da, dry skin, da khô, chứng khô", 5),
        ("Nám da", "nám da, melasma, tàn nhang, lão hóa da", 5),
        ("Lang ben", "lang ben, tinea versicolor, bệnh nấm", 5),
        
        # Răng-Hàm-Mặt (Specialty ID = 6)
        ("Đau răng", "đau răng, toothache, sâu răng, viêm nướu", 6),
        ("Viêm nướu", "viêm nướu, gingivitis, chảy máu chân răng", 6),
        ("Cao răng", "cao răng, tartar, mảng bám, vôi răng", 6),
        ("Hôi miệng", "hôi miệng, bad breath, mùi từ miệng", 6),
        
        # Tai-Mũi-Họng (Specialty ID = 7)
        ("Viêm họng", "viêm họng, đau họng, throat pain, sore throat", 7),
        ("Viêm amidan", "viêm amidan, tonsillitis, amidan sưng to", 7),
        ("Viêm xoang", "viêm xoang, sinusitis, xoang sưng, chứng xoang", 7),
        ("Ù tai", "ù tai, hearing loss, nặng tai, điếc một tai", 7),
        ("Sổi mũi", "sổi mũi, rhinitis, cảm lạnh, chảy nước mũi", 7),
    ]
    
    # Insert dữ liệu
    print("[*] Inserting symptoms data...")
    insert_query = """
    INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active, created_at)
    VALUES (?, ?, ?, 1, GETDATE())
    """
    
    for name, keywords, specialty_id in symptoms_data:
        cursor.execute(insert_query, (name, keywords, specialty_id))
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) as total FROM SYMPTOMS")
    total = cursor.fetchone()[0]
    
    print(f"\n[OK] Inserted {total} symptoms!")
    
    # Display sample
    cursor.execute("SELECT TOP 5 name, specialty_id FROM SYMPTOMS ORDER BY specialty_id")
    print("\n[Sample data]:")
    for row in cursor.fetchall():
        print(f"  - {row[0]} (Specialty ID: {row[1]})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
