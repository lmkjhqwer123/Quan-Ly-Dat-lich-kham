
from DataAccessLayer import data_access

# --- Auth Logic ---
def login_user(db, login_request: dict):
    user_info = None
    role = None

    if login_request.get("Phone"):
        patient = data_access.get_patient_by_phone(db, login_request["Phone"])
        if patient and data_access.verify_password(login_request["Password"], patient.PasswordHash):
            user_info = {"userId": patient.PatientId, "name": patient.FullName, "email": patient.Email}
            role = "Patient"
        else:
            doctor = data_access.get_doctor_by_phone(db, login_request["Phone"])
            if doctor and data_access.verify_password(login_request["Password"], doctor.PasswordHash):
                user_info = {"userId": doctor.DoctorId, "name": doctor.FullName, "email": doctor.Email}
                role = "Doctor"

    elif login_request.get("Username"):
        admin = data_access.get_admin_by_username(db, login_request["Username"])
        if admin and data_access.verify_password(login_request["Password"], admin.PasswordHash):
            user_info = {"userId": admin.AdminId, "name": admin.Username, "email": admin.Email}
            role = "Admin"

    if user_info:
        return {"role": role, **user_info}
    return None

def register_user(db, request: dict):
    role = request.get('role')
    user_data = request.get(f'{role}_data')

    if not user_data:
        return {"error": "Dữ liệu cho vai trò không hợp lệ."}

    email = user_data.get('Email')
    phone = user_data.get('Phone')

    # Kiểm tra xem email hoặc SĐT đã tồn tại trong cả hai bảng patient và doctor chưa
    if data_access.get_patient_by_email(db, email) or data_access.get_doctor_by_email(db, email):
        return {"error": f"Email '{email}' đã được sử dụng."}
    if data_access.get_patient_by_phone(db, phone) or data_access.get_doctor_by_phone(db, phone):
        return {"error": f"Số điện thoại '{phone}' đã được sử dụng."}

    if role == 'patient':
        new_patient = data_access.create_patient(db, user_data)
        return {"message": "Đăng ký bệnh nhân thành công!", "userId": new_patient.PatientId}
    
    elif role == 'doctor':
        # Cần kiểm tra xem SpecialtyId có tồn tại không (nếu cần)
        new_doctor = data_access.create_doctor(db, user_data)
        return {"message": "Đăng ký bác sĩ thành công!", "userId": new_doctor.DoctorId}

    return {"error": "Vai trò không được hỗ trợ."}

# --- Doctor Logic ---
def get_all_doctors_logic(db):
    doctors = data_access.get_all_doctors(db)
    return [
        {
            "DoctorId": d.DoctorId,
            "FullName": d.FullName,
            "Email": d.Email,
            "Phone": d.Phone,
            "SpecialtyId": d.SpecialtyId,
            "SpecialtyName": d.specialty.Name if d.specialty else None,
            "Qualifications": d.Qualifications
        } for d in doctors
    ]

def get_doctor_by_id_logic(db, doctor_id: int):
    doctor = data_access.get_doctor_by_id(db, doctor_id)
    if doctor:
        return {
            "DoctorId": doctor.DoctorId,
            "FullName": doctor.FullName,
            "Email": doctor.Email,
            "Phone": doctor.Phone,
            "SpecialtyId": doctor.SpecialtyId,
            "SpecialtyName": doctor.specialty.Name if doctor.specialty else None,
            "Qualifications": doctor.Qualifications
        }
    return None

def create_new_doctor_logic(db, request: dict):
    if data_access.get_doctor_by_email(db, request["Email"]) or data_access.get_patient_by_email(db, request["Email"]):
        return {"error": "Email đã được sử dụng."}
    if data_access.get_doctor_by_phone(db, request["Phone"]) or data_access.get_patient_by_phone(db, request["Phone"]):
        return {"error": "Số điện thoại đã được sử dụng."}

    new_doctor = data_access.create_doctor(db, request)
    return {
        "DoctorId": new_doctor.DoctorId,
        "FullName": new_doctor.FullName,
        "Email": new_doctor.Email,
        "Phone": new_doctor.Phone,
        "SpecialtyId": new_doctor.SpecialtyId,
        "Qualifications": new_doctor.Qualifications
    }

