
import datetime
from DataAccessLayer import data_access
from sqlalchemy.orm import Session

def seed_database():
    db: Session = next(data_access.get_db())
    print("Bắt đầu khởi tạo dữ liệu mẫu...")

    # --- Khởi tạo Bệnh nhân ---
    patient_phone = '0912345678'
    patient_pass = 'benhnhanA'
    patient = data_access.get_patient_by_phone(db, patient_phone)
    if patient:
        print(f"Bệnh nhân với SĐT {patient_phone} đã tồn tại. Cập nhật mật khẩu...")
        data_access.update_patient_password(db, patient.PatientId, patient_pass)
    else:
        print(f"Tạo mới bệnh nhân với SĐT {patient_phone}...")
        patient_data = {
            "FullName": "Nguyễn Văn An",
            "Email": "an.nguyen@example.com",
            "Phone": patient_phone,
            "birth_date": datetime.date(1990, 1, 15),
            "address": "123 Đường Láng, Hà Nội",
            "Password": patient_pass
        }
        data_access.create_patient(db, patient_data)

    # --- Khởi tạo Bác sĩ ---
    doctor_phone = '0987654321'
    doctor_pass = 'bacsiB'
    doctor = data_access.get_doctor_by_phone(db, doctor_phone)
    if doctor:
        print(f"Bác sĩ với SĐT {doctor_phone} đã tồn tại. Cập nhật mật khẩu...")
        data_access.update_doctor_password(db, doctor.DoctorId, doctor_pass)
    else:
        print(f"Tạo mới bác sĩ với SĐT {doctor_phone}...")
        # Bạn cần đảm bảo SpecialtyId=1 tồn tại trong bảng SPECIALTIES
        doctor_data = {
            "FullName": "Bác sĩ Trần Thị B",
            "Email": "bs.b@example.com",
            "Phone": doctor_phone,
            "SpecialtyId": 1, 
            "Qualifications": "Tiến sĩ, Bác sĩ Nội trú",
            "Password": doctor_pass
        }
        data_access.create_doctor(db, doctor_data)

    # --- Khởi tạo Admin ---
    admin_user = 'admin'
    admin_pass = 'admin123'
    admin = data_access.get_admin_by_username(db, admin_user)
    if admin:
        print(f"Admin với username '{admin_user}' đã tồn tại. Cập nhật mật khẩu...")
        data_access.update_admin_password(db, admin.AdminId, admin_pass)
    else:
        print(f"Tạo mới admin với username '{admin_user}'...")
        admin_data = {
            "Username": admin_user,
            "Email": "admin@benhvien.com",
            "Password": admin_pass
        }
        data_access.create_admin(db, admin_data)

    # --- Khởi tạo Dịch vụ ---
    print("Kiểm tra và tạo mới dịch vụ mẫu...")
    services_to_seed = [
        {"name": "Khám tổng quát", "description": "Kiểm tra sức khỏe tổng thể", "price": 200000.00, "is_active": True},
        {"name": "Xét nghiệm máu", "description": "Phân tích các chỉ số trong máu", "price": 150000.00, "is_active": True},
        {"name": "Chụp X-Quang", "description": "Chụp X-Quang các bộ phận cơ thể", "price": 300000.00, "is_active": True},
        {"name": "Siêu âm", "description": "Siêu âm chẩn đoán hình ảnh", "price": 250000.00, "is_active": True},
        {"name": "Tư vấn dinh dưỡng", "description": "Tư vấn chế độ ăn uống khoa học", "price": 100000.00, "is_active": False},
    ]

    for service_data in services_to_seed:
        existing_service = db.query(data_access.Service).filter(data_access.Service.name == service_data["name"]).first()
        if not existing_service:
            db_service = data_access.Service(**service_data)
            db.add(db_service)
            db.commit()
            db.refresh(db_service)
            print(f"Đã thêm dịch vụ: {db_service.name}")
        else:
            print(f"Dịch vụ '{service_data['name']}' đã tồn tại.")

    print("Hoàn tất khởi tạo dữ liệu!")
    db.close()

if __name__ == "__main__":
    seed_database()
