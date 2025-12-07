"""
Test Chatbot API Endpoints
"""
import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

import asyncio
import json
from routers.chatbot.chatbot_router import (
    create_new_conversation,
    send_message,
    SendMessageRequest
)

async def test_chatbot_api():
    """Test the chatbot API endpoints"""
    
    print("\n" + "="*70)
    print("BƯỚC 9: TESTING CHATBOT API ENDPOINTS")
    print("="*70)
    
    # TEST 1: Create new conversation
    print("\n[TEST 1] POST /api/chatbot/new-conversation")
    try:
        response = await create_new_conversation()
        print(f"✅ Conversation created:")
        print(f"   - Conversation ID: {response.conversation_id}")
        print(f"   - Session ID: {response.session_id}")
        conversation_id = response.conversation_id
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
    # TEST 2: Send message with symptom (should trigger Tool 1)
    print("\n[TEST 2] POST /api/chatbot/send-message - With symptom")
    try:
        request = SendMessageRequest(
            conversation_id=conversation_id,
            message="Tôi bị sốt từ 3 ngày"
        )
        response = await send_message(request)
        print(f"✅ Message processed:")
        print(f"   - Bot Response: {response.response[:100]}...")
        print(f"   - Tool Used: {response.tool_used}")
        if response.tool_response:
            print(f"   - Tool Response: {response.tool_response[:80]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # TEST 3: Send message for appointment (should trigger Tool 2)
    print("\n[TEST 3] POST /api/chatbot/send-message - Appointment request")
    try:
        request = SendMessageRequest(
            conversation_id=conversation_id,
            message="Tôi muốn đặt lịch khám"
        )
        response = await send_message(request)
        print(f"✅ Message processed:")
        print(f"   - Bot Response: {response.response[:100]}...")
        print(f"   - Tool Used: {response.tool_used}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # TEST 4: Send message about medicine (should trigger Tool 3)
    print("\n[TEST 4] POST /api/chatbot/send-message - Medicine search")
    try:
        request = SendMessageRequest(
            conversation_id=conversation_id,
            message="Thuốc aspirin có tác dụng gì?"
        )
        response = await send_message(request)
        print(f"✅ Message processed:")
        print(f"   - Bot Response: {response.response[:100]}...")
        print(f"   - Tool Used: {response.tool_used}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # TEST 5: Get conversation history
    print("\n[TEST 5] GET /api/chatbot/history/{conversation_id}")
    try:
        from routers.chatbot.chatbot_router import get_conversation_history
        response = await get_conversation_history(conversation_id)
        print(f"✅ History retrieved:")
        print(f"   - Conversation ID: {response.conversation_id}")
        print(f"   - Total Messages: {len(response.messages)}")
        for i, msg in enumerate(response.messages, 1):
            msg_type = "[USER]" if msg['sender_type'] == 'user' else "[BOT]"
            print(f"   {i}. {msg_type} {msg['message_text'][:60]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_chatbot_api())
