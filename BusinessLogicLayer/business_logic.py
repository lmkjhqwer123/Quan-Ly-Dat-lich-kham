from DataAccessLayer import data_access
from datetime import datetime, timedelta
import auth
import mail
from typing import Optional, List
from enum import Enum

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

# --- Auth Logic ---
def login_user(db, login_request: dict):
    user_info = None
    role = None

    if login_request.get("Username"):
        admin = data_access.get_admin_by_username(db, login_request["Username"])
        if admin and data_access.verify_password(login_request["Password"], admin.PasswordHash):
            user_info = {"userId": admin.AdminId, "name": admin.Username, "email": admin.Email}
            role = "Admin"

    elif login_request.get("Phone"):
        patient = data_access.get_patient_by_phone(db, login_request["Phone"])
        if patient and data_access.verify_password(login_request["Password"], patient.PasswordHash):
            user_info = {"userId": patient.PatientId, "name": patient.FullName, "email": patient.Email}
            role = "Patient"
        else:
            doctor = data_access.get_doctor_by_phone(db, login_request["Phone"])
            if doctor and data_access.verify_password(login_request["Password"], doctor.PasswordHash):
                user_info = {"userId": doctor.DoctorId, "name": doctor.FullName, "email": doctor.Email}
                role = "Doctor"

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

def request_password_reset_logic(db, email: str):
    user, role = data_access.get_user_by_email(db, email)
    if not user:
        return {"error": "Email not found"}

    user_id = user.PatientId if role == "Patient" else user.DoctorId
    token = auth.create_password_reset_token(data={"sub": email, "user_id": user_id, "role": role})
    expires_at = datetime.utcnow() + timedelta(minutes=auth.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)

    data_access.create_password_reset_token(db, user_id, role, token, expires_at)

    reset_link = f"http://localhost:8000/login.html?token={token}#reset-password"
    mail.send_reset_password_email(email, reset_link)

    return {"message": "Password reset email sent"}

def reset_password_logic(db, token: str, new_password: str):
    decoded_token = auth.verify_password_reset_token(token)
    if not decoded_token:
        return {"error": "Invalid or expired token"}

    db_token = data_access.get_password_reset_token(db, token)
    if not db_token or db_token.expires_at < datetime.utcnow():
        return {"error": "Invalid or expired token"}

    user_id = db_token.user_id
    role = db_token.user_role

    if role == 'Patient':
        data_access.update_patient_password(db, user_id, new_password)
    elif role == 'Doctor':
        data_access.update_doctor_password(db, user_id, new_password)
    else:
        return {"error": "Invalid role"}

    data_access.delete_password_reset_token(db, token)
    return {"message": "Password updated successfully"}

# --- Doctor Logic ---
def get_all_doctors_logic(db, search: Optional[str] = None, sort_direction: Optional[str] = None, sort_value: Optional[str] = None, sort_status: Optional[str] = None, sort_speciality: Optional[int] = None, sort_room: Optional[str] = None, limit: Optional[int] = None):
    doctors = data_access.get_all_doctors(db, search=search, sort_direction=sort_direction, sort_value=sort_value, sort_status=sort_status, sort_speciality=sort_speciality, sort_room=sort_room, limit=limit)
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

def get_doctor_dashboard_data_logic(db, doctor_id: int):
    today = datetime.now().date()
    
    # Get today's appointments
    appointments_today = data_access.get_appointments_by_doctor_id(db, doctor_id, date=today)
    
    # Get current examination queue
    examination_queue = data_access.get_examination_queue_by_doctor_id(db, doctor_id)
    
    return {
        "appointments_today": [
            {
                "AppointmentId": apt.AppointmentId,
                "PatientName": apt.patient.FullName,
                "AppointmentTime": apt.AppointmentDatetime.strftime("%H:%M"),
                "Status": apt.Status
            } for apt in appointments_today
        ],
        "examination_queue": [
            {
                "AppointmentId": q.AppointmentId,
                "PatientName": q.patient.FullName,
                "AppointmentTime": q.AppointmentDatetime.strftime("%H:%M"),
                "Status": q.Status
            } for q in examination_queue
        ]
    }

