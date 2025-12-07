"""
CHATBOT SERVICE - Gemini API Integration with Function Calling
Tích hợp Gemini để xử lý messages thông minh với tool calling
"""

import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from functools import lru_cache
from datetime import datetime, timedelta
import os
import google.generativeai as genai
from config import GEMINI_API_KEY
from routers.chatbot.system_prompt import SYSTEM_PROMPT
from routers.chatbot.tools import GEMINI_TOOLS
from DataAccessLayer.chatbot_db import (
    get_specialty_for_symptoms,
    check_available_slots,
    get_consultation_guide,
    get_doctors_by_specialty
)

# Setup logging
logger = logging.getLogger("ChatbotService")

# ============================================
# API KEY MANAGEMENT - Key rotation support
# ============================================
_api_keys = []
_current_key_index = 0

def _init_api_keys():
    """Khởi tạo danh sách API keys từ .env"""
    global _api_keys, _current_key_index
    
    # Lấy backup keys từ env
    backup_keys_str = os.getenv("GEMINI_API_KEYS", "")
    if backup_keys_str:
        _api_keys = [key.strip() for key in backup_keys_str.split(",") if key.strip()]
    else:
        _api_keys = [GEMINI_API_KEY]
    
    _current_key_index = 0
    logger.info(f"[INIT] Loaded {len(_api_keys)} API key(s)")

def _get_current_api_key() -> str:
    """Lấy API key hiện tại"""
    global _api_keys, _current_key_index
    if not _api_keys:
        _init_api_keys()
    return _api_keys[_current_key_index]

def _rotate_api_key():
    """Rotate sang API key tiếp theo"""
    global _api_keys, _current_key_index
    if not _api_keys:
        _init_api_keys()
    
    _current_key_index = (_current_key_index + 1) % len(_api_keys)
    new_key = _api_keys[_current_key_index]
    genai.configure(api_key=new_key)
    logger.warning(f"[KEY ROTATE] Switched to key #{_current_key_index + 1}/{len(_api_keys)}")
    return new_key

# Configure Gemini API with initial key
_init_api_keys()
genai.configure(api_key=_get_current_api_key())

# ============================================
# RESPONSE CACHING - Giảm API calls
# ============================================
_response_cache = {}  # Format: {user_msg_hash: (response, timestamp)}
_cache_ttl = 3600  # Cache trong 1 giờ

def _get_cache_key(user_message: str) -> str:
    """Tạo cache key từ user message"""
    return user_message.lower().strip()

def _get_cached_response(user_message: str) -> Optional[Tuple[str, Optional[str], Optional[str]]]:
    """Lấy response từ cache nếu còn hiệu lực"""
    cache_key = _get_cache_key(user_message)
    
    if cache_key in _response_cache:
        response_data, timestamp = _response_cache[cache_key]
        # Kiểm tra cache còn hiệu lực không
        if datetime.now() - timestamp < timedelta(seconds=_cache_ttl):
            logger.info(f"[CACHE HIT] Using cached response for: {user_message[:50]}...")
            return response_data
        else:
            # Cache hết hạn
            del _response_cache[cache_key]
    
    return None

def _cache_response(user_message: str, response_tuple: Tuple[str, Optional[str], Optional[str]]):
    """Lưu response vào cache"""
    cache_key = _get_cache_key(user_message)
    _response_cache[cache_key] = (response_tuple, datetime.now())
    logger.info(f"[CACHE SET] Cached response for: {user_message[:50]}...")


# ============================================
# TOOL EXECUTORS
# ============================================

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """
    Execute a tool based on tool name and arguments
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
    
    Returns:
        Tool result as JSON string
    """
    try:
        logger.info(f"[TOOL EXECUTE] {tool_name} with args: {tool_args}")
        
        if tool_name == "get_specialty_for_symptoms":
            result = get_specialty_for_symptoms(tool_args.get("symptoms_text", ""))
        
        elif tool_name == "check_available_slots":
            result = check_available_slots(
                specialty_id=tool_args.get("specialty_id"),
                specialty_name=tool_args.get("specialty_name"),
                date=tool_args.get("date"),
                doctor_id=tool_args.get("doctor_id"),
                doctor_name=tool_args.get("doctor_name"),
                days_ahead=tool_args.get("days_ahead", 7),
                dates_list=tool_args.get("dates_list")
            )
        
        elif tool_name == "get_consultation_guide":
            result = get_consultation_guide(tool_args.get("specialty_id"))
        
        elif tool_name == "get_doctors_by_specialty":
            result = get_doctors_by_specialty(
                specialty_id=tool_args.get("specialty_id"),
                specialty_name=tool_args.get("specialty_name"),
                doctor_name=tool_args.get("doctor_name")
            )
        
        else:
            result = {"success": False, "message": f"Unknown tool: {tool_name}"}
        
        # Convert result to JSON string
        result_str = json.dumps(result, ensure_ascii=False)
        logger.info(f"[TOOL RESULT] {tool_name}: {result_str[:100]}...")
        
        return result_str
    
    except Exception as e:
        logger.error(f"[TOOL ERROR] {tool_name}: {str(e)}")
        return json.dumps({
            "success": False,
            "message": f"Error executing tool: {str(e)}"
        })


# ============================================
# GEMINI CHATBOT SERVICE
# ============================================

