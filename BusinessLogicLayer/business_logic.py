from DataAccessLayer import data_access
from datetime import datetime, timedelta
import auth
import mail
from typing import Optional, List
from enum import Enum
from routers.doctor.leave_request import LeaveScheduleItem
from fastapi import HTTPException, status

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
            "PatientBirthDate": appointment.patient.birth_date.isoformat() if appointment.patient and appointment.patient.birth_date else None,
            "PatientPhone": appointment.patient.Phone if appointment.patient else None,
            "PatientAddress": appointment.patient.address if appointment.patient else None,
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

def get_doctor_schedule_logic(db, doctor_id: int):
    """
    Lấy và xử lý lịch làm việc cho bác sĩ.
    """
    schedule_data = data_access.get_doctor_schedule(db, doctor_id)
    
    # Chuyển đổi dữ liệu thô từ DB thành định dạng JSON-friendly
    return [
        {
            "appointment_id": item.appointment_id,
            "patient_name": item.patient_name,
            "start_time": item.start_time.isoformat(),
            "end_time": item.end_time.isoformat(),
            "status": item.status,
            "symptoms": item.symptoms
        }
        for item in schedule_data
    ]

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
def book_appointment_logic(db, patient_id: int, booking_dto: dict, booking_code: str):
    appointment_datetime_str = booking_dto.get("AppointmentDatetime")
    doctor_id = booking_dto.get("DoctorId")

    if not appointment_datetime_str or not doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AppointmentDatetime and DoctorId are required."
        )

    try:
        # Ensure appointment_datetime is a datetime object
        if isinstance(appointment_datetime_str, str):
            appointment_datetime = datetime.fromisoformat(appointment_datetime_str)
        elif isinstance(appointment_datetime_str, datetime):
            appointment_datetime = appointment_datetime_str
        else:
            raise ValueError
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid AppointmentDatetime format. Use ISO 8601 format."
        )

    # Assuming a 2-hour appointment slot as per user description
    appointment_end_time = appointment_datetime + timedelta(hours=2)

    # B. Conflict Check
    # 1. Check for conflicting appointments
    conflicting_appointments = data_access.get_conflicting_appointments(
        db,
        doctor_id=doctor_id,
        start_time=appointment_datetime,
        end_time=appointment_end_time
    )
    if conflicting_appointments:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected time slot is already booked with another appointment."
        )

    # 2. Check for conflicting doctor leaves
    conflicting_leaves = data_access.get_conflicting_doctor_leaves(
        db,
        doctor_id=doctor_id,
        start_time=appointment_datetime,
        end_time=appointment_end_time
    )
    if conflicting_leaves:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The doctor is on leave during the selected time slot."
        )

    # C. Ghi Dữ liệu (Data Insertion)
    # If no conflicts, create the appointment
    booking_dto['PatientId'] = patient_id
    booking_dto['Status'] = 'pending'
    booking_dto['BookingCode'] = booking_code
    # Ensure the datetime object is used, not the original string
    booking_dto['AppointmentDatetime'] = appointment_datetime 
    
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

