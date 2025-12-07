"""
Simple Test for Gemini API Key
Kiểm tra xem API Key có hoạt động không
"""

import os
from dotenv import load_dotenv

# Bước 1: Load .env
print("=" * 70)
print("BƯỚC 1: ĐỌC FILE .ENV")
print("=" * 70)

load_dotenv()

# Bước 2: Lấy API Key
print("\nBƯỚC 2: LẤY API KEY TỪ .ENV")
print("-" * 70)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ KHÔNG TÌM THẤY GEMINI_API_KEY trong .env file!")
    print("\nVui lòng kiểm tra file .env có dòng:")
    print('GEMINI_API_KEY="AIzaSyAaqMCEigmbZ-NJzAHAe3bvfJxTPCiD5IE"')
    exit(1)

print(f"✅ API Key tìm thấy!")
print(f"   Độ dài: {len(api_key)} ký tự")
print(f"   Bắt đầu: {api_key[:10]}...")
print(f"   Kết thúc: ...{api_key[-10:]}")

# Bước 3: Test import google.generativeai
print("\nBƯỚC 3: TEST IMPORT GOOGLE GENERATIVEAI")
print("-" * 70)

try:
    import google.generativeai as genai
    print("✅ Google Generative AI library imported successfully!")
except ImportError as e:
    print(f"❌ LỖI: {e}")
    print("\n💡 FIX: Cài đặt library bằng lệnh:")
    print("   pip install google-generativeai")
    exit(1)

# Bước 4: Configure Gemini
print("\nBƯỚC 4: CẤU HÌNH GEMINI API")
print("-" * 70)

try:
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully!")
except Exception as e:
    print(f"❌ LỖI: {e}")
    exit(1)

# Bước 5: Test gửi message đơn giản
print("\nBƯỚC 5: TEST GỬI MESSAGE SIMPLE")
print("-" * 70)

try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("📤 Gửi message: 'Xin chào'")
    
    response = model.generate_content("Xin chào")
    
    print("✅ Nhận response thành công!")
    print(f"\n💬 Response:\n{response.text}\n")

except Exception as e:
    print(f"❌ LỖI: {e}")
    print("\n💡 Kiểm tra:")
    print("  - API Key có đúng không?")
    print("  - Có internet connection không?")
    print("  - API Key có bị expire không?")
    exit(1)

# Bước 6: Test với chatbot Y tế
print("\nBƯỚC 6: TEST CHATBOT Y TẾ")
print("-" * 70)

try:
    chatbot_model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction="Bạn là một chatbot Y tế chuyên nghiệp"
    )
    
    print("📤 Gửi message: 'Tôi đau đầu và chóng mặt'")
    
    response = chatbot_model.generate_content("Tôi đau đầu và chóng mặt")
    
    print("✅ Chatbot response thành công!")
    print(f"\n💬 Response:\n{response.text}\n")

except Exception as e:
    print(f"❌ LỖI: {e}")
    exit(1)

# Bước 7: Kết luận
print("=" * 70)
print("✅ ✅ ✅ TẤT CẢ TESTS THÀNH CÔNG! ✅ ✅ ✅")
print("=" * 70)
print("\n🎉 API KEY CỦA BẠN HOẠT ĐỘNG BÌNH THƯỜNG!")
print("\n👉 Bây giờ bạn có thể:")
print("   1. Tạo các Tools cho Chatbot")
print("   2. Xây dựng Database Module")
print("   3. Tích hợp vào Frontend")
print("\n" + "=" * 70)
