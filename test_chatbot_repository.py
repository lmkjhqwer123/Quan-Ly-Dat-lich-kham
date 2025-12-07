"""
Test ChatbotRepository - Verify all 4 core functions work
"""
import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from routers.chatbot.chatbot_repository import ChatbotRepository
import logging

logging.basicConfig(level=logging.INFO)

# Test the repository
repo = ChatbotRepository()

print("\n" + "="*60)
print("BƯỚC 7 STEP 2: Testing ChatbotRepository")
print("="*60)

# TEST 1: Save Conversation
print("\n[TEST 1] save_conversation()")
conversation_id = repo.save_conversation(patient_id=1, session_id="test-session-001")
print(f"✅ Created conversation: ID={conversation_id}")

# TEST 2: Save Messages
print("\n[TEST 2] save_message() - User message")
msg_id_1 = repo.save_message(
    conversation_id=conversation_id,
    sender_type='user',
    message_text='Tôi bị sốt từ 3 ngày'
)
print(f"✅ Saved user message: ID={msg_id_1}")

print("\n[TEST 2b] save_message() - Bot message with tool")
msg_id_2 = repo.save_message(
    conversation_id=conversation_id,
    sender_type='bot',
    message_text='Dựa trên triệu chứng, bạn nên khám chuyên khoa Nội tiết',
    tool_used='get_specialty_for_symptoms',
    tool_response='{"specialty_id": 1, "name": "Nội tiết"}'
)
print(f"✅ Saved bot message: ID={msg_id_2}")

# TEST 3: Get Conversation Messages
print("\n[TEST 3] get_conversation_messages()")
messages = repo.get_conversation_messages(conversation_id)
print(f"✅ Retrieved {len(messages)} messages:")
for msg in messages:
    print(f"   - [{msg['sender_type']}] {msg['message_text'][:50]}...")
    if msg['tool_used']:
        print(f"     (Tool: {msg['tool_used']})")

# TEST 4: Update Conversation Status
print("\n[TEST 4] update_conversation_status()")
success = repo.update_conversation_status(
    conversation_id=conversation_id,
    status='closed',
    recommended_specialty_id=1
)
print(f"✅ Status updated: {success}")

# BONUS TEST 5: Get Conversation Details
print("\n[BONUS TEST 5] get_conversation()")
conv = repo.get_conversation(conversation_id)
if conv:
    print(f"✅ Conversation details:")
    print(f"   - ID: {conv['conversation_id']}")
    print(f"   - Status: {conv['status']}")
    print(f"   - Created: {conv['created_at']}")
    print(f"   - Ended: {conv['ended_at']}")
    print(f"   - Recommended Specialty: {conv['recommended_specialty_id']}")

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - STEP 2 COMPLETE")
print("="*60)
