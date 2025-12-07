"""
TEST: Quick Chatbot Prompts - Các câu hỏi thường gặp
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from routers.chatbot.chatbot_service import get_chatbot_service

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                TEST CHATBOT PROMPTS - QUICK VERSION                        ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

service = get_chatbot_service()

# Các prompt quan trọng để test
prompts = [
    ("Xin chào", "Greeting"),
    ("Tôi bị sốt, đau đầu", "Symptoms"),
    ("Aspirin là gì?", "Medicine"),
    ("Đặt lịch khám tim", "Appointment"),
]

print("\n📋 Testing Key Prompts:\n")

for prompt, category in prompts:
    print(f"➤ [{category}] {prompt}")
    print("-" * 70)
    
    try:
        response, tool, tool_resp = service.process_message(prompt)
        print(f"   Response: {response[:90]}...")
        if tool:
            print(f"   Tool: {tool}")
        else:
            print(f"   Tool: None (Direct response)")
    except Exception as e:
        print(f"   Error: {str(e)[:50]}")
    
    print()

print("✅ Quick test completed!")
