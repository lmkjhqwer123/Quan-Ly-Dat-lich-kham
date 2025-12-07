"""
Test the exact get_specialty_for_symptoms function
"""

from DataAccessLayer.chatbot_db import get_specialty_for_symptoms

print("Test 1: 'đau đầu'")
result = get_specialty_for_symptoms('đau đầu')
print(f"Result: {result}")
print()

print("Test 2: 'headache'")
result = get_specialty_for_symptoms('headache')
print(f"Result: {result}")
print()

print("Test 3: 'dau dau'")
result = get_specialty_for_symptoms('dau dau')
print(f"Result: {result}")
print()

print("Test 4: 'chóng'")
result = get_specialty_for_symptoms('chóng')
print(f"Result: {result}")
print()

print("Test 5: 'ho'")
result = get_specialty_for_symptoms('ho')
print(f"Result: {result}")
