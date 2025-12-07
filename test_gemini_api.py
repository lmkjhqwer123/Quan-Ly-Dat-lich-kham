"""
Test Gemini API Key
Script để kiểm tra xem API Key có hoạt động không
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

# Lấy API Key
api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("🔍 TESTING GEMINI API KEY")
print("=" * 60)

if not api_key:
    print("❌ GEMINI_API_KEY không được tìm thấy trong .env file!")
    exit(1)

print(f"✅ API Key tìm thấy: {api_key[:20]}...{api_key[-10:]}")

# Configure Gemini
genai.configure(api_key=api_key)

try:
    # Test 1: List available models
    print("\n🧪 Test 1: List available models...")
    models = genai.list_models()
    print(f"✅ Tìm thấy {len(list(models))} models")
    
    # Test 2: Simple message
    print("\n🧪 Test 2: Gửi simple message...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Xin chào, bạn tên gì?")
    print(f"✅ Response: {response.text[:100]}...")
    
    # Test 3: Test với system prompt
    print("\n🧪 Test 3: Test với system prompt...")
    chatbot_model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction="Bạn là một chatbot Y tế thông minh"
    )
    response = chatbot_model.generate_content("Tôi đau đầu")
    print(f"✅ Response: {response.text[:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ ✅ ✅ TẤT CẢ TESTS THÀNH CÔNG! ✅ ✅ ✅")
    print("=" * 60)
    print("\n🎉 API Key của bạn hoạt động bình thường!")
    print("👉 Bây giờ bạn có thể bắt đầu sử dụng Chatbot Service")

except Exception as e:
    print(f"\n❌ LỖI: {str(e)}")
    print("\n🔧 Kiểm tra lại:")
    print("  1. Đảm bảo API Key đúng")
    print("  2. Kiểm tra internet connection")
    print("  3. API Key có bị expired không")
    exit(1)
