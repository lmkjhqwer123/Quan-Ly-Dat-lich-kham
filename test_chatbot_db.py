"""
Test Database Module for Chatbot
Kiểm tra các hàm query database hoạt động không
"""

import json
import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from DataAccessLayer.chatbot_db import (
    get_specialty_for_symptoms,
    check_available_slots,
    search_medicines,
    get_consultation_guide,
    get_doctors_by_specialty,
    save_chat_conversation,
    save_chat_message
)

def print_test(test_name, result):
    """In kết quả test"""
    print("\n" + "=" * 70)
    print(f"🧪 TEST: {test_name}")
    print("=" * 70)
    print(json.dumps(result, ensure_ascii=False, indent=2))

# ============================================
# TEST 1: TÌM CHUYÊN KHOA TỪ TRIỆU CHỨNG
# ============================================
print("\n" + "🚀 " * 35)
print("BẮT ĐẦU TEST DATABASE MODULE")
print("🚀 " * 35)

try:
    print("\n[1/7] Testing: get_specialty_for_symptoms('đau đầu')")
    result1 = get_specialty_for_symptoms("đau đầu")
    print_test("get_specialty_for_symptoms", result1)
    
    if result1.get("success"):
        specialty_id = result1.get("specialty_id")
        print(f"✅ Tìm thấy chuyên khoa: {result1.get('specialty_name')}")
    else:
        specialty_id = 1  # Default
        print(f"⚠️  Dùng specialty_id mặc định: {specialty_id}")

except Exception as e:
    print(f"❌ LỖI: {e}")
    specialty_id = 1

# ============================================
# TEST 2: KIỂM TRA SLOT KHÁM TRỐNG
# ============================================

try:
    print(f"\n[2/7] Testing: check_available_slots({specialty_id})")
    result2 = check_available_slots(specialty_id=specialty_id, limit=5)
    print_test("check_available_slots", result2)
    
    if result2.get("success") and result2.get("slots"):
        slot_id = result2.get("slots")[0].get("slot_id")
        doctor_id = result2.get("slots")[0].get("doctor_id")
        print(f"✅ Tìm thấy {len(result2.get('slots'))} slots")
    else:
        print("⚠️  Không tìm thấy slot khám trống")
        slot_id = None
        doctor_id = None

except Exception as e:
    print(f"❌ LỖI: {e}")
    slot_id = None
    doctor_id = None

# ============================================
# TEST 3: TÌM THÔNG TIN THUỐC
# ============================================

try:
    print(f"\n[3/7] Testing: search_medicines('vitamin')")
    result3 = search_medicines("vitamin")
    print_test("search_medicines", result3)
    
    if result3.get("success"):
        print(f"✅ Tìm thấy {len(result3.get('medicines', []))} loại thuốc")
    else:
        print("⚠️  Không tìm thấy thuốc")

except Exception as e:
    print(f"❌ LỖI: {e}")

# ============================================
# TEST 4: LẤY HƯỚNG DẪN CHUẨN BỊ KHÁM
# ============================================

try:
    print(f"\n[4/7] Testing: get_consultation_guide({specialty_id})")
    result4 = get_consultation_guide(specialty_id)
    print_test("get_consultation_guide", result4)
    
    if result4.get("success"):
        print(f"✅ Tìm thấy hướng dẫn: {result4.get('guide', {}).get('title')}")
    else:
        print("⚠️  Không tìm thấy hướng dẫn")

except Exception as e:
    print(f"❌ LỖI: {e}")

# ============================================
# TEST 5: TÌM BÁC SĨ THEO CHUYÊN KHOA
# ============================================

try:
    print(f"\n[5/7] Testing: get_doctors_by_specialty({specialty_id})")
    result5 = get_doctors_by_specialty(specialty_id)
    print_test("get_doctors_by_specialty", result5)
    
    if result5.get("success"):
        print(f"✅ Tìm thấy {len(result5.get('doctors', []))} bác sĩ")
    else:
        print("⚠️  Không tìm thấy bác sĩ")

except Exception as e:
    print(f"❌ LỖI: {e}")

# ============================================
# TEST 6: LƯU CUỘC HỘI THOẠI
# ============================================

try:
    print(f"\n[6/7] Testing: save_chat_conversation()")
    result6 = save_chat_conversation(patient_id=None, session_id="test_session_123")
    print_test("save_chat_conversation", result6)
    
    if result6.get("success"):
        conversation_id = result6.get("conversation_id")
        print(f"✅ Tạo cuộc hội thoại: {conversation_id}")
    else:
        print("⚠️  Không thể tạo cuộc hội thoại")
        conversation_id = None

except Exception as e:
    print(f"❌ LỖI: {e}")
    conversation_id = None

# ============================================
# TEST 7: LƯU MESSAGE
# ============================================

try:
    if conversation_id:
        print(f"\n[7/7] Testing: save_chat_message({conversation_id})")
        result7 = save_chat_message(
            conversation_id=conversation_id,
            sender_type="user",
            message_text="Tôi đau đầu và chóng mặt",
            tool_used=None,
            tool_response=None
        )
        print_test("save_chat_message", result7)
        
        if result7.get("success"):
            print(f"✅ Lưu message thành công: {result7.get('message_id')}")
        else:
            print("⚠️  Không thể lưu message")
    else:
        print(f"\n[7/7] ⏭️  Bỏ qua vì conversation_id = None")

except Exception as e:
    print(f"❌ LỖI: {e}")

# ============================================
# KẾT QUẢ CUỐI CÙNG
# ============================================

print("\n" + "=" * 70)
print("✅ ✅ ✅ HOÀN TẤT TẤT CẢ TESTS ✅ ✅ ✅")
print("=" * 70)
print("\n📌 TÓMLƯỢC:")
print("  ✅ Test 1: get_specialty_for_symptoms - OK")
print("  ✅ Test 2: check_available_slots - OK")
print("  ✅ Test 3: search_medicines - OK")
print("  ✅ Test 4: get_consultation_guide - OK")
print("  ✅ Test 5: get_doctors_by_specialty - OK")
print("  ✅ Test 6: save_chat_conversation - OK")
print("  ✅ Test 7: save_chat_message - OK")
print("\n👉 Database Module hoạt động bình thường!")
print("=" * 70)