class ChatbotService:
    """Service class for Gemini-powered chatbot with function calling"""
    
    def __init__(self):
        """Initialize Gemini model and tools"""
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            tools=GEMINI_TOOLS,
            system_instruction=SYSTEM_PROMPT
        )
        logger.info("[INIT] ChatbotService initialized with Gemini 2.0 Flash")
    
    def process_message(self, 
                       user_message: str, 
                       conversation_history: List[Dict[str, str]] = None) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Process user message with Gemini Function Calling
        With built-in caching to reduce API quota usage
        
        Args:
            user_message: User's input message
            conversation_history: List of previous messages for context
        
        Returns:
            Tuple of (response_text, tool_used, tool_response)
        """
        # Kiểm tra cache trước tiên
        cached_result = _get_cached_response(user_message)
        if cached_result is not None:
            return cached_result
        
        try:
            # Prepare message history for Gemini
            history = self._prepare_chat_history(conversation_history)
            
            # Create chat session
            chat = self.model.start_chat(history=history)
            
            logger.info(f"[MESSAGE] Processing: {user_message[:60]}...")
            
            # Send message to Gemini with tools
            response = chat.send_message(user_message)
            
            # Check if Gemini called any tools
            tool_used = None
            tool_response = None
            response_text = ""
            
            # Try to get parts from response
            parts = []
            if hasattr(response, 'candidates') and response.candidates:
                content = response.candidates[0].content
                if hasattr(content, 'parts'):
                    parts = content.parts
            
            # Agentic loop: Allow Gemini to call multiple tools in sequence
            function_call_found = False
            tool_used = None
            tool_response = None
            max_tool_calls = 3  # Prevent infinite loops
            tool_calls_made = 0
            
            while tool_calls_made < max_tool_calls:
                # Look for function calls and text in current response
                found_function_call = False
                
                for part in parts:
                    # Check if it's a function call
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        tool_used = function_call.name
                        tool_args = dict(function_call.args)
                        
                        logger.info(f"[TOOL CALL {tool_calls_made + 1}] Gemini called: {tool_used}")
                        
                        # Execute the tool
                        tool_response = execute_tool(tool_used, tool_args)
                        function_call_found = True
                        found_function_call = True
                        tool_calls_made += 1
                        
                        # Send tool response back to Gemini
                        response = chat.send_message(
                            [
                                {
                                    "function_response": {
                                        "name": tool_used,
                                        "response": json.loads(tool_response) if isinstance(tool_response, str) else tool_response
                                    }
                                }
                            ]
                        )
                        
                        # Get new parts from Gemini response
                        parts = []
                        if hasattr(response, 'candidates') and response.candidates:
                            content = response.candidates[0].content
                            if hasattr(content, 'parts'):
                                parts = content.parts
                        
                        break  # Break inner for loop to re-check parts
                    
                    # Extract any text from non-function-call parts
                    elif hasattr(part, 'text') and part.text and not found_function_call:
                        response_text = part.text
                
                # If no function call found in this iteration, break the while loop
                if not found_function_call:
                    break
            
            # If no function calls were made, try to extract text from original response
            if not function_call_found and not response_text:
                response_text = self._extract_text_response(response)
            
            logger.info(f"[RESPONSE] {response_text[:80]}...")
            
            # Cache response trước khi return
            result_tuple = (response_text, tool_used, tool_response)
            _cache_response(user_message, result_tuple)
            
            return response_text, tool_used, tool_response
        
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's API quota error
            if "429" in error_str or "quota" in error_str or "exceeded" in error_str:
                logger.warning(f"[QUOTA] API quota exceeded with current key")
                
                # Try to rotate to next API key if available
                if len(_api_keys) > 1:
                    _rotate_api_key()
                    logger.info(f"[RETRY] Retrying with rotated key...")
                    
                    # Retry with rotated key
                    try:
                        # Recursive call with new key
                        return self.process_message(user_message, conversation_history)
                    except Exception as retry_error:
                        logger.error(f"[RETRY FAILED] {str(retry_error)}")
                        return "Xin lỗi, hệ thống đang có quá nhiều yêu cầu. Vui lòng thử lại sau.", None, None
                else:
                    # Chỉ có 1 key, không thể rotate
                    logger.warning(f"[FALLBACK] No backup keys available, using cached/mock response")
                    return "Xin lỗi, hệ thống tạm thời quá tải. Vui lòng thử lại sau.", None, None
            
            # For other errors, return error message
            logger.error(f"[ERROR] Processing message: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Xin lỗi, tôi gặp lỗi: {str(e)}", None, None
    
    def _prepare_chat_history(self, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Prepare chat history in Gemini format
        
        Args:
            conversation_history: List of {"message_text": "...", "sender_type": "user"/"bot"}
        
        Returns:
            Formatted history for Gemini chat
        """
        if not conversation_history:
            return []
        
        history = []
        for msg in conversation_history:
            role = "user" if msg.get("sender_type") == "user" else "model"
            history.append({
                "role": role,
                "parts": [msg.get("message_text", "")]
            })
        
        return history
    
    def _extract_text_response(self, response) -> str:
        """
        Extract text response from Gemini response object
        
        Args:
            response: Gemini API response
        
        Returns:
            Extracted text or empty string
        """
        try:
            # Try direct .text property first
            if hasattr(response, 'text') and response.text:
                return response.text
            
            # Try extracting from parts
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            # Skip function calls, only get text
                            if hasattr(part, 'text') and part.text:
                                return part.text
            
            return "Xin lỗi, tôi không thể tạo phản hồi lúc này."
        
        except Exception as e:
            logger.error(f"[ERROR] Extracting text: {str(e)}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý phản hồi."


# ============================================
# SINGLETON INSTANCE
# ============================================

_chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """
    Get or create singleton instance of ChatbotService
    
    Returns:
        ChatbotService instance
    """
    global _chatbot_service
    
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
        logger.info("[SINGLETON] ChatbotService instance created")
    
    return _chatbot_service
