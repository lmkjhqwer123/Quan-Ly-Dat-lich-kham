"""
CHATBOT API ROUTER - Endpoints cho chatbot frontend
Tích hợp Gemini Function Calling thông qua ChatbotService
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

# Import existing modules
from routers.chatbot.chatbot_repository import chatbot_repository
from routers.chatbot.chatbot_service import get_chatbot_service

# Setup logging
logger = logging.getLogger("ChatbotRouter")

# Create router
router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SendMessageRequest(BaseModel):
    """Request model for sending a message to chatbot"""
    conversation_id: Optional[int] = None
    message: str


class SendMessageResponse(BaseModel):
    """Response model for chatbot message"""
    conversation_id: int
    response: str
    tool_used: Optional[str] = None
    tool_response: Optional[str] = None
    booking_data: Optional[dict] = None  # For booking slot information


class NewConversationResponse(BaseModel):
    """Response model for creating new conversation"""
    conversation_id: int
    session_id: str


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    conversation_id: int
    messages: list


# ============================================
# ENDPOINTS
# ============================================

@router.post("/new-conversation", response_model=NewConversationResponse)
async def create_new_conversation():
    """
    Create a new chat conversation
    
    Returns:
        NewConversationResponse with conversation_id and session_id
    """
    try:
        # Create conversation in database
        conversation_id = chatbot_repository.save_conversation(patient_id=None)
        
        if not conversation_id:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
        
        # Get the conversation details to return session_id
        conversation = chatbot_repository.get_conversation(conversation_id)
        
        logger.info(f"New conversation created: ID={conversation_id}")
        
        return NewConversationResponse(
            conversation_id=conversation_id,
            session_id=conversation['session_id']
        )
    
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-message", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """
    Send a message to the chatbot and get response with Gemini Function Calling
    
    Args:
        request: SendMessageRequest with conversation_id and message
    
    Returns:
        SendMessageResponse with bot response
    """
    try:
        conversation_id = request.conversation_id
        user_message = request.message
        
        # Validate input
        if not user_message or not user_message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create conversation if doesn't exist
        if not conversation_id:
            conversation_id = chatbot_repository.save_conversation(patient_id=None)
            if not conversation_id:
                raise HTTPException(status_code=500, detail="Failed to create conversation")
        
        # Get conversation history for context
        history_messages = chatbot_repository.get_conversation_messages(conversation_id)
        history_for_gemini = [
            {
                "message_text": msg.get("message_text"),
                "sender_type": msg.get("sender_type")
            }
            for msg in (history_messages or [])
        ]
        
        # Save user message
        chatbot_repository.save_message(
            conversation_id=conversation_id,
            sender_type='user',
            message_text=user_message
        )
        
        # Process message with Gemini Function Calling
        bot_response, tool_used, tool_response = process_user_message(
            user_message=user_message,
            conversation_history=history_for_gemini
        )
        
        # Save bot response
        chatbot_repository.save_message(
            conversation_id=conversation_id,
            sender_type='bot',
            message_text=bot_response,
            tool_used=tool_used,
            tool_response=tool_response
        )
        
        logger.info(f"Message processed: Conversation={conversation_id}, Tool={tool_used}")
        
        # Extract booking data ONLY if user explicitly wants to book (has keywords like "muốn đặt", "chọn", "lựa chọn")
        booking_data = None
        user_msg_lower = user_message.lower()
        confirmation_keywords = ['đúng rồi', 'vâng', 'được', 'ok', 'ừ', 'chắc chắn', 'xác nhận', 'chấp thuận']
        has_booking_intent = any(keyword in user_msg_lower for keyword in ['muốn đặt', 'muốn chọn', 'chọn', 'lựa chọn', 'tôi chọn', 'tôi muốn', '7-9', '09:00', '13:00', '15:00', '7:00', '9:00', '11:00'])
        is_confirmation = any(keyword in user_msg_lower for keyword in confirmation_keywords)
        
        # Extract booking data from check_available_slots tool response
        if tool_used == 'check_available_slots' and tool_response and has_booking_intent:
            try:
                import json
                from DataAccessLayer.chatbot_db import get_db_connection
                
                tool_result = json.loads(tool_response)
                logger.info(f"[BOOKING] Tool response received: {str(tool_result)[:100]}")
                
                if tool_result.get('success') and tool_result.get('availability'):
                    # Find first available slot matching user's choice
                    specialty_id = tool_result.get('specialty_id')
                    for day_info in tool_result['availability']:
                        for slot_info in day_info.get('slots', []):
                            if slot_info.get('available') and slot_info.get('available_doctors'):
                                doctor_name = slot_info['available_doctors'][0] if slot_info['available_doctors'] else ''
                                
                                # Convert doctor name to ID
                                doctor_id = None
                                if doctor_name:
                                    try:
                                        conn = get_db_connection()
                                        cursor = conn.cursor()
                                        cursor.execute("SELECT doctor_id FROM DOCTORS WHERE full_name LIKE ?", (f"%{doctor_name}%",))
                                        result = cursor.fetchone()
                                        if result:
                                            doctor_id = result[0]
                                        cursor.close()
                                        conn.close()
                                    except Exception as db_err:
                                        logger.debug(f"Could not convert doctor name to ID: {str(db_err)}")
                                
                                booking_data = {
                                    'specialty_id': specialty_id,
                                    'specialty': tool_result.get('specialty_name', ''),
                                    'doctor_id': doctor_id,
                                    'doctor': doctor_name,
                                    'date': day_info.get('date', ''),
                                    'time': slot_info.get('slot_name', '')
                                }
                                
                                logger.info(f"[BOOKING] Extracted booking data: {booking_data}")
                                
                                # Save booking context to database for later retrieval
                                chatbot_repository.save_message(
                                    conversation_id=conversation_id,
                                    sender_type='system',
                                    message_text=json.dumps(booking_data),
                                    tool_used='booking_context'
                                )
                                break
                        if booking_data:
                            break
            except Exception as e:
                logger.warning(f"[BOOKING] Could not extract booking data: {str(e)}")
        
        # If user is confirming, try to retrieve booking data from conversation history
        elif is_confirmation:
            try:
                import json
                # Look for previous booking context in message history
                all_messages = chatbot_repository.get_conversation_messages(conversation_id)
                for msg in reversed(all_messages or []):
                    if msg.get('tool_used') == 'booking_context':
                        booking_data = json.loads(msg.get('message_text', '{}'))
                        logger.info(f"[BOOKING] Retrieved booking context from history: {booking_data}")
                        break
            except Exception as e:
                logger.warning(f"[BOOKING] Could not retrieve booking context: {str(e)}")
        
        logger.info(f"[BOOKING] Final booking_data: {booking_data}")
        
        return SendMessageResponse(
            conversation_id=conversation_id,
            response=bot_response,
            tool_used=tool_used,
            tool_response=tool_response,
            booking_data=booking_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: int):
    """
    Get message history for a conversation
    
    Args:
        conversation_id: ID of the conversation
    
    Returns:
        ConversationHistoryResponse with all messages
    """
    try:
        messages = chatbot_repository.get_conversation_messages(conversation_id)
        
        if messages is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"Retrieved history for conversation {conversation_id}: {len(messages)} messages")
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HELPER FUNCTIONS
# ============================================

def process_user_message(user_message: str, conversation_history: list = None) -> tuple:
    """
    Process user message using Gemini Function Calling
    
    Args:
        user_message: User's input message
        conversation_history: Previous messages for context
    
    Returns:
        Tuple of (bot_response, tool_used, tool_response)
    """
    try:
        # Get Gemini service
        chatbot_service = get_chatbot_service()
        
        # Process message with Gemini
        response_text, tool_used, tool_response = chatbot_service.process_message(
            user_message=user_message,
            conversation_history=conversation_history or []
        )
        
        logger.info(f"[GEMINI] Response: {response_text[:80]}... Tool: {tool_used}")
        
        return response_text, tool_used, tool_response
    
    except Exception as e:
        logger.error(f"Error in process_user_message: {str(e)}")
        return f"Xin lỗi, tôi gặp sự cố: {str(e)}", None, None
