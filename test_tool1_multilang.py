"""
Test Tool 1 - get_specialty_for_symptoms with Vietnamese (dấu/không dấu) + English
"""

from DataAccessLayer.chatbot_db import get_specialty_for_symptoms

print("=" * 80)
print("Testing Tool 1: get_specialty_for_symptoms")
print("Hỗ trợ: Tiếng Việt có dấu, Tiếng Việt không dấu, Tiếng Anh")
print("=" * 80)

test_cases = [
    # Vietnamese with accents (tiếng Việt có dấu)
    ("sốt", "Vietnamese: fever with accents"),
    ("đau đầu", "Vietnamese: headache with accents"),
    ("chóng mặt", "Vietnamese: dizziness with accents"),
    
    # Vietnamese without accents (tiếng Việt không dấu)
    ("sot", "Vietnamese: fever without accents"),
    ("dau dau", "Vietnamese: headache without accents"),
    ("chong mat", "Vietnamese: dizziness without accents"),
    
    # English
    ("fever", "English: fever"),
    ("headache", "English: headache"),
    ("dizziness", "English: dizziness"),
    ("breathing difficulty", "English: difficulty breathing"),
]

for search_term, description in test_cases:
    print(f"\n[Test] {description}")
    print(f"  Search term: '{search_term}'")
    
    result = get_specialty_for_symptoms(search_term)
    
    if result['success']:
        print(f"  ✅ Status: SUCCESS")
        print(f"  Found {len(result['specialties'])} specialties:")
        for spec in result['specialties']:
            print(f"    - {spec['specialty_name']} ({spec['specialty_id']}) - {spec['doctors_count']} doctors")
    else:
        print(f"  ❌ Status: NOT FOUND")
        print(f"  Message: {result['message']}")

print("\n" + "=" * 80)
print("✅ Test completed!")
print("=" * 80)
