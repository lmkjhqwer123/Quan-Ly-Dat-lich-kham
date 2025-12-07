"""
🔧 TOOL HANDLERS - Xử lý Tool Calls từ Gemini API

Nhận tool_call từ Gemini → Gọi hàm database → Return kết quả
Bao gồm: logging, error handling, parameter validation
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from DataAccessLayer.chatbot_db import (
    get_specialty_for_symptoms,
    check_available_slots,
    search_medicines,
    get_consultation_guide,
    get_doctors_by_specialty
)

# ============================================
# SETUP LOGGING
# ============================================

logger = logging.getLogger("ChatbotToolHandler")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ============================================
# TOOL HANDLER FUNCTIONS
# ============================================

def handle_get_specialty_for_symptoms(symptoms_text: str) -> Dict[str, Any]:
    """
    Handler cho tool: get_specialty_for_symptoms
    
    Args:
        symptoms_text: Mô tả triệu chứng
    
    Returns:
        Dict với kết quả
    """
    try:
        # Xử lý encoding input trước khi log
        try:
            safe_symptoms = symptoms_text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            logger.info(f"[TOOL] get_specialty_for_symptoms called with: symptoms_text='{safe_symptoms}'")
        except:
            logger.info(f"[TOOL] get_specialty_for_symptoms called")
        
        # Validate input
        if not symptoms_text or not isinstance(symptoms_text, str):
            logger.warning(f"[TOOL] Invalid symptoms_text: {symptoms_text}")
            return {
                "success": False,
                "message": "Triệu chứng không hợp lệ",
                "specialties": []
            }
        
        # Gọi database function
        result = get_specialty_for_symptoms(symptoms_text)
        
        # Log result - xử lý encoding an toàn
        try:
            safe_result = json.dumps(result, ensure_ascii=False, indent=2)
            logger.info(f"[TOOL] get_specialty_for_symptoms result: {safe_result}")
        except:
            logger.info(f"[TOOL] get_specialty_for_symptoms result: {result.get('success')}")
        
        return result
    
    except Exception as e:
        logger.error(f"[TOOL] Error in get_specialty_for_symptoms: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "specialties": []
        }

def handle_check_available_slots(
    specialty_id: int,
    date: Optional[str] = None,
    doctor_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Handler cho tool: check_available_slots
    
    Args:
        specialty_id: ID chuyên khoa
        date: Ngày khám (YYYY-MM-DD)
        doctor_id: ID bác sĩ
    
    Returns:
        Dict với danh sách slots
    """
    try:
        logger.info(f"[TOOL] check_available_slots called with: specialty_id={specialty_id}, date={date}, doctor_id={doctor_id}")
        
        # Validate input
        if not isinstance(specialty_id, int) or specialty_id <= 0:
            logger.warning(f"[TOOL] Invalid specialty_id: {specialty_id}")
            return {
                "success": False,
                "message": "ID chuyên khoa không hợp lệ",
                "slots": []
            }
        
        # Gọi database function
        result = check_available_slots(
            specialty_id=specialty_id,
            date=date,
            doctor_id=doctor_id,
            limit=5  # Limit = 5 theo yêu cầu
        )
        
        # Log result
        logger.info(f"[TOOL] check_available_slots result: {len(result.get('slots', []))} slots found")
        logger.debug(f"[TOOL] check_available_slots full result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    
    except Exception as e:
        logger.error(f"[TOOL] Error in check_available_slots: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "slots": []
        }

def handle_search_medicines(search_term: str) -> Dict[str, Any]:
    """
    Handler cho tool: search_medicines
    
    Args:
        search_term: Tên thuốc hoặc tác dụng
    
    Returns:
        Dict với danh sách thuốc từ Gemini
    """
    try:
        logger.info(f"[TOOL] search_medicines called with: search_term='{search_term}'")
        
        # Validate input
        if not search_term or not isinstance(search_term, str):
            logger.warning(f"[TOOL] Invalid search_term: {search_term}")
            return {
                "success": False,
                "message": "Từ khóa tìm kiếm không hợp lệ",
                "medicines": []
            }
        
        # Gọi database function (sẽ gọi Gemini API bên trong)
        result = search_medicines(search_term)
        
        # Log result
        logger.info(f"[TOOL] search_medicines result: {len(result.get('medicines', []))} medicines found")
        logger.debug(f"[TOOL] search_medicines full result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    
    except Exception as e:
        logger.error(f"[TOOL] Error in search_medicines: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "medicines": []
        }

def handle_get_consultation_guide(specialty_id: int) -> Dict[str, Any]:
    """
    Handler cho tool: get_consultation_guide
    
    Args:
        specialty_id: ID chuyên khoa
    
    Returns:
        Dict với hướng dẫn chuẩn bị
    """
    try:
        logger.info(f"[TOOL] get_consultation_guide called with: specialty_id={specialty_id}")
        
        # Validate input
        if not isinstance(specialty_id, int) or specialty_id <= 0:
            logger.warning(f"[TOOL] Invalid specialty_id: {specialty_id}")
            return {
                "success": False,
                "message": "ID chuyên khoa không hợp lệ",
                "guide": None
            }
        
        # Gọi database function
        result = get_consultation_guide(specialty_id)
        
        # Log result
        logger.info(f"[TOOL] get_consultation_guide result: success={result.get('success')}")
        logger.debug(f"[TOOL] get_consultation_guide full result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    
    except Exception as e:
        logger.error(f"[TOOL] Error in get_consultation_guide: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "guide": None
        }

def handle_get_doctors_by_specialty(
    specialty_id: Optional[int] = None,
    doctor_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handler cho tool: get_doctors_by_specialty
    
    Args:
        specialty_id: ID chuyên khoa (tùy chọn)
        doctor_name: Tên bác sĩ (tùy chọn)
    
    Returns:
        Dict với danh sách bác sĩ
    """
    try:
        logger.info(f"[TOOL] get_doctors_by_specialty called with: specialty_id={specialty_id}, doctor_name={doctor_name}")
        
        # Validate input
        if specialty_id is not None and (not isinstance(specialty_id, int) or specialty_id <= 0):
            logger.warning(f"[TOOL] Invalid specialty_id: {specialty_id}")
            return {
                "success": False,
                "message": "ID chuyên khoa không hợp lệ",
                "doctors": []
            }
        
        # Gọi database function
        result = get_doctors_by_specialty(
            specialty_id=specialty_id,
            limit=5  # Limit = 5 theo yêu cầu
        )
        
        # Log result
        logger.info(f"[TOOL] get_doctors_by_specialty result: {len(result.get('doctors', []))} doctors found")
        logger.debug(f"[TOOL] get_doctors_by_specialty full result: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
    
    except Exception as e:
        logger.error(f"[TOOL] Error in get_doctors_by_specialty: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi: {str(e)}",
            "doctors": []
        }

# ============================================
# MAIN TOOL PROCESSOR
# ============================================

def process_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Xử lý tool call từ Gemini API
    
    Args:
        tool_name: Tên của tool
        tool_args: Arguments của tool
    
    Returns:
        Dict với kết quả từ tool
    """
    
    logger.info(f"[PROCESS] Tool call received: {tool_name}")
    logger.info(f"[PROCESS] Tool args: {json.dumps(tool_args, ensure_ascii=False)}")
    
    try:
        # Route đến handler đúng
        if tool_name == "get_specialty_for_symptoms":
            result = handle_get_specialty_for_symptoms(
                symptoms_text=tool_args.get("symptoms_text", "")
            )
        
        elif tool_name == "check_available_slots":
            result = handle_check_available_slots(
                specialty_id=tool_args.get("specialty_id"),
                date=tool_args.get("date"),
                doctor_id=tool_args.get("doctor_id")
            )
        
        elif tool_name == "search_medicines":
            result = handle_search_medicines(
                search_term=tool_args.get("search_term", "")
            )
        
        elif tool_name == "get_consultation_guide":
            result = handle_get_consultation_guide(
                specialty_id=tool_args.get("specialty_id")
            )
        
        elif tool_name == "get_doctors_by_specialty":
            result = handle_get_doctors_by_specialty(
                specialty_id=tool_args.get("specialty_id"),
                doctor_name=tool_args.get("doctor_name")
            )
        
        else:
            logger.warning(f"[PROCESS] Unknown tool: {tool_name}")
            result = {
                "success": False,
                "message": f"Tool '{tool_name}' không tồn tại"
            }
        
        # Log final result
        logger.info(f"[PROCESS] Tool call completed: {tool_name} → success={result.get('success')}")
        
        return result
    
    except Exception as e:
        logger.error(f"[PROCESS] Error processing tool call: {tool_name}", exc_info=True)
        return {
            "success": False,
            "message": f"Lỗi xử lý tool call: {str(e)}"
        }

# ============================================
# UTILITY FUNCTIONS
# ============================================

def log_tool_call_summary(tool_name: str, success: bool, message: str = ""):
    """Log tóm tắt của một tool call"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"[SUMMARY] {status} - {tool_name}: {message}")
