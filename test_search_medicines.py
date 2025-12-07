"""
Test search_medicines with Gemini API
"""

from DataAccessLayer.chatbot_db import search_medicines

print("=" * 70)
print("Testing search_medicines with Gemini API")
print("=" * 70)

# Test 1
print("\n[Test 1] Searching for 'aspirin'...")
result = search_medicines('aspirin')
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
if result['medicines']:
    print(f"Found {len(result['medicines'])} medicine(s):")
    for i, med in enumerate(result['medicines'][:2], 1):
        print(f"\n  Medicine {i}:")
        print(f"    Name: {med.get('name', 'N/A')}")
        print(f"    Usage: {med.get('usage', 'N/A')}")
        print(f"    Dosage: {med.get('dosage', 'N/A')}")
else:
    print("No medicines found")

# Test 2
print("\n\n[Test 2] Searching for 'hạ sốt' (fever reducing)...")
result = search_medicines('hạ sốt')
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
if result['medicines']:
    print(f"Found {len(result['medicines'])} medicine(s)")
else:
    print("No medicines found")

print("\n" + "=" * 70)
