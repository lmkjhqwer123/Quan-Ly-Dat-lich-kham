"""
Database Access Layer for Chatbot
Kết nối SQL Server và các hàm query dữ liệu
"""

import pyodbc
import json
from typing import List, Dict, Any, Optional
from config import MSSQL_SERVER, MSSQL_DATABASE, MSSQL_DRIVER

# ============================================
# DATABASE CONNECTION
# ============================================

def get_db_connection():
    """
    Tạo kết nối đến SQL Server
    
    Returns:
        pyodbc.Connection
    """
    try:
        # SQL Server NVARCHAR is stored as UTF-16LE in the database
        # Using UTF-16LE for WCHAR encoding should work better
        connection_string = f"""
            Driver={{{MSSQL_DRIVER}}};
            Server={MSSQL_SERVER};
            Database={MSSQL_DATABASE};
            Trusted_Connection=yes;
        """
        
        conn = pyodbc.connect(connection_string)
        
        # Set decoding for reading text from SQL Server
        # SQL Server NVARCHAR uses UTF-16LE
        try:
            conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16-le')
            conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            # DON'T set encoding - it breaks parameter binding
            # conn.setencoding(encoding='utf-8')
        except Exception as enc_err:
            pass  # Continue with defaults
        
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise

# ============================================
# FUNCTION 1: TÌM CHUYÊN KHOA TỪ TRIỆU CHỨNG
# ============================================

def get_specialty_for_symptoms(symptoms_text: str) -> Dict[str, Any]:
    """
    Tìm chuyên khoa phù hợp dựa trên triệu chứng
    
    Args:
        symptoms_text: Mô tả triệu chứng (VD: "đau đầu, chóng mặt")
    
    Returns:
        Dict với:
        - specialty_id: ID chuyên khoa
        - specialty_name: Tên chuyên khoa
        - description: Mô tả
        - doctors_count: Số bác sĩ
        - matched_symptoms: Triệu chứng tìm thấy
    """
    try:
        # Xử lý encoding input
        if not symptoms_text or not isinstance(symptoms_text, str):
            return {
                "success": False,
                "message": "Triệu chứng không hợp lệ",
                "specialty_id": None,
                "specialty_name": None
            }
        
        # Normalize input encoding (handle Vietnamese chars)
        try:
            symptoms_text = symptoms_text.encode('utf-8').decode('utf-8')
        except:
            symptoms_text = symptoms_text  # Keep original if encoding fails
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tìm triệu chứng khớp
        query_symptoms = """
        SELECT DISTINCT s.symptom_id, s.name, s.specialty_id
        FROM SYMPTOMS s
        WHERE s.is_active = 1
        AND (s.name LIKE ? OR s.keywords LIKE ?)
        ORDER BY s.specialty_id
        """
        
        # Use a simple search term that's safer to encode
        search_term = f"%{symptoms_text}%"
        try:
            # Ensure search_term can be encoded to cp1252
            search_term.encode('cp1252')
        except UnicodeEncodeError:
            # If Vietnamese characters can't encode to cp1252, try without special encoding
            pass
        
        cursor.execute(query_symptoms, (search_term, search_term))
        found_symptoms = cursor.fetchall()
        
        if not found_symptoms:
            return {
                "success": False,
                "message": "Không tìm thấy triệu chứng phù hợp",
                "specialties": []
            }
        
        # Lấy các specialty_id từ triệu chứng tìm thấy
        specialty_ids = list(dict.fromkeys([s[2] for s in found_symptoms if s[2]]))  # Remove duplicates, preserve order
        
        # Nếu không có specialty_id nào, dùng specialty_id 1
        if not specialty_ids:
            specialty_ids = [1]
        
        # Lấy top 3 specialties
        specialties_list = []
        for spec_id in specialty_ids[:3]:
            query_specialty = """
            SELECT specialty_id, name
            FROM SPECIALTIES
            WHERE specialty_id = ?
            """
            
            cursor.execute(query_specialty, (spec_id,))
            specialty = cursor.fetchone()
            
            if specialty:
                # Safely convert specialty name with fallback
                try:
                    specialty_name = str(specialty[1])
                except:
                    specialty_name = "Không xác định"
                
                # Đếm bác sĩ trong chuyên khoa
                query_doctors_count = """
                SELECT COUNT(*) FROM DOCTORS WHERE specialty_id = ?
                """
                
                cursor.execute(query_doctors_count, (spec_id,))
                doctors_count = cursor.fetchone()[0]
                
                specialties_list.append({
                    "specialty_id": specialty[0],
                    "specialty_name": specialty_name,
                    "doctors_count": doctors_count
                })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "specialties": specialties_list
        }
    
    except Exception as e:
        # Safe error message encoding
        try:
            error_msg = f"Lỗi: {str(e)}".encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except:
            error_msg = "Lỗi không xác định"
        
        print(f"❌ Error in get_specialty_for_symptoms: {e}")
        return {
            "success": False,
            "message": error_msg,
            "specialties": []
        }

