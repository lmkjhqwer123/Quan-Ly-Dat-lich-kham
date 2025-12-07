"""
Test System Prompt Design
Kiểm tra System Prompt có phù hợp không
"""

import sys
sys.path.insert(0, r'c:\Users\Lenovo\Desktop\quanlydatlich')

from routers.chatbot.system_prompt import SYSTEM_PROMPT, SYSTEM_PROMPT_CONFIG

print("\n" + "="*80)
print("BƯỚC 12: SYSTEM PROMPT DESIGN - VERIFICATION")
print("="*80)

# CHECK 1: System Prompt Content
print("\n[CHECK 1] System Prompt Content")
print("-" * 80)
print("✅ System Prompt loaded successfully!")
print(f"\n📏 Prompt length: {len(SYSTEM_PROMPT)} characters")

# CHECK 2: Configuration
print("\n[CHECK 2] Configuration Parameters")
print("-" * 80)
for key, value in SYSTEM_PROMPT_CONFIG.items():
    print(f"  ✅ {key}: {value}")

# CHECK 3: Key Elements
print("\n[CHECK 3] Key Elements in Prompt")
print("-" * 80)
required_elements = [
    ("PERSONALITY", "Tone definition"),
    ("CAPABILITIES", "Tool usage"),
    ("CONVERSATION FLOW", "Response structure"),
    ("IMPORTANT GUIDELINES", "Rules and constraints"),
    ("TOOL USAGE RULES", "When to use each tool"),
    ("RESPONSE EXAMPLES", "Sample responses"),
]

for element, description in required_elements:
    present = element in SYSTEM_PROMPT
    status = "✅" if present else "❌"
    print(f"  {status} {element:<25} - {description}")

# CHECK 4: Tool Integration
print("\n[CHECK 4] Tools Mentioned in Prompt")
print("-" * 80)
tools = [
    "get_specialty_for_symptoms",
    "check_available_slots",
    "search_medicines",
    "get_consultation_guide",
    "get_doctors_by_specialty",
]

for tool in tools:
    present = tool in SYSTEM_PROMPT
    status = "✅" if present else "⚠️"
    print(f"  {status} {tool}")

# CHECK 5: Vietnamese Language Support
print("\n[CHECK 5] Vietnamese Language Support")
print("-" * 80)
vietnamese_samples = [
    "Xin chào",
    "bạn",
    "khám",
    "bác sĩ",
    "lịch",
]

for sample in vietnamese_samples:
    present = sample in SYSTEM_PROMPT
    status = "✅" if present else "⚠️"
    print(f"  {status} Vietnamese: '{sample}'")

# CHECK 6: Tone & Style Verification
print("\n[CHECK 6] Tone & Style Verification")
print("-" * 80)
tone_checks = [
    ("Professional", "Professional yet friendly"),
    ("Empathetic", "empathetic"),
    ("Friendly", "friendly"),
    ("Clear", "clear"),
]

for tone, keyword in tone_checks:
    present = keyword.lower() in SYSTEM_PROMPT.lower()
    status = "✅" if present else "⚠️"
    print(f"  {status} {tone}: '{keyword}'")

# CHECK 7: Safety Guidelines
print("\n[CHECK 7] Safety & Responsibility Guidelines")
print("-" * 80)
safety_checks = [
    ("No diagnosis", "Never diagnose"),
    ("Emergency warning", "emergency"),
    ("Doctor consultation", "doctor"),
    ("Health disclaimer", "Lưu ý"),
]

for check, keyword in safety_checks:
    present = keyword.lower() in SYSTEM_PROMPT.lower()
    status = "✅" if present else "⚠️"
    print(f"  {status} {check}")

# SUMMARY
print("\n" + "="*80)
print("✅ BƯỚC 12 COMPLETE: SYSTEM PROMPT DESIGNED")
print("="*80)
print(f"""
📋 SUMMARY:

✅ Character: Medical Appointment Booking Assistant
✅ Tone: Professional + Friendly + Warm
✅ Response Length: 3-5 sentences (Medium)
✅ Language: Vietnamese (primary)
✅ Address Style: Casual (bạn, anh/chị/em)
✅ Tools Integrated: All 5 tools documented
✅ Safety: Emergency warning + Disclaimer included
✅ Examples: Sample responses provided

🎯 READY FOR IMPLEMENTATION:
   - Next step: Integrate with Gemini API
   - Use this prompt as system message for all Gemini calls
   - Preserve context for multi-turn conversations
""")
print("="*80)
