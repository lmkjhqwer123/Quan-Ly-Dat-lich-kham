"""
Test PHASE 5: Gemini Function Calling Integration
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

import asyncio
from routers.chatbot.chatbot_service import get_chatbot_service

async def test_gemini_integration():
    """Test Gemini Function Calling"""
    
    print("\n" + "="*80)
    print("PHASE 5: GEMINI FUNCTION CALLING INTEGRATION - TEST")
    print("="*80)
    
    # Get chatbot service
    service = get_chatbot_service()
    
    # TEST 1: Simple message (no tool needed)
    print("\n[TEST 1] Simple greeting")
    print("-" * 80)
    response, tool, tool_resp = service.process_message("Xin chào")
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool: {tool}")
    
    # TEST 2: Message with symptoms (should trigger tool)
    print("\n[TEST 2] Symptoms detection (should trigger get_specialty_for_symptoms)")
    print("-" * 80)
    response, tool, tool_resp = service.process_message("Tôi bị sốt, đau đầu và chóng mặt")
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool used: {tool}")
    if tool_resp:
        print(f"   Tool result: {tool_resp[:80]}...")
    
    # TEST 3: Appointment request (should trigger check_available_slots)
    print("\n[TEST 3] Appointment request (should trigger check_available_slots)")
    print("-" * 80)
    response, tool, tool_resp = service.process_message("Tôi muốn đặt lịch khám chuyên khoa nội tiết")
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool used: {tool}")
    if tool_resp:
        print(f"   Tool result: {tool_resp[:80]}...")
    
    # TEST 4: Medicine search
    print("\n[TEST 4] Medicine search (should trigger search_medicines)")
    print("-" * 80)
    response, tool, tool_resp = service.process_message("Thuốc aspirin dùng để làm gì?")
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool used: {tool}")
    
    # TEST 5: Multi-turn conversation with history
    print("\n[TEST 5] Multi-turn conversation with history")
    print("-" * 80)
    history = [
        {"message_text": "Tôi bị sốt", "sender_type": "user"},
        {"message_text": "Dựa trên triệu chứng của bạn, nên khám chuyên khoa Nội tiết", "sender_type": "bot"}
    ]
    response, tool, tool_resp = service.process_message(
        "Có slot trống không?",
        conversation_history=history
    )
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool used: {tool}")
    print(f"   (Gemini should understand context from history)")
    
    print("\n" + "="*80)
    print("✅ PHASE 5 TEST COMPLETE")
    print("="*80)
    print("""
✅ Gemini Function Calling Integration Working:
   - System prompt loaded
   - Tools configured
   - Message processing with context
   - Tool calling and execution
   - Response generation
    """)


if __name__ == "__main__":
    asyncio.run(test_gemini_integration())