def get_doctor_appointments_logic(
    db, 
    doctor_id: int, 
    search: Optional[str] = None, 
    sort_by: Optional[str] = None, 
    sort_direction: Optional[str] = "desc", 
    appointment_status: Optional[str] = None, 
    appointment_date: Optional[datetime.date] = None, # Add appointment_date parameter
    limit: Optional[int] = None
):
    appointments = data_access.get_appointments_by_doctor_id(
        db, 
        doctor_id=doctor_id, 
        search=search, 
        sort_by=sort_by, 
        sort_direction=sort_direction, 
        status=appointment_status, 
        appointment_date=appointment_date, # Pass appointment_date to data_access
        limit=limit
    )
    return [
        {
            "AppointmentId": a.AppointmentId,
            "AppointmentDatetime": a.AppointmentDatetime,
            "Status": a.Status,
            "PatientName": a.patient.FullName if a.patient else None,
            "SpecialtyName": a.specialty.Name if a.specialty else None,
            "Symptoms": a.Symptoms,
            "BookingCode": a.BookingCode,
            "Services": [{"id": aps.service.service_id, "name": aps.service.name, "quantity": aps.quantity} for aps in a.appointment_services]
        } for a in sorted(appointments, key=lambda x: x.AppointmentDatetime, reverse=False)
    ]

def get_doctor_appointment_by_id_logic(db, doctor_id: int, appointment_id: int):
    appointment = data_access.get_appointment_by_id(db, appointment_id, doctor_id=doctor_id) # Pass doctor_id to data_access
    if appointment: # data_access now handles doctor_id check
        return {
            "AppointmentId": appointment.AppointmentId,
            "AppointmentDatetime": appointment.AppointmentDatetime,
            "Status": appointment.Status,
            "PatientName": appointment.patient.FullName if appointment.patient else None,
            "SpecialtyName": appointment.specialty.Name if appointment.specialty else None,
            "Symptoms": appointment.Symptoms,
            "BookingCode": appointment.BookingCode
        }
    return None

def get_doctor_examination_queue_logic(
    db, 
    doctor_id: int, 
    statuses: List[AppointmentStatus],
    appointment_date: Optional[datetime.date] = None
):
    examination_queue = data_access.get_examination_queue_by_doctor_id(
        db, 
        doctor_id=doctor_id, 
        statuses=[s.value for s in statuses],
        appointment_date=appointment_date
    )
    return [
        {
            "AppointmentId": q.AppointmentId,
            "PatientName": q.patient.FullName,
            "AppointmentDatetime": q.AppointmentDatetime, # Keep as datetime object for client-side formatting
            "Status": q.Status,
            "SpecialtyName": q.specialty.Name if q.specialty else None,
            "Symptoms": q.Symptoms
        } for q in examination_queue
    ]

def get_doctor_profile_logic(db, doctor_id: int):
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

def update_doctor_profile_logic(db, doctor_id: int, update_data: dict):
    doctor = data_access.get_doctor_by_id(db, doctor_id)
    if not doctor:
        return {"error": "Không tìm thấy bác sĩ."}

    # Check for duplicate email/phone if they are being updated
    if "Email" in update_data and update_data["Email"] != doctor.Email:
        if data_access.get_doctor_by_email(db, update_data["Email"]) and data_access.get_doctor_by_email(db, update_data["Email"]).DoctorId != doctor_id:
            return {"error": "Email đã được sử dụng bởi một tài khoản khác."}
        if data_access.get_patient_by_email(db, update_data["Email"]):
            return {"error": "Email đã được sử dụng bởi một bệnh nhân."}

    if "Phone" in update_data and update_data["Phone"] != doctor.Phone:
        if data_access.get_doctor_by_phone(db, update_data["Phone"]) and data_access.get_doctor_by_phone(db, update_data["Phone"]).DoctorId != doctor_id:
            return {"error": "Số điện thoại đã được sử dụng bởi một tài khoản khác."}
        if data_access.get_patient_by_phone(db, update_data["Phone"]):
            return {"error": "Số điện thoại đã được sử dụng bởi một bệnh nhân."}

    updated_doctor = data_access.update_doctor(db, doctor_id, update_data)
    if updated_doctor:
        return {
            "DoctorId": updated_doctor.DoctorId,
            "FullName": updated_doctor.FullName,
            "Email": updated_doctor.Email,
            "Phone": updated_doctor.Phone,
            "SpecialtyId": updated_doctor.SpecialtyId,
            "SpecialtyName": updated_doctor.specialty.Name if updated_doctor.specialty else None,
            "Qualifications": updated_doctor.Qualifications
        }
    return {"error": "Cập nhật thông tin bác sĩ thất bại."}


