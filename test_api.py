"""
Test script để kiểm tra API lịch sử đặt lịch khám
"""
import requests
import json

# Thay đổi token nếu cần
ACCESS_TOKEN = "your_access_token_here"
BASE_URL = "http://localhost:8000"

def test_appointment_history():
    """Test API /api/patients/me/appointments/history"""
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("=" * 60)
    print("TEST: Lịch sử đặt lịch khám")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/patients/me/appointments/history",
            headers=headers,
            timeout=10
        )
        
        print(f"\n✓ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Số lịch hẹn: {len(data)}")
            
            if data:
                print("\n📋 Chi tiết lịch hẹn:")
                for apt in data:
                    print(f"\n  - ID: {apt.get('AppointmentId')}")
                    print(f"    Khoa: {apt.get('SpecialtyName')}")
                    print(f"    Bác sĩ: {apt.get('DoctorName')}")
                    print(f"    Ngày giờ: {apt.get('AppointmentDatetime')}")
                    print(f"    Trạng thái: {apt.get('Status')}")
                    print(f"    Triệu chứng: {apt.get('Symptoms')}")
            else:
                print("⚠️  Không có lịch hẹn nào")
                
        else:
            print(f"✗ Lỗi: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Không thể kết nối tới server")
        print(f"  Đảm bảo API chạy tại {BASE_URL}")
    except Exception as e:
        print(f"✗ Lỗi: {str(e)}")

if __name__ == "__main__":
    print(f"\nServer: {BASE_URL}")
    print(f"Token: {ACCESS_TOKEN[:20]}...\n")
    
    if ACCESS_TOKEN == "your_access_token_here":
        print("⚠️  CẢNH BÁO: Chưa cấu hình ACCESS_TOKEN")
        print("   Vui lòng cập nhật token từ sessionStorage")
    else:
        test_appointment_history()
