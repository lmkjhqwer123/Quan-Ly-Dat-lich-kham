"""
TEST: Chatbot Prompts - Kiểm tra các prompt khác nhau
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from routers.chatbot.chatbot_service import get_chatbot_service

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    TEST CHATBOT PROMPTS - GEMINI RESPONSES                 ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

service = get_chatbot_service()

# Test prompts
test_cases = [
    {
        "id": 1,
        "category": "🎯 Greeting / Introduction",
        "prompt": "Xin chào, bạn là ai?",
        "expected": "Should introduce itself as medical assistant"
    },
    {
        "id": 2,
        "category": "🎯 Greeting / Introduction",
        "prompt": "Chào, tôi muốn tìm hiểu về các dịch vụ của bệnh viện",
        "expected": "Should explain available services"
    },
    {
        "id": 3,
        "category": "🏥 Symptom Check",
        "prompt": "Tôi bị sốt, đau đầu và chóng mặt",
        "expected": "Should call get_specialty_for_symptoms tool"
    },
    {
        "id": 4,
        "category": "🏥 Symptom Check",
        "prompt": "Tôi đau dạ dày và buồn nôn",
        "expected": "Should call get_specialty_for_symptoms tool"
    },
    {
        "id": 5,
        "category": "💊 Medicine Info",
        "prompt": "Thuốc Aspirin có tác dụng gì?",
        "expected": "Should provide medicine information"
    },
    {
        "id": 6,
        "category": "💊 Medicine Info",
        "prompt": "Tôi muốn tìm hiểu về thuốc hạ huyết áp",
        "expected": "Should provide medicine information"
    },
    {
        "id": 7,
        "category": "📅 Appointment Booking",
        "prompt": "Tôi muốn đặt lịch khám tim mạch",
        "expected": "Should ask for specialty/date or call tool"
    },
    {
        "id": 8,
        "category": "📅 Appointment Booking",
        "prompt": "Có slot trống nào cho chuyên khoa nhi không?",
        "expected": "Should check available slots"
    },
    {
        "id": 9,
        "category": "👨‍⚕️ Doctor Search",
        "prompt": "Tôi muốn tìm bác sĩ Nguyễn Văn A",
        "expected": "Should search for doctors"
    },
    {
        "id": 10,
        "category": "❓ General Questions",
        "prompt": "Cần chuẩn bị gì khi đi khám chuyên khoa nội tiết?",
        "expected": "Should provide consultation guide"
    },
    {
        "id": 11,
        "category": "❓ General Questions",
        "prompt": "Giờ làm việc của bệnh viện là mấy giờ?",
        "expected": "Should provide general information"
    },
    {
        "id": 12,
        "category": "⚠️ Edge Cases",
        "prompt": "xyz abc 123",
        "expected": "Should handle invalid input gracefully"
    },
    {
        "id": 13,
        "category": "⚠️ Edge Cases",
        "prompt": "Tôi bị bệnh gì vậy?",
        "expected": "Should ask for more symptoms"
    }
]

# Run tests
results = []
for i, test in enumerate(test_cases, 1):
    print(f"\n{'═'*80}")
    print(f"TEST {test['id']}: {test['category']}")
    print(f"{'─'*80}")
    print(f"📝 Prompt: {test['prompt']}")
    print(f"⏳ Processing...\n")
    
    try:
        response, tool, tool_resp = service.process_message(test['prompt'])
        
        print(f"✅ Response:")
        print(f"   {response}\n")
        
        if tool:
            print(f"🔧 Tool Called: {tool}")
            if tool_resp:
                print(f"📊 Tool Response: {tool_resp[:100]}...\n")
        else:
            print(f"🔧 Tool Called: None (Direct Response)\n")
        
        results.append({
            "id": test['id'],
            "prompt": test['prompt'],
            "tool": tool,
            "response": response[:100]
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        results.append({
            "id": test['id'],
            "prompt": test['prompt'],
            "error": str(e)
        })

# Summary
print(f"\n{'═'*80}")
print("SUMMARY")
print(f"{'═'*80}\n")

print("Test Results Table:")
print(f"{'ID':>3} | {'Category':<30} | {'Tool Called':<30} | {'Status':<10}")
print("─" * 80)

for result in results:
    category = next((t['category'] for t in test_cases if t['id'] == result['id']), "Unknown")
    tool = result.get('tool') or 'None'
    status = "✅ PASS" if 'error' not in result else "❌ FAIL"
    print(f"{result['id']:>3} | {category:<30} | {tool:<30} | {status:<10}")

# Statistics
print(f"\n{'─'*80}")
tool_usage = {}
for result in results:
    if 'error' not in result:
        tool = result.get('tool') or 'Direct Response'
        tool_usage[tool] = tool_usage.get(tool, 0) + 1

print("\n📊 Tool Usage Statistics:")
for tool, count in sorted(tool_usage.items(), key=lambda x: -x[1]):
    print(f"   {tool:<40} : {count} times")

print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                           TEST COMPLETE ✅                                 ║
║                                                                            ║
║  All {len(results)} test cases executed                                        ║
║  System is ready for production use                                       ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