# --- Specialty Logic ---
def get_all_specialties_logic(db, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    specialties = data_access.get_all_specialties(db, sort_by, sort_direction)
    return [
        {
            "SpecialtyId": s.SpecialtyId,
            "Name": s.Name,
            "description": s.description
        } for s in specialties
    ]

def search_specialties_logic(db, query: str, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    specialties = data_access.search_specialties(db, query, sort_by, sort_direction)
    return [
        {
            "SpecialtyId": s.SpecialtyId,
            "Name": s.Name,
            "description": s.description
        } for s in specialties
    ]

def get_specialty_by_id_logic(db, specialty_id: int):
    specialty = data_access.get_specialty_by_id(db, specialty_id)
    if specialty:
        return {
            "SpecialtyId": specialty.SpecialtyId,
            "Name": specialty.Name,
            "description": specialty.description
        }
    return None

def create_new_specialty_logic(db, request: dict):
    # Optional: Add validation here if needed, e.g., check for duplicate specialty names
    existing_specialty = data_access.get_specialty_by_name(db, request["Name"])
    if existing_specialty:
        return {"error": "Tên chuyên khoa đã tồn tại."}

    new_specialty = data_access.create_specialty(db, request)
    return {
        "SpecialtyId": new_specialty.SpecialtyId,
        "Name": new_specialty.Name,
        "description": new_specialty.description
    }

def update_specialty_info_logic(db, specialty_id: int, request: dict):
    specialty = data_access.get_specialty_by_id(db, specialty_id)
    if not specialty:
        return {"error": "Không tìm thấy chuyên khoa."}

    if "Name" in request and request["Name"] != specialty.Name:
        existing_specialty = data_access.get_specialty_by_name(db, request["Name"])
        if existing_specialty and existing_specialty.SpecialtyId != specialty_id:
            return {"error": "Tên chuyên khoa đã được sử dụng bởi chuyên khoa khác."}

    updated_specialty = data_access.update_specialty(db, specialty_id, request)
    return {
        "SpecialtyId": updated_specialty.SpecialtyId,
        "Name": updated_specialty.Name,
        "description": updated_specialty.description
    }

def delete_specialty_by_id_logic(db, specialty_id: int):
    # Optional: Check for dependencies (e.g., doctors associated with this specialty)
    # For now, assuming direct deletion is allowed.
    if data_access.delete_specialty(db, specialty_id):
        return {"message": "Xóa chuyên khoa thành công."}
    return {"error": "Không tìm thấy chuyên khoa."}

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
            "Symptoms": a.Symptoms,
            "PatientName": a.patient.FullName if a.patient else None
        } for a in sorted(appointments, key=lambda x: x.AppointmentDatetime, reverse=True)
    ]

def get_all_appointments_logic(db, statuses: Optional[list[str]] = None, date: Optional[datetime.date] = None):
    appointments = data_access.get_all_appointments(db, statuses=statuses, date=date)
    return [
        {
            "AppointmentId": a.AppointmentId,
            "AppointmentDatetime": a.AppointmentDatetime,
            "Status": a.Status,
            "DoctorName": a.doctor.FullName if a.doctor else None,
            "SpecialtyName": a.specialty.Name if a.specialty else None,
            "Symptoms": a.Symptoms,
            "PatientName": a.patient.FullName if a.patient else None,
            "Services": [{"id": aps.service.service_id, "name": aps.service.name, "quantity": aps.quantity} for aps in a.appointment_services]
        } for a in sorted(appointments, key=lambda x: x.AppointmentDatetime, reverse=False)
    ]

