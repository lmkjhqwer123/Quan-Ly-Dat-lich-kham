"""
═══════════════════════════════════════════════════════════════════════════════
  GUIDE: TEST CHATBOT THỰC TẾ
═══════════════════════════════════════════════════════════════════════════════
"""

guide = """

🚀 BƯỚC 1: KHỞI ĐỘNG FASTAPI SERVER
═══════════════════════════════════════════════════════════════════════════════

Mở Terminal PowerShell và chạy:

    cd c:\\Users\\Lenovo\\Desktop\\quanlydatlich
    python api.py

✅ Khi thấy dòng này, server đã khởi động:
    INFO:     Uvicorn running on http://127.0.0.1:8000


🌐 BƯỚC 2: MỞ FILE TEST HTML
═══════════════════════════════════════════════════════════════════════════════

File vừa tạo: c:\\Users\\Lenovo\\Desktop\\quanlydatlich\\test_chatbot.html

Cách mở:
    1. Mở Windows Explorer
    2. Điều hướng tới: c:\\Users\\Lenovo\\Desktop\\quanlydatlich
    3. Tìm file: test_chatbot.html
    4. Double-click để mở trong browser

Hoặc dùng lệnh:
    start test_chatbot.html


💬 BƯỚC 3: TEST CHATBOT WIDGET
═══════════════════════════════════════════════════════════════════════════════

Test Case 1: Greeting
    Input:    "Xin chào"
    Expected: Chatbot giới thiệu bản thân
    
Test Case 2: Symptom (CÓ THỂ TRIGGER TOOL)
    Input:    "Tôi bị đau bụng"
    Expected: Gợi ý chuyên khoa (ví dụ: Tiêu hóa)
    
Test Case 3: Medicine Info
    Input:    "Aspirin là gì?"
    Expected: Thông tin về Aspirin
    
Test Case 4: Appointment (CÓ THỂ TRIGGER TOOL)
    Input:    "Chuẩn bị gì khám Nội tiết?"
    Expected: Hướng dẫn chuẩn bị hoặc không tìm thấy

Test Case 5: Multi-turn
    Input:    "Tôi bị sốt 39 độ"
    (sau khi nhận response)
    Input:    "Có slot khám ngày mai không?"
    Expected: Chatbot hiểu context từ message trước


🔍 DEBUG TIPS
═══════════════════════════════════════════════════════════════════════════════

1. Xem Browser Console (F12 → Console)
   ✅ Thành công: "✅ Conversation created: <id>"
   ❌ Lỗi: Xem error message

2. Xem Network Requests (F12 → Network)
   - Chọn tab "XHR"
   - Gửi message
   - Xem request/response details

3. Xem Server Logs
   - Console chạy server sẽ in logs
   - Xem requests được nhận
   - Xem responses được gửi

4. Test API trực tiếp (với curl hoặc Postman)
   
   curl -X POST http://localhost:8000/api/chatbot/send-message \\
     -H "Content-Type: application/json" \\
     -d '{"conversation_id": 1, "message": "Xin chào"}'


✅ EXPECTED OUTPUT
═══════════════════════════════════════════════════════════════════════════════

Browser Console:
    ✅ Conversation created: 1
    ✅ Response: {"response": "...", "tool_used": null, ...}

Server Console:
    [INFO] Creating conversation for patient_id: None
    [INFO] Saving message: user -> "Tôi bị đau bụng"
    [INFO] Processing with Gemini...
    [INFO] Saving message: bot -> "Với triệu chứng đau bụng..."

Chatbot Widget:
    Bot: "Với triệu chứng đau bụng, bạn nên khám chuyên khoa Tiêu hóa..."
    [Tool indicator if tool was called]


⚠️ TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

❌ "Failed to fetch" / CORS Error
   → Server chưa chạy
   → Solution: Đảm bảo python api.py đang chạy

❌ "429 Quota exceeded"
   → Gemini API limit đạt
   → Solution: Chờ 1 phút rồi thử lại

❌ "Cannot find conversation"
   → Conversation ID không match
   → Solution: Refresh page để tạo conversation mới

❌ HTML không load được
   → Kiểm tra đường dẫn file
   → Solution: Dùng lệnh: start c:\\Users\\Lenovo\\Desktop\\quanlydatlich\\test_chatbot.html

❌ Message gửi nhưng không có response
   → Kiểm tra server logs
   → Solution: Xem Browser DevTools → Network → Response

❌ Chatbot widget không gọi tool
   → Gemini chọn không cần tool (thường là đúng)
   → Solution: Dùng prompt cụ thể hơn


📝 EXAMPLE PROMPTS ĐỂ TRIGGER TOOLS
═══════════════════════════════════════════════════════════════════════════════

Để gọi get_specialty_for_symptoms:
    "Triệu chứng sốt 40 độ, ho, khó thở - nên khám gì?"
    "Tôi bị đau bụng suốt 3 ngày"
    "Đau ngực, khó thở, hoa mắt"

Để gọi get_consultation_guide:
    "Chuẩn bị gì khi đi khám chuyên khoa Nội tiết?"
    "Cần mang giấy tờ gì đến bệnh viện?"

Để gọi check_available_slots:
    "Có slot khám nào ngày 30/12 không?"
    "Chuyên khoa Nhi có khám thứ 7 không?"

Để gọi search_medicines:
    "Thuốc huyết áp mới nhất là gì?"
    "Tìm thuốc chữa viêm dạ dày"

Để gọi get_doctors_by_specialty:
    "Tìm bác sĩ chuyên khoa Tim mạch"
    "Bác sĩ nào giỏi khám bệnh trẻ em?"


🎯 NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

Sau khi test thành công:
    1. ✅ Verify all 3 endpoints work
    2. ✅ Confirm messages được lưu vào database
    3. ✅ Check tool calling works when needed
    4. ✅ Verify conversation history maintained

Sau đó:
    1. Integrate chatbot vào main HTML application
    2. Test full end-to-end flow
    3. Prepare for PHASE 6 (Production)


════════════════════════════════════════════════════════════════════════════════
✅ READY TO TEST!
════════════════════════════════════════════════════════════════════════════════

Now:
1. Run: python api.py
2. Open: test_chatbot.html
3. Type: "Tôi bị đau bụng"
4. See Gemini response!

Let's go! 🚀
"""

print(guide)
