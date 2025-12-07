"""
🛠️ TOOLS DEFINITION FOR GEMINI FUNCTION CALLING
Định nghĩa các tools để Gemini API có thể gọi các hàm backend

Tools:
1. get_specialty_for_symptoms - Tìm chuyên khoa từ triệu chứng
2. check_available_slots - Kiểm tra slot khám trống
3. search_medicines - Tìm kiếm thuốc
4. get_consultation_guide - Lấy hướng dẫn chuẩn bị
5. get_doctors_by_specialty - Tìm bác sĩ theo chuyên khoa
"""

from google.generativeai.types import FunctionDeclaration

# ============================================
# TOOL 1: GET_SPECIALTY_FOR_SYMPTOMS
# ============================================

GET_SPECIALTY_FOR_SYMPTOMS = FunctionDeclaration(
    name="get_specialty_for_symptoms",
    description="Tìm chuyên khoa phù hợp dựa trên triệu chứng của bệnh nhân.",
    parameters={
        "type": "object",
        "properties": {
            "symptoms_text": {
                "type": "string",
                "description": "Mô tả triệu chứng"
            }
        },
        "required": ["symptoms_text"]
    }
)

# ============================================
# TOOL 2: CHECK_AVAILABLE_SLOTS
# ============================================

CHECK_AVAILABLE_SLOTS = FunctionDeclaration(
    name="check_available_slots",
    description="Kiểm tra các slot khám trống chia thành ca 2 tiếng (07-09, 09-11, 13-15, 15-17). Tự động lọc các ca mà bác sĩ đang nghỉ hoặc đã có lịch hẹn.",
    parameters={
        "type": "object",
        "properties": {
            "specialty_id": {
                "type": "integer",
                "description": "ID của chuyên khoa"
            },
            "specialty_name": {
                "type": "string",
                "description": "Tên của chuyên khoa (VD: Khoa Nội, Da liễu, Nha khoa)"
            },
            "date": {
                "type": "string",
                "description": "Ngày cụ thể cần kiểm tra (YYYY-MM-DD). Nếu không có, mặc định kiểm tra 7 ngày tới"
            },
            "doctor_id": {
                "type": "integer",
                "description": "ID bác sĩ cụ thể (optional)"
            },
            "doctor_name": {
                "type": "string",
                "description": "Tên bác sĩ (VD: Trần Thị B, Nguyễn Văn A)"
            },
            "days_ahead": {
                "type": "integer",
                "description": "Số ngày tới để kiểm tra (default: 7). VD: 5 = 5 ngày tới"
            },
            "dates_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Danh sách ngày cụ thể cần kiểm tra (YYYY-MM-DD). VD: ['2025-11-28', '2025-11-29', '2025-11-30']. Nếu có sẽ ưu tiên hơn date và days_ahead"
            }
        },
        "required": []
    }
)

# ============================================
# TOOL 3: GET_CONSULTATION_GUIDE
# ============================================

GET_CONSULTATION_GUIDE = FunctionDeclaration(
    name="get_consultation_guide",
    description="Lấy hướng dẫn chuẩn bị khám cho một chuyên khoa.",
    parameters={
        "type": "object",
        "properties": {
            "specialty_id": {
                "type": "integer",
                "description": "ID của chuyên khoa"
            }
        },
        "required": ["specialty_id"]
    }
)

# ============================================
# TOOL 5: GET_DOCTORS_BY_SPECIALTY
# ============================================

GET_DOCTORS_BY_SPECIALTY = FunctionDeclaration(
    name="get_doctors_by_specialty",
    description="Tìm danh sách bác sĩ theo chuyên khoa hoặc tên.",
    parameters={
        "type": "object",
        "properties": {
            "specialty_id": {
                "type": "integer",
                "description": "ID của chuyên khoa"
            },
            "specialty_name": {
                "type": "string",
                "description": "Tên của chuyên khoa (VD: Nội tổng quát, Da liễu)"
            },
            "doctor_name": {
                "type": "string",
                "description": "Tên bác sĩ hoặc một phần tên"
            }
        },
        "required": []
    }
)

# ============================================
# DANH SÁCH TẤT CẢ TOOLS
# ============================================

TOOLS_LIST = [
    GET_SPECIALTY_FOR_SYMPTOMS,
    CHECK_AVAILABLE_SLOTS,
    GET_CONSULTATION_GUIDE,
    GET_DOCTORS_BY_SPECIALTY
]

# Gemini API format - just pass the tool objects directly
GEMINI_TOOLS = TOOLS_LIST
