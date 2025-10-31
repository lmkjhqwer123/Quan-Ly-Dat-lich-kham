
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