# ============================================
# FUNCTION 2: KIỂM TRA SLOT KHÁM TRỐNG
# ============================================

def check_available_slots(
    specialty_id: int = None,
    specialty_name: str = None,
    date: Optional[str] = None,
    doctor_id: Optional[int] = None,
    doctor_name: Optional[str] = None,
    days_ahead: int = 7,
    dates_list: Optional[list] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Kiểm tra slot khám trống và chia thành các ca 2 tiếng
    Loại bỏ slots trong lịch nghỉ và đã được đặt
    
    Args:
        specialty_id: ID chuyên khoa (optional)
        specialty_name: Tên chuyên khoa (optional, sẽ convert thành ID)
        date: Ngày khám (format: YYYY-MM-DD), None = 7 ngày tới
        doctor_id: ID bác sĩ (optional)
        doctor_name: Tên bác sĩ (optional, sẽ convert thành ID)
        days_ahead: Số ngày tới để check (default: 7)
        dates_list: Danh sách ngày cụ thể (format: ["2025-11-28", "2025-11-29"]), nếu có sẽ ưu tiên hơn date và days_ahead
        limit: Số lượng ngày trả về
    
    Returns:
        Dict với availability theo ca 2 tiếng
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Nếu có specialty_name, convert thành ID
        if specialty_name and not specialty_id:
            query_spec = "SELECT specialty_id FROM SPECIALTIES WHERE name LIKE ?"
            cursor.execute(query_spec, (f"%{specialty_name}%",))
            spec_result = cursor.fetchone()
            if spec_result:
                specialty_id = spec_result[0]
            else:
                return {
                    "success": False,
                    "message": f"Không tìm thấy chuyên khoa '{specialty_name}'",
                    "availability": []
                }
        
        # Nếu có doctor_name, convert thành ID
        if doctor_name and not doctor_id:
            query_doc = "SELECT doctor_id FROM DOCTORS WHERE full_name LIKE ?"
            cursor.execute(query_doc, (f"%{doctor_name}%",))
            doc_result = cursor.fetchone()
            if doc_result:
                doctor_id = doc_result[0]
            else:
                return {
                    "success": False,
                    "message": f"Không tìm thấy bác sĩ '{doctor_name}'",
                    "availability": []
                }
        
        if not specialty_id and not doctor_id:
            return {
                "success": False,
                "message": "Vui lòng cung cấp specialty_id, specialty_name, doctor_id hoặc doctor_name",
                "availability": []
            }
        
        # Các ca làm việc: 7-9, 9-11, 13-15, 15-17
        time_slots = [
            {"name": "07:00-09:00", "start_hour": 7, "end_hour": 9},
            {"name": "09:00-11:00", "start_hour": 9, "end_hour": 11},
            {"name": "13:00-15:00", "start_hour": 13, "end_hour": 15},
            {"name": "15:00-17:00", "start_hour": 15, "end_hour": 17}
        ]
        
        # Xác định date range
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        if dates_list:
            # Nếu user cung cấp danh sách ngày cụ thể
            try:
                date_range = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates_list]
                # Sort dates
                date_range = sorted(date_range)
            except:
                return {
                    "success": False,
                    "message": "Format date sai trong dates_list, dùng YYYY-MM-DD",
                    "availability": []
                }
        elif date:
            try:
                check_date = datetime.strptime(date, "%Y-%m-%d").date()
                date_range = [check_date]
            except:
                return {
                    "success": False,
                    "message": "Format date sai, dùng YYYY-MM-DD",
                    "availability": []
                }
        else:
            # Tính 7 ngày tới
            date_range = [today + timedelta(days=i) for i in range(days_ahead)]
        
        # Lấy bác sĩ ID nếu chỉ có specialty
        doctor_ids = []
        if doctor_id:
            doctor_ids = [doctor_id]
        elif specialty_id:
            query_docs = "SELECT doctor_id FROM DOCTORS WHERE specialty_id = ? ORDER BY full_name"
            cursor.execute(query_docs, (specialty_id,))
            doctor_ids = [row[0] for row in cursor.fetchall()]
        
        if not doctor_ids:
            return {
                "success": False,
                "message": "Không tìm thấy bác sĩ",
                "availability": []
            }
        
        # Xây dựng availability list
        availability = []
        
        for check_date in date_range:
            day_name = check_date.strftime("%A")
            # Map to Vietnamese
            day_names_vi = {
                "Monday": "Thứ Hai", "Tuesday": "Thứ Ba", "Wednesday": "Thứ Tư",
                "Thursday": "Thứ Năm", "Friday": "Thứ Sáu",
                "Saturday": "Thứ Bảy", "Sunday": "Chủ Nhật"
            }
            day_name_vi = day_names_vi.get(day_name, day_name)
            
            day_availability = {
                "date": str(check_date),
                "day_name": day_name_vi,
                "slots": []
            }
            
            # Check từng ca
            for slot_info in time_slots:
                slot_name = slot_info["name"]
                start_hour = slot_info["start_hour"]
                end_hour = slot_info["end_hour"]
                
                # Tạo datetime range cho ca này
                slot_start = datetime.combine(check_date, datetime.min.time()).replace(hour=start_hour)
                slot_end = datetime.combine(check_date, datetime.min.time()).replace(hour=end_hour)
                
                # Kiểm tra xem có bác sĩ nào rảnh trong khoảng này không
                slot_available = False
                available_doctors = []
                
                for doc_id in doctor_ids:
                    # Kiểm tra DOCTOR_LEAVES
                    query_leaves = """
                    SELECT COUNT(*) FROM DOCTOR_LEAVES
                    WHERE doctor_id = ?
                      AND status IN ('pending', 'approved')
                      AND (start_datetime < ? AND end_datetime > ?)
                    """
                    cursor.execute(query_leaves, (
                        doc_id,
                        slot_end, slot_start
                    ))
                    leave_count = cursor.fetchone()[0]
                    
                    if leave_count > 0:
                        # Bác sĩ này đang nghỉ
                        continue
                    
                    # Kiểm tra APPOINTMENTS (pending/confirmed)
                    query_appts = """
                    SELECT COUNT(*) FROM APPOINTMENTS
                    WHERE doctor_id = ?
                      AND status IN ('pending', 'confirmed')
                      AND (
                        (appointment_datetime >= ? AND appointment_datetime < ?)
                      )
                    """
                    cursor.execute(query_appts, (
                        doc_id,
                        slot_start, slot_end
                    ))
                    appt_count = cursor.fetchone()[0]
                    
                    if appt_count > 0:
                        # Bác sĩ đã có appointment
                        continue
                    
                    # Bác sĩ này rảnh!
                    slot_available = True
                    query_doc_name = "SELECT full_name FROM DOCTORS WHERE doctor_id = ?"
                    cursor.execute(query_doc_name, (doc_id,))
                    doc_name = cursor.fetchone()[0]
                    available_doctors.append(doc_name)
                
                day_availability["slots"].append({
                    "slot_name": slot_name,
                    "available": slot_available,
                    "available_doctors": available_doctors if slot_available else [],
                    "reason": None if slot_available else "Tất cả bác sĩ đều bận hoặc đang nghỉ"
                })
            
            availability.append(day_availability)
        
        cursor.close()
        conn.close()
        
        # Get specialty name if we have specialty_id
        specialty_name = ""
        if specialty_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM SPECIALTIES WHERE specialty_id = ?", (specialty_id,))
            result = cursor.fetchone()
            if result:
                specialty_name = result[0]
            cursor.close()
            conn.close()
        
        return {
            "success": True,
            "message": f"Lấy lịch rảnh cho {len(availability)} ngày",
            "specialty_id": specialty_id,
            "specialty_name": specialty_name,
            "availability": availability
        }
    
    except Exception as e:
        print(f"❌ Error in check_available_slots: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "availability": []
        }

