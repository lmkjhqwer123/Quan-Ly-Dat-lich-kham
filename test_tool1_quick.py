"""
Quick test Tool 1 sau khi thêm dữ liệu
"""

import sys
sys.path.insert(0, 'c:\\Users\\Lenovo\\Desktop\\quanlydatlich')

from routers.chatbot.tool_handlers import handle_get_specialty_for_symptoms
import json

print("[*] Testing handle_get_specialty_for_symptoms with database data...")
print()

# Test 1: Với keyword match
result = handle_get_specialty_for_symptoms(symptoms_text="ho, sot")
print("Test 1: Search 'ho, sot'")
print(json.dumps(result, ensure_ascii=False, indent=2))
print()

# Test 2
result = handle_get_specialty_for_symptoms(symptoms_text="dau dau")
print("Test 2: Search 'dau dau'")
print(json.dumps(result, ensure_ascii=False, indent=2))
print()

# Test 3
result = handle_get_specialty_for_symptoms(symptoms_text="tim")
print("Test 3: Search 'tim'")
print(json.dumps(result, ensure_ascii=False, indent=2))
