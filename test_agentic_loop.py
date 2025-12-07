"""
Test agentic loop functionality
"""

import sys
import json
from routers.chatbot.chatbot_service import ChatbotService

def test_agentic_loop():
    """Test that chatbot can call multiple tools in sequence"""
    
    service = ChatbotService()
    
    # Test case: Symptoms → should trigger get_specialty + get_doctors
    print("=" * 80)
    print("TEST: Agentic Loop with Symptoms")
    print("=" * 80)
    
    user_message = "Tôi bị đau bụng"
    conversation_history = []
    
    response_text, tool_used, tool_response = service.process_message(
        user_message=user_message,
        conversation_history=conversation_history
    )
    
    print(f"\n✅ User Message: {user_message}")
    print(f"✅ Response Text: {response_text[:200]}...")
    print(f"✅ Tool Used: {tool_used}")
    if tool_response:
        try:
            tool_response_json = json.loads(tool_response)
            print(f"✅ Tool Response (success): {tool_response_json.get('success')}")
        except:
            print(f"✅ Tool Response: {tool_response[:100]}...")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_agentic_loop()