# ============================================
# FUNCTION 3: TẠO LỊCH HẸN (BOOKING)
# ============================================

def submit_booking(
    patient_id: int,
    slot_id: int,
    reason: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tạo lịch hẹn mới
    
    Args:
        patient_id: ID bệnh nhân
        slot_id: ID slot khám
        reason: Lý do khám (optional)
        notes: Ghi chú thêm (optional)
    
    Returns:
        Dict với thông tin lịch hẹn vừa tạo
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lấy thông tin slot
        query_slot = """
        SELECT slot_datetime, doctor_id, specialty_id, price
        FROM APPOINTMENT_SLOTS
        WHERE slot_id = ? AND status = 'available'
        """
        
        cursor.execute(query_slot, (slot_id,))
        slot = cursor.fetchone()
        
        if not slot:
            return {
                "success": False,
                "message": "Slot khám không khả dụng"
            }
        
        slot_datetime, doctor_id, specialty_id, price = slot
        
        # Tạo appointment
        query_appointment = """
        INSERT INTO APPOINTMENTS 
        (patient_id, doctor_id, specialty_id, appointment_datetime, status, notes, symptoms)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
        
        SELECT @@IDENTITY as appointment_id
        """
        
        cursor.execute(query_appointment, (
            patient_id,
            doctor_id,
            specialty_id,
            slot_datetime,
            notes or "",
            reason or ""
        ))
        
        appointment_id = cursor.fetchone()[0]
        
        # Update slot status
        query_update_slot = """
        UPDATE APPOINTMENT_SLOTS
        SET status = 'booked', updated_at = GETDATE()
        WHERE slot_id = ?
        """
        
        cursor.execute(query_update_slot, (slot_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Đặt lịch khám thành công",
            "appointment_id": int(appointment_id),
            "appointment_datetime": slot_datetime.isoformat(),
            "doctor_id": doctor_id,
            "specialty_id": specialty_id,
            "price": float(price) if price else 0
        }
    
    except Exception as e:
        print(f"❌ Error in submit_booking: {e}")
        return {
            "success": False,
            "message": f"Lỗi khi đặt lịch: {str(e)}"
        }

# ============================================
# FUNCTION 4: TÌM THÔNG TIN THUỐC
# ============================================

def search_medicines(search_term: str) -> Dict[str, Any]:
    """
    Tìm thông tin về thuốc sử dụng Gemini API
    Truy vấn Gemini để lấy thông tin y tế chính xác về thuốc từ internet
    
    Args:
        search_term: Tên thuốc hoặc từ khóa tìm kiếm
    
    Returns:
        Dict với danh sách thuốc tìm thấy từ Gemini
    """
    try:
        from config import GEMINI_API_KEY
        import google.generativeai as genai
        
        # Validate input
        if not search_term or not isinstance(search_term, str) or len(search_term.strip()) == 0:
            return {
                "success": False,
                "message": "Từ khóa tìm kiếm không hợp lệ",
                "medicines": []
            }
        
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Create prompt for Gemini to search for medicines
        prompt = f"""
Bạn là trợ lý y tế chuyên về thông tin thuốc. Người dùng đang tìm kiếm thông tin về: "{search_term}"

Hãy tìm và cung cấp thông tin chi tiết về thuốc/tác dụng này:
1. Tên chính thức của thuốc
2. Tên gọi khác (nếu có)
3. Thành phần chính
4. Tác dụng chính
5. Liều dùng thông thường
6. Tác dụng phụ thường gặp
7. Chống chỉ định
8. Giá tiền ước tính (nếu có)

Trả lời dưới dạng JSON với cấu trúc:
{{
  "medicines": [
    {{
      "name": "Tên thuốc",
      "generic_name": "Tên hoạt chất",
      "usage": "Tác dụng chính",
      "dosage": "Liều dùng",
      "side_effects": "Tác dụng phụ",
      "contraindications": "Chống chỉ định",
      "price": "Giá ước tính (nếu biết)"
    }}
  ],
  "note": "Ghi chú nếu có"
}}

Chỉ tìm và trả lại tối đa 5 kết quả thuốc liên quan nhất.
Nếu không tìm thấy thông tin phù hợp, trả lại danh sách rỗng.
"""
        
        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            return {
                "success": False,
                "message": "Không thể phân tích phản hồi từ Gemini",
                "medicines": []
            }
        
        try:
            data = json.loads(json_match.group())
            medicines = data.get("medicines", [])
            
            if not medicines or len(medicines) == 0:
                return {
                    "success": False,
                    "message": f"Không tìm thấy thông tin về thuốc '{search_term}'",
                    "medicines": []
                }
            
            # Format medicines list
            medicines_list = []
            for med in medicines[:5]:  # Limit to 5 results
                medicines_list.append({
                    "name": med.get("name", ""),
                    "generic_name": med.get("generic_name", ""),
                    "usage": med.get("usage", ""),
                    "dosage": med.get("dosage", ""),
                    "side_effects": med.get("side_effects", ""),
                    "contraindications": med.get("contraindications", ""),
                    "price": med.get("price", "Không rõ")
                })
            
            return {
                "success": True,
                "message": f"Tìm thấy {len(medicines_list)} thông tin về thuốc/tác dụng '{search_term}'",
                "medicines": medicines_list,
                "note": data.get("note", "")
            }
        
        except json.JSONDecodeError as je:
            return {
                "success": False,
                "message": f"Lỗi phân tích dữ liệu: {str(je)}",
                "medicines": []
            }
    
    except Exception as e:
        print(f"❌ Error in search_medicines: {e}")
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "medicines": []
        }

# ============================================
# FUNCTION 5: LẤY HƯỚNG DẪN CHUẨN BỊ KHÁM
# ============================================

def get_consultation_guide(specialty_id: int) -> Dict[str, Any]:
    """
    Lấy hướng dẫn chuẩn bị khám cho chuyên khoa
    
    Args:
        specialty_id: ID chuyên khoa
    
    Returns:
        Dict với hướng dẫn chuẩn bị
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT
            guide_id,
            title,
            content,
            items_to_bring,
            preparation_notes,
            estimated_duration_minutes
        FROM CONSULTATION_GUIDES
        WHERE specialty_id = ? AND is_active = 1
        """
        
        cursor.execute(query, (specialty_id,))
        guide = cursor.fetchone()
        
        conn.close()
        
        if not guide:
            return {
                "success": False,
                "message": "Không tìm thấy hướng dẫn chuẩn bị",
                "guide": None
            }
        
        return {
            "success": True,
            "guide": {
                "guide_id": guide[0],
                "title": guide[1],
                "content": guide[2],
                "items_to_bring": guide[3],
                "preparation_notes": guide[4],
                "estimated_duration_minutes": guide[5]
            }
        }
    
    except Exception as e:
        print(f"❌ Error in get_consultation_guide: {e}")
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "guide": None
        }