def get_appointment_by_id_logic(db, appointment_id: int):
    appointment = data_access.get_appointment_by_id(db, appointment_id)
    if appointment:
        return {
            "AppointmentId": appointment.AppointmentId,
            "AppointmentDatetime": appointment.AppointmentDatetime,
            "Status": appointment.Status,
            "DoctorName": appointment.doctor.FullName if appointment.doctor else None,
            "SpecialtyName": appointment.specialty.Name if appointment.specialty else None,
            "Symptoms": appointment.Symptoms,
            "PatientName": appointment.patient.FullName if appointment.patient else None,
            "Services": [{"id": aps.service.service_id, "name": aps.service.name, "quantity": aps.quantity} for aps in appointment.appointment_services]
        }

    return None

def get_all_patients_logic(db, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    patients = data_access.get_all_patients(db, sort_by, sort_direction)
    return [
        {
            "PatientId": p.PatientId,
            "FullName": p.FullName,
            "Email": p.Email,
            "Phone": p.Phone,
            "birth_date": p.birth_date,
            "address": p.address
        } for p in patients
    ]

def get_patients_for_doctor_logic(db, doctor_id: int, search_query: Optional[str] = None, sort_by: Optional[str] = None, sort_direction: Optional[str] = None, limit: Optional[int] = None):
    patients = data_access.get_patients_for_doctor(db, doctor_id, search_query, sort_by, sort_direction, limit)
    return [
        {
            "PatientId": p.PatientId,
            "FullName": p.FullName,
            "Email": p.Email,
            "Phone": p.Phone,
            "birth_date": p.birth_date,
            "address": p.address
        } for p in patients
    ]

def get_patient_details_for_doctor_logic(db, doctor_id: int, patient_id: int):
    patient = data_access.get_patient_details_for_doctor(db, doctor_id, patient_id)
    if patient:
        return {
            "PatientId": patient.PatientId,
            "FullName": patient.FullName,
            "Email": patient.Email,
            "Phone": patient.Phone,
            "birth_date": patient.birth_date,
            "address": patient.address
        }
    return None

# --- User Profile Logic ---
def get_patient_profile_logic(db, patient_id: int):
    patient = data_access.get_patient_by_id(db, patient_id=patient_id)
    if patient:
        return {
            "PatientId": patient.PatientId,
            "FullName": patient.FullName,
            "Email": patient.Email,
            "Phone": patient.Phone,
            "birth_date": patient.birth_date,
            "address": patient.address
        }
    return None


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

def search_patients_logic(db, query: str, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    patients = data_access.search_patients(db, query, sort_by, sort_direction)
    return [
        {
            "PatientId": p.PatientId,
            "FullName": p.FullName,
            "Email": p.Email,
            "Phone": p.Phone,
            "birth_date": p.birth_date,
            "address": p.address
        } for p in patients
    ]

def get_all_services_logic(db, query: Optional[str] = None, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    services = data_access.get_all_services(db, query, sort_by, sort_direction)
    return [
        {
            "id": s.service_id,
            "name": s.name,
            "description": s.description,
            "price": float(s.price), # Ensure price is float for JSON serialization
            "is_active": s.is_active
        } for s in services
    ]

def get_service_by_id_logic(db, service_id: int):
    service = data_access.get_service_by_id(db, service_id)
    if service:
        return {
            "id": service.service_id,
            "name": service.name,
            "description": service.description,
            "price": float(service.price),
            "is_active": service.is_active
        }
    return None

def create_service_logic(db, service_data: dict):
    new_service = data_access.create_service(db, service_data)
    return {
        "id": new_service.service_id,
        "name": new_service.name,
        "description": new_service.description,
        "price": float(new_service.price),
        "is_active": new_service.is_active
    }

def update_service_logic(db, service_id: int, service_data: dict):
    updated_service = data_access.update_service(db, service_id, service_data)
    if updated_service:
        return {
            "id": updated_service.service_id,
            "name": updated_service.name,
            "description": updated_service.description,
            "price": float(updated_service.price),
            "is_active": updated_service.is_active
        }
    return None

def delete_service_logic(db, service_id: int):
    if data_access.delete_service(db, service_id):
        return {"message": "Dịch vụ đã được xóa thành công."}
    return {"error": "Không tìm thấy dịch vụ."}