"""
🧪 TEST TOOLS - Kiểm tra các tools hoạt động ổn không

Test từng tool một:
1. get_specialty_for_symptoms
2. check_available_slots
3. search_medicines
4. get_consultation_guide
5. get_doctors_by_specialty
"""

import json
import sys
from config import GEMINI_API_KEY

print("[OK] Config loaded successfully!")
print(f"[OK] GEMINI_API_KEY: {GEMINI_API_KEY[:20]}...")

print("\n" + "="*70)
print("BẮT ĐẦU TEST TOOLS")
print("="*70 + "\n")

from routers.chatbot.tool_handlers import (
    handle_get_specialty_for_symptoms,
    handle_check_available_slots,
    handle_search_medicines,
    handle_get_consultation_guide,
    handle_get_doctors_by_specialty,
    process_tool_call
)

# ============================================
# TEST 1: get_specialty_for_symptoms
# ============================================

print("[1/5] Testing: handle_get_specialty_for_symptoms('headache')")
print("-" * 70)

result_1 = handle_get_specialty_for_symptoms(symptoms_text="headache")

print(f"✅ Status: {result_1.get('success')}")
print(f"📊 Specialties found: {len(result_1.get('specialties', []))}")
if result_1.get('specialties'):
    for i, spec in enumerate(result_1.get('specialties', [])[:3], 1):
        print(f"   {i}. {spec.get('specialty_name')} (ID: {spec.get('specialty_id')}, Doctors: {spec.get('doctors_count')})")
else:
    print(f"⚠️  Message: {result_1.get('message')}")

print()

# ============================================
# TEST 2: check_available_slots
# ============================================

print("[2/5] Testing: handle_check_available_slots(specialty_id=1)")
print("-" * 70)

result_2 = handle_check_available_slots(specialty_id=1, date=None, doctor_id=None)

print(f"✅ Status: {result_2.get('success')}")
print(f"📊 Slots found: {len(result_2.get('slots', []))}")
if result_2.get('slots'):
    for i, slot in enumerate(result_2.get('slots', [])[:3], 1):
        print(f"   {i}. {slot.get('doctor_name')} - {slot.get('slot_datetime')} (Price: {slot.get('price'):,} VND)")
else:
    print(f"⚠️  Message: {result_2.get('message')}")

print()

# ============================================
# TEST 3: search_medicines
# ============================================

print("[3/5] Testing: handle_search_medicines('vitamin')")
print("-" * 70)

result_3 = handle_search_medicines(search_term="vitamin")

print(f"✅ Status: {result_3.get('success')}")
print(f"📊 Medicines found: {len(result_3.get('medicines', []))}")
if result_3.get('medicines'):
    for i, med in enumerate(result_3.get('medicines', [])[:3], 1):
        print(f"   {i}. {med.get('name')} - {med.get('purpose', 'N/A')}")
else:
    print(f"⚠️  Message: {result_3.get('message')}")

print()

# ============================================
# TEST 4: get_consultation_guide
# ============================================

print("[4/5] Testing: handle_get_consultation_guide(specialty_id=1)")
print("-" * 70)

result_4 = handle_get_consultation_guide(specialty_id=1)

print(f"✅ Status: {result_4.get('success')}")
if result_4.get('guide'):
    guide = result_4.get('guide')
    print(f"📋 Title: {guide.get('title')}")
    print(f"📝 Content: {guide.get('content')[:100]}..." if guide.get('content') else "")
    print(f"🎒 Items to bring: {guide.get('items_to_bring')[:50]}..." if guide.get('items_to_bring') else "")
else:
    print(f"⚠️  Message: {result_4.get('message')}")

print()

# ============================================
# TEST 5: get_doctors_by_specialty
# ============================================

print("[5/5] Testing: handle_get_doctors_by_specialty(specialty_id=1)")
print("-" * 70)

result_5 = handle_get_doctors_by_specialty(specialty_id=1, doctor_name=None)

print(f"✅ Status: {result_5.get('success')}")
print(f"📊 Doctors found: {len(result_5.get('doctors', []))}")
if result_5.get('doctors'):
    for i, doc in enumerate(result_5.get('doctors', [])[:3], 1):
        print(f"   {i}. {doc.get('name')} - {doc.get('qualifications')}")
else:
    print(f"⚠️  Message: {result_5.get('message')}")

print()

# ============================================
# TEST 6: process_tool_call (main processor)
# ============================================

print("[BONUS] Testing: process_tool_call() - Main processor")
print("-" * 70)

tool_call_1 = process_tool_call(
    tool_name="get_specialty_for_symptoms",
    tool_args={"symptoms_text": "đau lưng"}
)

print(f"✅ Tool call 'get_specialty_for_symptoms' result: {tool_call_1.get('success')}")
if tool_call_1.get('specialties'):
    print(f"   Found {len(tool_call_1.get('specialties'))} specialties")

print()

tool_call_2 = process_tool_call(
    tool_name="check_available_slots",
    tool_args={"specialty_id": 1, "date": None}
)

print(f"✅ Tool call 'check_available_slots' result: {tool_call_2.get('success')}")
if tool_call_2.get('slots'):
    print(f"   Found {len(tool_call_2.get('slots'))} slots")

print()

# ============================================
# SUMMARY
# ============================================

print("="*70)
print("✅ ✅ ✅ TẤT CẢ TESTS HOÀN THÀNH ✅ ✅ ✅")
print("="*70)

test_results = {
    "Test 1 (get_specialty_for_symptoms)": result_1.get('success'),
    "Test 2 (check_available_slots)": result_2.get('success'),
    "Test 3 (search_medicines)": result_3.get('success'),
    "Test 4 (get_consultation_guide)": result_4.get('success'),
    "Test 5 (get_doctors_by_specialty)": result_5.get('success'),
}

print("\n📊 KẾT QUẢ TỔNG QUÁT:")
passed = sum(1 for v in test_results.values() if v)
total = len(test_results)

for test_name, status in test_results.items():
    status_icon = "✅" if status else "❌"
    print(f"  {status_icon} {test_name}: {'PASS' if status else 'FAIL'}")

print(f"\n🎯 TỔNG: {passed}/{total} tests passed")

if passed == total:
    print("\n🚀 Tất cả tools đều hoạt động ổn! Sẵn sàng cho BƯỚC 7 (Chatbot Service Update)")
else:
    print(f"\n⚠️  {total - passed} test(s) failed. Cần debug!")