# ============================================
# FUNCTION 6: TÌM BÁC SĨ THEO CHUYÊN KHOA
# ============================================

def get_doctors_by_specialty(specialty_id: int = None, specialty_name: str = None, doctor_name: str = None, limit: int = 5) -> Dict[str, Any]:
    """
    Lấy danh sách bác sĩ theo chuyên khoa hoặc tên
    
    Args:
        specialty_id: ID chuyên khoa (optional)
        specialty_name: Tên chuyên khoa (optional, sẽ được convert thành ID)
        doctor_name: Tên bác sĩ (optional)
        limit: Số lượng bác sĩ trả về
    
    Returns:
        Dict với danh sách bác sĩ
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If specialty_name is provided, find specialty_id
        if specialty_name and not specialty_id:
            query_spec = """
            SELECT specialty_id FROM SPECIALTIES
            WHERE name LIKE ?
            """
            cursor.execute(query_spec, (f"%{specialty_name}%",))
            spec_result = cursor.fetchone()
            if spec_result:
                specialty_id = spec_result[0]
            else:
                return {
                    "success": False,
                    "message": f"Không tìm thấy chuyên khoa '{specialty_name}'",
                    "doctors": []
                }
        
        # Build query based on parameters
        if specialty_id and doctor_name:
            query = """
            SELECT TOP (?)
                doctor_id,
                full_name,
                email,
                phone,
                qualifications,
                specialty_id
            FROM DOCTORS
            WHERE specialty_id = ? AND full_name LIKE ?
            ORDER BY full_name ASC
            """
            cursor.execute(query, (limit, specialty_id, f"%{doctor_name}%"))
        elif specialty_id:
            query = """
            SELECT TOP (?)
                doctor_id,
                full_name,
                email,
                phone,
                qualifications,
                specialty_id
            FROM DOCTORS
            WHERE specialty_id = ?
            ORDER BY full_name ASC
            """
            cursor.execute(query, (limit, specialty_id))
        elif doctor_name:
            query = """
            SELECT TOP (?)
                doctor_id,
                full_name,
                email,
                phone,
                qualifications,
                specialty_id
            FROM DOCTORS
            WHERE full_name LIKE ?
            ORDER BY full_name ASC
            """
            cursor.execute(query, (limit, f"%{doctor_name}%"))
        else:
            return {
                "success": False,
                "message": "Vui lòng cung cấp ID/tên chuyên khoa hoặc tên bác sĩ",
                "doctors": []
            }
        doctors = cursor.fetchall()
        
        conn.close()
        
        if not doctors:
            return {
                "success": False,
                "message": "Không tìm thấy bác sĩ nào",
                "doctors": []
            }
        
        doctors_list = []
        for doc in doctors:
            doctors_list.append({
                "doctor_id": doc[0],
                "name": doc[1],
                "email": doc[2],
                "phone": doc[3],
                "qualifications": doc[4],
                "specialty_id": doc[5]
            })
        
        return {
            "success": True,
            "message": f"Tìm thấy {len(doctors_list)} bác sĩ",
            "doctors": doctors_list
        }
    
    except Exception as e:
        print(f"❌ Error in get_doctors_by_specialty: {e}")
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "doctors": []
        }

# ============================================
# FUNCTION 7: LƯU CUỘC HỘI THOẠI
# ============================================

def save_chat_conversation(
    patient_id: Optional[int] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tạo mới một cuộc hội thoại
    
    Args:
        patient_id: ID bệnh nhân (optional)
        session_id: Session ID (optional)
    
    Returns:
        Dict với conversation_id
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO CHAT_CONVERSATIONS (PATIENT_ID, SESSION_ID, STATUS, CREATED_AT)
        VALUES (?, ?, 'active', GETDATE())
        """
        
        cursor.execute(query, (patient_id, session_id))
        conn.commit()
        
        # Lấy ID vừa tạo
        cursor.execute("SELECT @@IDENTITY as conversation_id")
        result = cursor.fetchone()
        conversation_id = result[0] if result else None
        
        conn.close()
        
        return {
            "success": True,
            "conversation_id": int(conversation_id) if conversation_id else None
        }
    
    except Exception as e:
        print(f"❌ Error in save_chat_conversation: {e}")
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }

