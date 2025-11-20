
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

    # --- Khởi tạo Chuyên khoa (nếu chưa có) ---
    specialty_name = "Nội Tổng Quát"
    specialty = db.query(data_access.Specialty).filter(data_access.Specialty.Name == specialty_name).first()
    if not specialty:
        specialty_data = {"Name": specialty_name, "description": "Chuyên khoa khám và điều trị các bệnh lý nội khoa tổng quát."}
        specialty = data_access.create_specialty(db, specialty_data)
        print(f"Đã thêm chuyên khoa: {specialty.Name}")
    else:
        print(f"Chuyên khoa '{specialty_name}' đã tồn tại.")

    # Lấy lại các đối tượng đã tạo để đảm bảo chúng có ID
    patient = data_access.get_patient_by_phone(db, patient_phone)
    doctor = data_access.get_doctor_by_phone(db, doctor_phone)
    service1 = db.query(data_access.Service).filter(data_access.Service.name == "Khám tổng quát").first()
    service2 = db.query(data_access.Service).filter(data_access.Service.name == "Xét nghiệm máu").first()

    # --- Khởi tạo Lịch hẹn và Dịch vụ cho lịch hẹn ---
    if patient and doctor and specialty and service1 and service2:
        print("Kiểm tra và tạo mới lịch hẹn mẫu...")
        # Tạo lịch hẹn 1
        appointment_data_1 = {
            "PatientId": patient.PatientId,
            "DoctorId": doctor.DoctorId,
            "SpecialtyId": specialty.SpecialtyId,
            "AppointmentDatetime": datetime.datetime.now() + datetime.timedelta(days=7, hours=10),
            "Symptoms": "Đau đầu, sốt nhẹ",
            "Status": "pending",
            "Services": [
                {"service_id": service1.service_id, "quantity": 1, "notes": "Kiểm tra tổng quát"},
                {"service_id": service2.service_id, "quantity": 1, "notes": "Xét nghiệm máu cơ bản"}
            ]
        }
        existing_appointment_1 = db.query(data_access.Appointment).filter(
            data_access.Appointment.PatientId == patient.PatientId,
            data_access.Appointment.DoctorId == doctor.DoctorId,
            data_access.Appointment.AppointmentDatetime == appointment_data_1["AppointmentDatetime"]
        ).first()

        if not existing_appointment_1:
            appointment_1 = data_access.create_appointment(db, appointment_data_1)
            print(f"Đã tạo lịch hẹn {appointment_1.AppointmentId} với dịch vụ.")
        else:
            print(f"Lịch hẹn 1 đã tồn tại: {existing_appointment_1.AppointmentId}")

        # Tạo lịch hẹn 2 (ví dụ thêm)
        appointment_data_2 = {
            "PatientId": patient.PatientId,
            "DoctorId": doctor.DoctorId,
            "SpecialtyId": specialty.SpecialtyId,
            "AppointmentDatetime": datetime.datetime.now() + datetime.timedelta(days=14, hours=14),
            "Symptoms": "Kiểm tra định kỳ",
            "Status": "confirmed",
            "Services": [
                {"service_id": service1.service_id, "quantity": 1, "notes": "Kiểm tra tổng quát"}
            ]
        }
        existing_appointment_2 = db.query(data_access.Appointment).filter(
            data_access.Appointment.PatientId == patient.PatientId,
            data_access.Appointment.DoctorId == doctor.DoctorId,
            data_access.Appointment.AppointmentDatetime == appointment_data_2["AppointmentDatetime"]
        ).first()

        if not existing_appointment_2:
            appointment_2 = data_access.create_appointment(db, appointment_data_2)
            print(f"Đã tạo lịch hẹn {appointment_2.AppointmentId} với dịch vụ.")
        else:
            print(f"Lịch hẹn 2 đã tồn tại: {existing_appointment_2.AppointmentId}")
    else:
        print("Không thể tạo lịch hẹn mẫu vì thiếu thông tin bệnh nhân, bác sĩ, chuyên khoa hoặc dịch vụ.")

    print("Hoàn tất khởi tạo dữ liệu!")
    db.close()

if __name__ == "__main__":
    seed_database()