def update_doctor_info_logic(db, doctor_id: int, request: dict):
    doctor = data_access.get_doctor_by_id(db, doctor_id)
    if not doctor:
        return {"error": "Không tìm thấy bác sĩ."}

    existing_doctor_email = data_access.get_doctor_by_email(db, request["Email"])
    if existing_doctor_email and existing_doctor_email.DoctorId != doctor_id:
        return {"error": "Email đã được sử dụng bởi một tài khoản khác."}

    existing_doctor_phone = data_access.get_doctor_by_phone(db, request["Phone"])
    if existing_doctor_phone and existing_doctor_phone.DoctorId != doctor_id:
        return {"error": "Số điện thoại đã được sử dụng bởi một tài khoản khác."}

    updated_doctor = data_access.update_doctor(db, doctor_id, request)
    return updated_doctor

def delete_doctor_by_id_logic(db, doctor_id: int):
    if data_access.has_appointments(db, doctor_id):
        return {"error": "Không thể xóa bác sĩ vì đã có lịch hẹn liên quan."}
    
    if data_access.delete_doctor(db, doctor_id):
        return {"message": "Xóa bác sĩ thành công."}
    
    return {"error": "Không tìm thấy bác sĩ."}

# --- Patient/Appointment Logic ---
def book_appointment_logic(db, patient_id: int, booking_dto: dict):
    booking_dto['PatientId'] = patient_id
    booking_dto['Status'] = 'pending'
    new_appointment = data_access.create_appointment(db, booking_dto)
    return {"message": "Đặt lịch hẹn thành công!", "appointmentId": new_appointment.AppointmentId}

def get_my_history_logic(db, patient_id: int):
    appointments = data_access.get_appointments_by_patient_id(db, patient_id)
    return [
        {
            "AppointmentId": a.AppointmentId,
            "AppointmentDatetime": a.AppointmentDatetime,
            "Status": a.Status,
            "DoctorName": a.doctor.FullName if a.doctor else None,
            "SpecialtyName": a.specialty.Name if a.specialty else None,
            "Symptoms": a.Symptoms
        } for a in sorted(appointments, key=lambda x: x.AppointmentDatetime, reverse=True)
    ]

# --- User Profile Logic ---
def update_patient_profile_logic(db, patient_id: int, request: dict):
    patient = data_access.get_patient_by_id(db, patient_id=patient_id)
    if not patient:
        return {"error": "Không tìm thấy bệnh nhân."}

    update_data = {k: v for k, v in request.items() if v is not None}

    if "Email" in update_data and update_data["Email"] != patient.Email:
        if data_access.get_patient_by_email(db, update_data["Email"]) or data_access.get_doctor_by_email(db, update_data["Email"]):
            return {"error": "Email đã được sử dụng."}

    if "Phone" in update_data and update_data["Phone"] != patient.Phone:
        if data_access.get_patient_by_phone(db, update_data["Phone"]) or data_access.get_doctor_by_phone(db, update_data["Phone"]):
            return {"error": "Số điện thoại đã được sử dụng."}

    updated_patient = data_access.update_patient(db, patient_id, update_data)
    return updated_patient

def update_user_password_logic(db, user_id: int, role: str, request: dict):
    user = None
    if role == 'Patient':
        user = data_access.get_patient_by_id(db, patient_id=user_id)
    elif role == 'Doctor':
        user = data_access.get_doctor_by_id(db, doctor_id=user_id)

    if not user:
        return {"error": "Không tìm thấy người dùng."}

    if not data_access.verify_password(request["current_password"], user.PasswordHash):
        return {"error": "Mật khẩu hiện tại không đúng."}

    if role == 'Patient':
        data_access.update_patient_password(db, user_id, request["new_password"])
    elif role == 'Doctor':
        data_access.update_doctor_password(db, user_id, request["new_password"])

    return {"message": "Cập nhật mật khẩu thành công."}