# ============================================
# FUNCTION 8: LƯU MESSAGE
# ============================================

def save_chat_message(
    conversation_id: int,
    sender_type: str,
    message_text: str,
    tool_used: Optional[str] = None,
    tool_response: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lưu một message trong cuộc hội thoại
    
    Args:
        conversation_id: ID cuộc hội thoại
        sender_type: 'user' hoặc 'bot'
        message_text: Nội dung message
        tool_used: Tên tool được gọi (optional)
        tool_response: Kết quả từ tool (optional)
    
    Returns:
        Dict với message_id
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO CHAT_MESSAGES 
        (conversation_id, sender_type, message_text, tool_used, tool_response, created_at)
        VALUES (?, ?, ?, ?, ?, GETDATE())
        
        SELECT @@IDENTITY as message_id
        """
        
        cursor.execute(query, (
            conversation_id,
            sender_type,
            message_text,
            tool_used,
            tool_response
        ))
        
        message_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message_id": int(message_id)
        }
    
    except Exception as e:
        print(f"❌ Error in save_chat_message: {e}")
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("Testing Database Module...")
    
    # Test 1: Get specialty for symptoms
    print("\n1️⃣ Test: get_specialty_for_symptoms('đau đầu')")
    result = get_specialty_for_symptoms("đau đầu")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Test 2: Check available slots
    if result.get("success"):
        print(f"\n2️⃣ Test: check_available_slots({result['specialty_id']})")
        result2 = check_available_slots(result['specialty_id'])
        print(json.dumps(result2, ensure_ascii=False, indent=2)[:200] + "...")
