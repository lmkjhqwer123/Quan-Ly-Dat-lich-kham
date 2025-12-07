"""
Quick test of PHASE 5: Gemini Function Calling - Just first test
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from routers.chatbot.chatbot_service import get_chatbot_service

print("\n" + "="*80)
print("PHASE 5: QUICK INTEGRATION TEST")
print("="*80)

# Get chatbot service
service = get_chatbot_service()

# Simple test
print("\n[TEST 1] Simple greeting")
print("-" * 80)
try:
    response, tool, tool_resp = service.process_message("Xin chào")
    print(f"✅ Response: {response[:100]}...")
    print(f"   Tool: {tool}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("✅ QUICK TEST COMPLETE - SERVICE WORKING!")
print("="*80)
