"""
Chatbot Module
Hệ thống chatbot y tế thông minh sử dụng Gemini API + Function Calling
"""

from .tools import (
    GET_SPECIALTY_FOR_SYMPTOMS,
    CHECK_AVAILABLE_SLOTS,
    GET_CONSULTATION_GUIDE,
    GET_DOCTORS_BY_SPECIALTY,
    TOOLS_LIST,
    GEMINI_TOOLS
)

from .tool_handlers import (
    process_tool_call,
    handle_get_specialty_for_symptoms,
    handle_check_available_slots,
    handle_get_consultation_guide,
    handle_get_doctors_by_specialty
)

from .chatbot_repository import (
    ChatbotRepository,
    chatbot_repository
)

from .chatbot_router import router as chatbot_router

__all__ = [
    # Tools
    'GET_SPECIALTY_FOR_SYMPTOMS',
    'CHECK_AVAILABLE_SLOTS',
    'GET_CONSULTATION_GUIDE',
    'GET_DOCTORS_BY_SPECIALTY',
    'TOOLS_LIST',
    'GEMINI_TOOLS',
    
    # Handlers
    'process_tool_call',
    'handle_get_specialty_for_symptoms',
    'handle_check_available_slots',
    'handle_get_consultation_guide',
    'handle_get_doctors_by_specialty',
    
    # Repository
    'ChatbotRepository',
    'chatbot_repository',
    
    # Router
    'chatbot_router',
]