def submit_doctor_leave_request_logic(db, doctor_id: int, leave_type: str, description: Optional[str], schedules: List[LeaveScheduleItem]):
    created_leaves = []
    today = datetime.now().date()

    # --- New Validation Logic ---
    
    # 1. Parse and sort requested dates
    requested_dates = sorted([datetime.strptime(s.date, '%Y-%m-%d').date() for s in schedules])

    # 2. Check for more than 3 consecutive days in the request itself
    if len(requested_dates) > 3:
        for i in range(len(requested_dates) - 3):
            if (requested_dates[i+3] - requested_dates[i]).days == 3:
                raise ValueError("Không thể đăng ký nghỉ quá 3 ngày liên tục trong một lần đăng ký.")

    # 3. Check monthly leave limit (<= 6 days)
    monthly_requests = {}
    for date in requested_dates:
        month_key = (date.year, date.month)
        if month_key not in monthly_requests:
            monthly_requests[month_key] = 0
        monthly_requests[month_key] += 1

    for (year, month), count in monthly_requests.items():
        existing_leaves = data_access.get_doctor_leaves_for_month(db, doctor_id, year, month)
        if len(existing_leaves) + count > 6:
            raise ValueError(f"Không thể đăng ký nghỉ quá 6 ngày trong tháng {month}/{year}.")

    # 4. Check for consecutive days within a week (including existing leave)
    for req_date in requested_dates:
        # Check a 7-day window around the requested date
        start_check = req_date - timedelta(days=3)
        end_check = req_date + timedelta(days=3)
        
        # Get existing leaves in this window
        existing_leaves_in_window = data_access.get_doctor_leaves_in_range(db, doctor_id, start_check, end_check)
        
        # Combine existing leave dates and the current request's dates within the window
        all_leave_dates_in_window = set(l.StartDatetime.date() for l in existing_leaves_in_window)
        all_leave_dates_in_window.update(d for d in requested_dates if start_check <= d <= end_check)
        
        sorted_window_dates = sorted(list(all_leave_dates_in_window))

        # Check for more than 3 consecutive days in the combined list
        if len(sorted_window_dates) > 3:
            for i in range(len(sorted_window_dates) - 3):
                if (sorted_window_dates[i+3] - sorted_window_dates[i]).days == 3:
                    raise ValueError(f"Việc đăng ký ngày {req_date.strftime('%d/%m/%Y')} sẽ tạo thành một chuỗi nghỉ dài hơn 3 ngày liên tục.")

    # --- End of New Validation Logic ---

    urgent_leave_types = ['sick', 'urgent']
    doctor_specialty_id = data_access.get_doctor_specialty_id(db, doctor_id)
    if not doctor_specialty_id:
        raise ValueError("Doctor's specialty not found.")
    
    for schedule_item in schedules:
        date_str = schedule_item.date
        start_time_str = schedule_item.start_time
        end_time_str = schedule_item.end_time

        schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if schedule_date < today:
            raise ValueError(f"Không thể đăng ký nghỉ phép cho ngày trong quá khứ: {date_str}")

        start_datetime_str = f"{date_str}T{start_time_str or '00:00:00'}"
        end_datetime_str = f"{date_str}T{end_time_str or '23:59:59'}"

        try:
            start_datetime = datetime.fromisoformat(start_datetime_str)
            end_datetime = datetime.fromisoformat(end_datetime_str)
        except ValueError:
            raise ValueError(f"Invalid date or time format for schedule item: {schedule_item}")

        if start_datetime >= end_datetime:
            raise ValueError("Start time must be before end time for leave request.")

        overlapping_leaves = data_access.get_overlapping_doctor_leaves(db, doctor_id, start_datetime, end_datetime)
        if overlapping_leaves:
            raise ValueError(f"Bạn đã có đơn đăng ký nghỉ phép trùng lặp hoặc chồng chéo vào ngày {date_str} từ {start_time_str} đến {end_time_str}.")

        total_doctors_in_specialty = data_access.get_total_doctors_in_specialty(db, doctor_specialty_id)
        doctors_on_leave_in_specialty = data_access.get_doctors_on_leave_in_specialty(db, doctor_specialty_id, start_datetime, end_datetime)
        
        available_doctors_after_this_leave = total_doctors_in_specialty - doctors_on_leave_in_specialty - 1
        if available_doctors_after_this_leave < 1:
            raise ValueError(f"Không thể đăng ký nghỉ phép vào ngày {date_str} vì sẽ không có đủ bác sĩ trong chuyên khoa này hoạt động vào thời gian đó.")

        initial_status = "approved" if leave_type in urgent_leave_types else "pending"

        new_leave = data_access.create_doctor_leave_entry(
            db,
            doctor_id=doctor_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=description,
            leave_type=leave_type,
            status=initial_status
        )
        created_leaves.append(new_leave)
    
    response_leaves = []
    for leave in created_leaves:
        response_leaves.append({
            "leave_id": leave.LeaveId,
            "doctor_id": leave.DoctorId,
            "start_datetime": leave.StartDatetime,
            "end_datetime": leave.EndDatetime,
            "reason": leave.Reason,
            "leave_type": leave.LeaveType,
            "status": leave.Status
        })
    return response_leaves

def get_doctor_monthly_availability_logic(db, doctor_id: int, year: int, month: int):
    """
    Business logic to get monthly availability for a doctor.
    """
    return data_access.get_doctor_monthly_availability(db, doctor_id, year, month)

def get_doctor_daily_availability_logic(db, doctor_id: int, date: datetime.date):
    """
    Business logic to get daily availability for a doctor.
    """
    return data_access.get_doctor_daily_availability(db, doctor_id, date)

def update_appointment_status_logic(db, appointment_id: int, new_status: str):
    """
    Business logic to update the status of an appointment.
    """
    # Optional: Add validation for the new_status here if needed
    # For example, check if it's a valid status from an Enum

    updated_appointment = data_access.update_appointment_status(db, appointment_id, new_status)

    if not updated_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with id {appointment_id} not found."
        )

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": updated_appointment.AppointmentId,
        "new_status": updated_appointment.Status
    }

async def create_medical_record_bl(db, medical_record_data: dict):
    """
    Business logic to create a medical record and update the associated appointment status to 'completed'.
    """
    appointment_id = medical_record_data.get("appointment_id")
    if not appointment_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment ID is required to create a medical record.")

    # 1. Create the medical record
    medical_record_id = data_access.insert_medical_record(db, medical_record_data)
    
    if not medical_record_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create medical record.")

    # 2. Update the appointment status to 'completed'
    updated_appointment = data_access.update_appointment_status(db, appointment_id, AppointmentStatus.COMPLETED.value)

    if not updated_appointment:
        # If for some reason the appointment status update fails, we should consider rolling back the medical record creation
        # For simplicity, we'll just log an error or raise an exception here.
        # In a real-world scenario, a more robust transaction management would be needed.
        print(f"Warning: Medical record created (ID: {medical_record_id}) but failed to update appointment {appointment_id} status to 'completed'.")
        # Optionally, raise an exception if this is considered a critical failure
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Medical record created but failed to update appointment status.")

    return medical_record_id