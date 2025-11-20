import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Date, DECIMAL, Boolean, func, text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, joinedload, Session
import bcrypt
import datetime
from typing import Optional, List

# --- Database Setup ---
# --- Thay đổi chuỗi kết nối theo cấu hình của bạn ---
DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://DESKTOP-V9NP2C3/QuanLyKhamBenhDB?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&Encrypt=yes&TrustServerCertificate=yes")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Models ---
class Patient(Base):
    __tablename__ = "patients"
    PatientId = Column('patient_id', Integer, primary_key=True, index=True)
    FullName = Column('full_name', String, index=True)
    Email = Column('email', String, unique=True, index=True)
    Phone = Column('phone', String, unique=True, index=True)
    PasswordHash = Column('password_hash', String)
    birth_date = Column('birth_date', Date)
    address = Column('address', String)
    appointments = relationship("Appointment", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"
    DoctorId = Column('doctor_id', Integer, primary_key=True, index=True)
    FullName = Column('full_name', String, index=True)
    Email = Column('email', String, unique=True, index=True)
    Phone = Column('phone', String, unique=True, index=True)
    SpecialtyId = Column('specialty_id', Integer, ForeignKey("specialties.specialty_id"))
    Qualifications = Column('qualifications', String)
    PasswordHash = Column('password_hash', String)
    specialty = relationship("Specialty")
    appointments = relationship("Appointment", back_populates="doctor")

class Admin(Base):
    __tablename__ = "admins"
    AdminId = Column('admin_id', Integer, primary_key=True, index=True)
    Username = Column('username', String, unique=True, index=True)
    Email = Column('email', String, unique=True)
    PasswordHash = Column('password_hash', String)

class Specialty(Base):
    __tablename__ = "specialties"
    SpecialtyId = Column('specialty_id', Integer, primary_key=True, index=True)
    Name = Column('name', String, index=True)
    description = Column('description', String)

class Appointment(Base):
    __tablename__ = "appointments"
    AppointmentId = Column('appointment_id', Integer, primary_key=True, index=True)
    PatientId = Column('patient_id', Integer, ForeignKey("patients.patient_id"))
    DoctorId = Column('doctor_id', Integer, ForeignKey("doctors.doctor_id"))
    SpecialtyId = Column('specialty_id', Integer, ForeignKey("specialties.specialty_id"))
    AppointmentDatetime = Column('appointment_datetime', DateTime)
    Symptoms = Column('symptoms', Text)
    Status = Column('status', String)
    BookingCode = Column('booking_code', String, nullable=True)
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    specialty = relationship("Specialty")
    appointment_services = relationship("AppointmentService", back_populates="appointment", lazy='joined')

class AppointmentService(Base):
    __tablename__ = "appointment_services"
    appointment_service_id = Column('appointment_service_id', Integer, primary_key=True, index=True)
    appointment_id = Column('appointment_id', Integer, ForeignKey("appointments.appointment_id"))
    service_id = Column('service_id', Integer, ForeignKey("SERVICES.service_id"))
    quantity = Column('quantity', Integer, default=1)
    notes = Column('notes', String)

    appointment = relationship("Appointment", back_populates="appointment_services")
    service = relationship("Service", back_populates="appointment_services")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_role = Column(String(50), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

class Service(Base):
    __tablename__ = "SERVICES"
    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    appointment_services = relationship("AppointmentService", back_populates="service")

class DoctorLeave(Base):
    __tablename__ = "DOCTOR_LEAVES"
    LeaveId = Column('leave_id', Integer, primary_key=True, index=True)
    DoctorId = Column('doctor_id', Integer, ForeignKey("doctors.doctor_id"))
    StartDatetime = Column('start_datetime', DateTime, nullable=False)
    EndDatetime = Column('end_datetime', DateTime, nullable=False)
    Reason = Column('reason', Text, nullable=True)
    LeaveType = Column('leave_type', String(50), nullable=False)
    Status = Column('status', String(20), nullable=False)

    doctor = relationship("Doctor")

class DoctorWorkingHour(Base):
    __tablename__ = "DOCTOR_WORKING_HOURS"
    WorkingHourId = Column('working_hour_id', Integer, primary_key=True, index=True)
    DoctorId = Column('doctor_id', Integer, ForeignKey("doctors.doctor_id"))
    DayOfWeek = Column('day_of_week', String(10), nullable=False)
    StartTime = Column('start_time', String, nullable=False) # Store as string 'HH:MM'
    EndTime = Column('end_time', String, nullable=False) # Store as string 'HH:MM'

    doctor = relationship("Doctor")

import pyodbc

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# --- Data Access Functions ---

def get_raw_db_connection():
    """
    Provides a direct pyodbc connection to the database.
    The caller is responsible for closing the connection.
    """
    try:
        # The DATABASE_URL is for SQLAlchemy, we need to construct a pyodbc one
        # This is a simplified example. In a real app, parse DATABASE_URL or use separate configs.
        conn_str = os.getenv("DATABASE_URL_PYODBC", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-V9NP2C3;DATABASE=QuanLyKhamBenhDB;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes")
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"PYODBC Connection Error: {sqlstate}")
        print(ex)
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# --- User/Auth ---
def get_user_by_email(db, email: str):
    user = db.query(Patient).filter(Patient.Email == email).first()
    if user:
        return user, "Patient"
    user = db.query(Doctor).filter(Doctor.Email == email).first()
    if user:
        return user, "Doctor"
    return None, None

def get_patient_by_phone(db, phone: str):
    return db.query(Patient).filter(Patient.Phone == phone).first()

def get_doctor_by_phone(db, phone: str):
    return db.query(Doctor).filter(Doctor.Phone == phone).first()

def get_admin_by_username(db, username: str):
    return db.query(Admin).filter(Admin.Username == username).first()

def get_admin_by_id(db, admin_id: int):
    return db.query(Admin).filter(Admin.AdminId == admin_id).first()

# --- Doctors ---
def get_all_doctors(db, search: Optional[str] = None, sort_direction: Optional[str] = None, sort_value: Optional[str] = None, sort_status: Optional[str] = None, sort_speciality: Optional[int] = None, sort_room: Optional[str] = None, limit: Optional[int] = None):
    query = db.query(Doctor)

    if search:
        query = query.filter(Doctor.FullName.ilike(f"%{search}%"))
    
    if sort_speciality:
        query = query.filter(Doctor.SpecialtyId == sort_speciality)

    # Assuming 'status' is a property on the Doctor model, which it is not.
    # This will need to be adjusted if status is handled differently.
    # For now, commenting out status filtering.
    # if sort_status:
    #     query = query.filter(Doctor.status == sort_status)

    if sort_value == "name":
        if sort_direction == "desc":
            query = query.order_by(Doctor.FullName.desc())
        else:
            query = query.order_by(Doctor.FullName.asc())
    
    # Sorting by role is not directly possible as role is not a column.
    # Assuming a default sorting if role is selected.
    
    if limit:
        query = query.limit(limit)
        
    return query.all()

def get_doctor_by_id(db, doctor_id: int):
    return db.query(Doctor).filter(Doctor.DoctorId == doctor_id).first()

def get_doctor_specialty_id(db: Session, doctor_id: int) -> Optional[int]:
    doctor = db.query(Doctor).filter(Doctor.DoctorId == doctor_id).first()
    if doctor:
        return doctor.SpecialtyId
    return None

def get_doctors_in_specialty_excluding_one(db: Session, specialty_id: int, excluded_doctor_id: int) -> List[Doctor]:
    return db.query(Doctor).filter(
        Doctor.SpecialtyId == specialty_id,
        Doctor.DoctorId != excluded_doctor_id
    ).all()

def get_total_doctors_in_specialty(db: Session, specialty_id: int) -> int:
    """
    Counts the total number of doctors in a given specialty.
    """
    return db.query(Doctor).filter(Doctor.SpecialtyId == specialty_id).count()

def get_doctors_on_leave_in_specialty(db: Session, specialty_id: int, start_datetime: datetime, end_datetime: datetime) -> int:
    """
    Counts the number of doctors in a given specialty who have approved leave requests
    that overlap with the specified time range.
    """
    return db.query(Doctor.DoctorId).distinct().join(DoctorLeave).filter(
        Doctor.SpecialtyId == specialty_id,
        DoctorLeave.Status == 'approved',
        DoctorLeave.StartDatetime < end_datetime,
        DoctorLeave.EndDatetime > start_datetime
    ).count()

def is_doctor_available(db: Session, doctor_id: int, check_start_datetime: datetime, check_end_datetime: datetime) -> bool:
    # 1. Check for overlapping leaves
    overlapping_leaves = db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.Status == 'approved', # Only consider approved leaves
        DoctorLeave.StartDatetime < check_end_datetime,
        DoctorLeave.EndDatetime > check_start_datetime
    ).first()
    if overlapping_leaves:
        return False # Doctor is on an approved leave

    # 2. Check for working hours
    # Convert check_start_datetime and check_end_datetime to day of week and time objects
    day_of_week = check_start_datetime.strftime('%A').upper() # e.g., 'MONDAY'
    check_start_time = check_start_datetime.time()
    check_end_time = check_end_datetime.time()

    # Find working hours for the specific day
    working_hours_entries = db.query(DoctorWorkingHour).filter(
        DoctorWorkingHour.DoctorId == doctor_id,
        DoctorWorkingHour.DayOfWeek == day_of_week
    ).all()

    if not working_hours_entries:
        # If no specific working hours are defined for this day, assume default availability.
        # This means the doctor is available if not on leave.
        return True

    # If there are specific working hours, check if the requested time range falls within any defined working hours
    for wh in working_hours_entries:
        wh_start_time = datetime.datetime.strptime(wh.StartTime, '%H:%M').time()
        wh_end_time = datetime.datetime.strptime(wh.EndTime, '%H:%M').time()

        # Check for overlap:
        # (StartA < EndB) and (EndA > StartB)
        if (check_start_time < wh_end_time) and (check_end_time > wh_start_time):
            return True # There is an overlap with working hours

    return False # No overlapping working hours found, and specific working hours were defined

def get_doctor_by_email(db, email: str):
    return db.query(Doctor).filter(Doctor.Email == email).first()

def get_overlapping_doctor_leaves(db: Session, doctor_id: int, start_datetime: datetime, end_datetime: datetime) -> List[DoctorLeave]:
    """
    Retrieves any existing leave entries for a specific doctor that overlap with the given time range.
    """
    return db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.StartDatetime < end_datetime,
        DoctorLeave.EndDatetime > start_datetime
    ).all()

def create_doctor(db, doctor_data: dict):
    hashed_password = hash_password(doctor_data["Password"])
    db_doctor = Doctor(
        FullName=doctor_data["FullName"],
        Email=doctor_data["Email"],
        Phone=doctor_data["Phone"],
        SpecialtyId=doctor_data["SpecialtyId"],
        Qualifications=doctor_data["Qualifications"],
        PasswordHash=hashed_password
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def update_doctor(db, doctor_id: int, doctor_data: dict):
    db_doctor = get_doctor_by_id(db, doctor_id)
    if db_doctor:
        db_doctor.FullName = doctor_data["FullName"]
        db_doctor.Email = doctor_data["Email"]
        db_doctor.Phone = doctor_data["Phone"]
        db_doctor.SpecialtyId = doctor_data["SpecialtyId"],
        db_doctor.Qualifications = doctor_data["Qualifications"]
        db.commit()
        db.refresh(db_doctor)
    return db_doctor
    
def update_doctor_password(db, doctor_id: int, new_password: str):
    db_doctor = db.query(Doctor).filter(Doctor.DoctorId == doctor_id).first()
    if db_doctor:
        db_doctor.PasswordHash = hash_password(new_password)
        db.commit()
        return True
    return False

def delete_doctor(db, doctor_id: int):
    db_doctor = get_doctor_by_id(db, doctor_id)
    if db_doctor:
        db.delete(db_doctor)
        db.commit()
        return True
    return False

def has_appointments(db, doctor_id: int):
    return db.query(Appointment).filter(Appointment.DoctorId == doctor_id).first() is not None

# --- Specialties ---
def get_all_specialties(db, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    query = db.query(Specialty)
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(Specialty.Name.desc())
        else:
            query = query.order_by(Specialty.Name.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            query = query.order_by(Specialty.SpecialtyId.desc())
        else:
            query = query.order_by(Specialty.SpecialtyId.asc())
    return query.all()

def search_specialties(db, query: str, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    search_pattern = f"%{query}%"
    base_query = db.query(Specialty).filter(
        (Specialty.Name.ilike(search_pattern)) |
        (Specialty.description.ilike(search_pattern))
    )

    if sort_by == "name":
        if sort_direction == "desc":
            base_query = base_query.order_by(Specialty.Name.desc())
        else:
            base_query = base_query.order_by(Specialty.Name.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            base_query = base_query.order_by(Specialty.SpecialtyId.desc())
        else:
            base_query = base_query.order_by(Specialty.SpecialtyId.asc())
    return base_query.all()

def get_specialty_by_id(db, specialty_id: int):
    return db.query(Specialty).filter(Specialty.SpecialtyId == specialty_id).first()

def create_specialty(db, specialty_data: dict):
    db_specialty = Specialty(
        Name=specialty_data["Name"],
        description=specialty_data.get("description")
    )
    db.add(db_specialty)
    db.commit()
    db.refresh(db_specialty)
    return db_specialty

def update_specialty(db, specialty_id: int, specialty_data: dict):
    db_specialty = get_specialty_by_id(db, specialty_id)
    if db_specialty:
        for key, value in specialty_data.items():
            setattr(db_specialty, key, value)
        db.commit()
        db.refresh(db_specialty)
    return db_specialty

def delete_specialty(db, specialty_id: int):
    db_specialty = get_specialty_by_id(db, specialty_id)
    if db_specialty:
        db.delete(db_specialty)
        db.commit()
        return True
    return False

def get_specialty_by_name(db, name: str):
    return db.query(Specialty).filter(Specialty.Name == name).first()

# --- Patients ---
def get_patient_by_id(db, patient_id: int):
    return db.query(Patient).filter(Patient.PatientId == patient_id).first()

def get_patient_by_email(db, email: str):
    return db.query(Patient).filter(Patient.Email == email).first()

def get_all_patients(db, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    query = db.query(Patient)
    if sort_by == "name":
        if sort_direction == "desc":
            query = query.order_by(Patient.FullName.desc())
        else:
            query = query.order_by(Patient.FullName.asc())
    elif sort_by == "email":
        if sort_direction == "desc":
            query = query.order_by(Patient.Email.desc())
        else:
            query = query.order_by(Patient.Email.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            query = query.order_by(Patient.PatientId.desc())
        else:
            query = query.order_by(Patient.PatientId.asc())
    return query.all()

def get_patients_for_doctor(db, doctor_id: int, search_query: Optional[str] = None, sort_by: Optional[str] = None, sort_direction: Optional[str] = None, limit: Optional[int] = None):
    # Subquery to get unique patient IDs associated with the doctor
    patient_ids_subquery = db.query(Appointment.PatientId).filter(Appointment.DoctorId == doctor_id).distinct()

    # Main query for patients
    base_query = db.query(Patient).filter(Patient.PatientId.in_(patient_ids_subquery))

    if search_query:
        search_pattern = f"%{search_query}%"
        base_query = base_query.filter(
            (Patient.FullName.ilike(search_pattern)) |
            (Patient.Email.ilike(search_pattern)) |
            (Patient.Phone.ilike(search_pattern))
        )

    if sort_by == "name":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.FullName.desc())
        else:
            base_query = base_query.order_by(Patient.FullName.asc())
    elif sort_by == "email":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.Email.desc())
        else:
            base_query = base_query.order_by(Patient.Email.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.PatientId.desc())
        else:
            base_query = base_query.order_by(Patient.PatientId.asc())
            
    return base_query.all()

def get_patient_details_for_doctor(db, doctor_id: int, patient_id: int):
    # Check if the patient is associated with the doctor through an appointment
    is_associated = db.query(Appointment).filter(
        Appointment.DoctorId == doctor_id,
        Appointment.PatientId == patient_id
    ).first()

    if is_associated:
        return db.query(Patient).filter(Patient.PatientId == patient_id).first()
    return None

def create_patient(db, patient_data: dict):
    hashed_password = hash_password(patient_data["Password"])
    birth_date = patient_data.get("birth_date") or datetime.date.today()
    db_patient = Patient(
        FullName=patient_data["FullName"],
        Email=patient_data["Email"],
        Phone=patient_data["Phone"],
        birth_date=birth_date,
        address=patient_data.get("address"),
        PasswordHash=hashed_password
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient_password(db, patient_id: int, new_password: str):
    db_patient = db.query(Patient).filter(Patient.PatientId == patient_id).first()
    if db_patient:
        db_patient.PasswordHash = hash_password(new_password)
        db.commit()
        return True
    return False

def update_patient(db, patient_id: int, patient_data: dict):
    db_patient = get_patient_by_id(db, patient_id)
    if db_patient:
        for key, value in patient_data.items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def search_patients(db, query: str, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    search_pattern_starts_with = f"{query}%"
    search_pattern_contains = f"%{query}%"

    base_query = db.query(Patient).filter(
        (Patient.FullName.ilike(search_pattern_starts_with)) |
        (Patient.Email.ilike(search_pattern_contains)) |
        (Patient.Phone.ilike(search_pattern_contains)) |
        (Patient.address.ilike(search_pattern_contains))
    )

    if sort_by == "name":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.FullName.desc())
        else:
            base_query = base_query.order_by(Patient.FullName.asc())
    elif sort_by == "email":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.Email.desc())
        else:
            base_query = base_query.order_by(Patient.Email.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            base_query = base_query.order_by(Patient.PatientId.desc())
        else:
            base_query = base_query.order_by(Patient.PatientId.asc())
    return base_query.all()

# --- Admins ---
def create_admin(db, admin_data: dict):
    hashed_password = hash_password(admin_data["Password"])
    db_admin = Admin(
        Username=admin_data["Username"],
        Email=admin_data["Email"],
        PasswordHash=hashed_password
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_admin__password(db, admin_id: int, new_password: str):
    db_admin = db.query(Admin).filter(Admin.AdminId == admin_id).first()
    if db_admin:
        db_admin.PasswordHash = hash_password(new_password)
        db.commit()
        return True
    return False

# --- Appointments ---
def create_appointment(db, appointment_data: dict):
    services_data = appointment_data.pop("Services", [])
    db_appointment = Appointment(**appointment_data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    for service_item in services_data:
        db_appointment_service = AppointmentService(
            appointment_id=db_appointment.AppointmentId,
            service_id=service_item["service_id"],
            quantity=service_item.get("quantity", 1)
        )
        db.add(db_appointment_service)
    db.commit()
    db.refresh(db_appointment) # Refresh again to load the newly added appointment_services
    return db_appointment

def get_conflicting_appointments(db: Session, doctor_id: int, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Checks for existing appointments for a doctor that conflict with the given time slot.
    It considers appointments that are 'pending' or 'confirmed'.
    An appointment conflicts if its 2-hour slot overlaps with the proposed time slot.
    """
    return db.query(Appointment).filter(
        Appointment.DoctorId == doctor_id,
        Appointment.Status.in_(['pending', 'confirmed']),
        Appointment.AppointmentDatetime < end_time,
        func.DATEADD(text("hour"), 2, Appointment.AppointmentDatetime) > start_time
    ).all()

def get_conflicting_doctor_leaves(db: Session, doctor_id: int, start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Checks for approved doctor leaves that conflict with the given time slot.
    """
    return db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.Status == 'approved',
        DoctorLeave.StartDatetime < end_time,
        DoctorLeave.EndDatetime > start_time
    ).all()

def get_appointments_by_doctor_id(
    db, 
    doctor_id: int, 
    search: Optional[str] = None, 
    sort_by: Optional[str] = None, 
    sort_direction: Optional[str] = "desc", 
    status: Optional[str] = None, 
    appointment_date: Optional[datetime.date] = None,
    limit: Optional[int] = None
):
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.specialty),
        joinedload(Appointment.appointment_services).joinedload(AppointmentService.service)
    ).filter(Appointment.DoctorId == doctor_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Appointment.patient.has(Patient.FullName.ilike(search_pattern))) |
            (Appointment.BookingCode.ilike(search_pattern))
        )

    if status:
        query = query.filter(Appointment.Status == status)

    if appointment_date:
        start_of_day = datetime.datetime.combine(appointment_date, datetime.time.min)
        end_of_day = datetime.datetime.combine(appointment_date, datetime.time.max)
        query = query.filter(Appointment.AppointmentDatetime.between(start_of_day, end_of_day))

    if sort_by == "time":
        if sort_direction == "desc":
            query = query.order_by(Appointment.AppointmentDatetime.desc())
        else:
            query = query.order_by(Appointment.AppointmentDatetime.asc())
    elif sort_by == "patient_name":
        if sort_direction == "desc":
            query = query.order_by(Patient.FullName.desc())
        else:
            query = query.order_by(Patient.FullName.asc())
    else:
        query = query.order_by(Appointment.AppointmentDatetime.asc()) # Default sort

    if limit:
        query = query.limit(limit)
        
    return query.all()

def get_examination_queue_by_doctor_id(
    db, 
    doctor_id: int,
    statuses: List[str],
    appointment_date: Optional[datetime.date] = None
):
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.specialty) # Eagerly load specialty
    ).filter(
        Appointment.DoctorId == doctor_id
    )

    # Filter by appointment date
    if appointment_date:
        start_of_day = datetime.datetime.combine(appointment_date, datetime.time.min)
        end_of_day = datetime.datetime.combine(appointment_date, datetime.time.max)
        query = query.filter(Appointment.AppointmentDatetime.between(start_of_day, end_of_day))
    else:
        # Default to today if no specific date is provided
        today = datetime.date.today()
        start_of_day = datetime.datetime.combine(today, datetime.time.min)
        end_of_day = datetime.datetime.combine(today, datetime.time.max)
        query = query.filter(Appointment.AppointmentDatetime.between(start_of_day, end_of_day))

    # Filter by appointment statuses
    if statuses:
        query = query.filter(Appointment.Status.in_(statuses))
    else:
        # Default to 'confirmed' if no statuses are provided
        query = query.filter(Appointment.Status == 'confirmed')

    query = query.order_by(Appointment.AppointmentDatetime.asc()) # Default sort for queue
        
    return query.all()

def get_appointment_by_id(db, appointment_id: int, doctor_id: Optional[int] = None):
    query = db.query(Appointment).options(
        joinedload(Appointment.patient), 
        joinedload(Appointment.doctor), 
        joinedload(Appointment.specialty), 
        joinedload(Appointment.appointment_services).joinedload(AppointmentService.service)
    ).filter(Appointment.AppointmentId == appointment_id)
    
    if doctor_id:
        query = query.filter(Appointment.DoctorId == doctor_id)
        
    return query.first()

def get_all_appointments(db, statuses: Optional[List[str]] = None, date: Optional[datetime.date] = None):
    query = db.query(Appointment).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.specialty),
        joinedload(Appointment.appointment_services).joinedload(AppointmentService.service)
    )

    if statuses:
        query = query.filter(Appointment.Status.in_(statuses))

    if date:
        start_of_day = datetime.datetime.combine(date, datetime.time.min)
        end_of_day = datetime.datetime.combine(date, datetime.time.max)
        query = query.filter(Appointment.AppointmentDatetime.between(start_of_day, end_of_day))
        
    return query.all()

def get_doctor_schedule(db: Session, doctor_id: int):
    """
    Lấy lịch làm việc của bác sĩ từ các cuộc hẹn đã được xác nhận.
    end_time được tính bằng cách thêm 2 giờ vào thời gian bắt đầu cuộc hẹn.
    """
    query = text("""
        SELECT 
            a.appointment_id,
            p.full_name AS patient_name,
            a.appointment_datetime AS start_time,
            DATEADD(hour, 2, a.appointment_datetime) AS end_time,
            a.status,
            a.symptoms
        FROM 
            appointments a
        JOIN 
            patients p ON a.patient_id = p.patient_id
        WHERE 
            a.doctor_id = :doctor_id
        ORDER BY 
            a.appointment_datetime
    """)
    
    result = db.execute(query, {"doctor_id": doctor_id})
    return result.mappings().all()

def update_appointment_status(db: Session, appointment_id: int, new_status: str):
    """
    Updates the status of a specific appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.AppointmentId == appointment_id).first()
    if appointment:
        appointment.Status = new_status
        db.commit()
        db.refresh(appointment)
    return appointment

# --- Password Reset Tokens ---
def create_password_reset_token(db, user_id: int, user_role: str, token: str, expires_at: datetime):
    db_token = PasswordResetToken(
        user_id=user_id,
        user_role=user_role,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_password_reset_token(db, token: str):
    return db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

def delete_password_reset_token(db, token: str):
    db_token = get_password_reset_token(db, token)
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False

# --- Services ---
def get_all_services(db, query: Optional[str] = None, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    base_query = db.query(Service)

    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(
            (Service.name.ilike(search_pattern)) |
            (Service.description.ilike(search_pattern))
        )

    if sort_by == "name":
        if sort_direction == "desc":
            base_query = base_query.order_by(Service.name.desc())
        else:
            base_query = base_query.order_by(Service.name.asc())
    elif sort_by == "id":
        if sort_direction == "desc":
            base_query = base_query.order_by(Service.service_id.desc())
        else:
            base_query = base_query.order_by(Service.service_id.asc())
    
    return base_query.all()

def get_service_by_id(db, service_id: int):
    return db.query(Service).filter(Service.service_id == service_id).first()

def create_service(db, service_data: dict):
    db_service = Service(
        name=service_data["name"],
        description=service_data.get("description"),
        price=service_data["price"],
        is_active=service_data.get("is_active", True)
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def update_service(db, service_id: int, service_data: dict):
    db_service = get_service_by_id(db, service_id)
    if db_service:
        for key, value in service_data.items():
            setattr(db_service, key, value)
        db.commit()
        db.refresh(db_service)
    return db_service

def delete_service(db, service_id: int):
    db_service = get_service_by_id(db, service_id)
    if db_service:
        db.delete(db_service)
        db.commit()
        return True
    return False

def get_service_by_name(db, name: str):
    return db.query(Service).filter(Service.name == name).first()

def create_appointment_service(db, appointment_service_data: dict):
    db_appointment_service = AppointmentService(**appointment_service_data)
    db.add(db_appointment_service)
    db.commit()
    db.refresh(db_appointment_service)
    return db_appointment_service

def get_doctor_monthly_availability(db: Session, doctor_id: int, year: int, month: int) -> dict:
    """
    Retrieves the availability of a doctor for each day of a given month,
    considering approved leaves and pending/confirmed appointments.
    Returns a dictionary where keys are days of the month (int) and values are
    lists of unavailable time slots (e.g., ['07:00-09:00', '09:00-11:00']).
    """
    start_date = datetime.datetime(year, month, 1)
    # Calculate the last day of the month
    if month == 12:
        end_date = datetime.datetime(year + 1, 1, 1) - datetime.timedelta(microseconds=1)
    else:
        end_date = datetime.datetime(year, month + 1, 1) - datetime.timedelta(microseconds=1)

    # Define the fixed time slots
    time_slots = {
        "07:00-09:00": (datetime.time(7, 0, 0), datetime.time(9, 0, 0)),
        "09:00-11:00": (datetime.time(9, 0, 0), datetime.time(11, 0, 0)),
        "13:00-15:00": (datetime.time(13, 0, 0), datetime.time(15, 0, 0)),
        "15:00-17:00": (datetime.time(15, 0, 0), datetime.time(17, 0, 0)),
    }

    monthly_availability = {}
    for day in range(1, (end_date.day + 1)):
        monthly_availability[day] = []

    # Fetch appointments for the month
    appointments = db.query(Appointment).filter(
        Appointment.DoctorId == doctor_id,
        Appointment.AppointmentDatetime >= start_date,
        Appointment.AppointmentDatetime <= end_date,
        Appointment.Status.in_(['pending', 'confirmed'])
    ).all()

    for appt in appointments:
        appt_date = appt.AppointmentDatetime.date()
        appt_time = appt.AppointmentDatetime.time()
        day_of_month = appt_date.day

        for slot_name, (slot_start, slot_end) in time_slots.items():
            # Check if appointment time falls within a slot
            if slot_start <= appt_time < slot_end:
                if slot_name not in monthly_availability[day_of_month]:
                    monthly_availability[day_of_month].append(slot_name)
                break # Assuming one appointment per slot for simplicity

    # Fetch approved doctor leaves for the month
    leaves = db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.StartDatetime <= end_date,
        DoctorLeave.EndDatetime >= start_date,
        DoctorLeave.Status == 'approved'
    ).all()

    for leave in leaves:
        leave_start_date = leave.StartDatetime.date()
        leave_end_date = leave.EndDatetime.date()

        current_date = max(start_date.date(), leave_start_date)
        while current_date <= min(end_date.date(), leave_end_date):
            day_of_month = current_date.day
            
            for slot_name, (slot_start, slot_end) in time_slots.items():
                # Check if the leave period overlaps with the time slot on the current_date
                leave_start_time_on_day = leave.StartDatetime.time() if leave_start_date == current_date else datetime.time.min
                leave_end_time_on_day = leave.EndDatetime.time() if leave_end_date == current_date else datetime.time.max

                # Convert slot times to datetime objects for comparison with leave datetimes
                slot_start_dt = datetime.datetime.combine(current_date, slot_start)
                slot_end_dt = datetime.datetime.combine(current_date, slot_end)
                
                leave_start_dt_on_day = datetime.datetime.combine(current_date, leave_start_time_on_day)
                leave_end_dt_on_day = datetime.datetime.combine(current_date, leave_end_time_on_day)

                # Check for overlap between leave and time slot
                if (slot_start_dt < leave_end_dt_on_day) and (slot_end_dt > leave_start_dt_on_day):
                    if slot_name not in monthly_availability[day_of_month]:
                        monthly_availability[day_of_month].append(slot_name)
            current_date += datetime.timedelta(days=1)
            
    return monthly_availability

def get_doctor_daily_availability(db: Session, doctor_id: int, date: datetime.date) -> dict:
    """
    Retrieves the availability of each time slot for a specific doctor on a given date,
    considering approved leaves and pending/confirmed appointments.
    Returns a dictionary where keys are time slot names (e.g., '07:00-09:00') and values are booleans (True for available, False for booked).
    """
    start_datetime = datetime.datetime.combine(date, datetime.time.min)
    end_datetime = datetime.datetime.combine(date, datetime.time.max)

    # Define the fixed time slots and initialize availability
    time_slots = {
        "07:00-09:00": (datetime.time(7, 0), datetime.time(9, 0)),
        "09:00-11:00": (datetime.time(9, 0), datetime.time(11, 0)),
        "13:00-15:00": (datetime.time(13, 0), datetime.time(15, 0)),
        "15:00-17:00": (datetime.time(15, 0), datetime.time(17, 0)),
    }
    daily_availability = {slot: True for slot in time_slots}

    # Check for appointments
    appointments = db.query(Appointment).filter(
        Appointment.DoctorId == doctor_id,
        Appointment.AppointmentDatetime >= start_datetime,
        Appointment.AppointmentDatetime <= end_datetime,
        Appointment.Status.in_(['pending', 'confirmed'])
    ).all()

    for appt in appointments:
        appt_time = appt.AppointmentDatetime.time()
        for slot_name, (slot_start, slot_end) in time_slots.items():
            if slot_start <= appt_time < slot_end:
                daily_availability[slot_name] = False
                break

    # Check for approved leaves
    leaves = db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.StartDatetime <= end_datetime,
        DoctorLeave.EndDatetime >= start_datetime,
        DoctorLeave.Status == 'approved'
    ).all()

    for leave in leaves:
        for slot_name, (slot_start, slot_end) in time_slots.items():
            # Create datetime objects for the slot on the given date
            slot_start_dt = datetime.datetime.combine(date, slot_start)
            slot_end_dt = datetime.datetime.combine(date, slot_end)

            # Check for overlap between the leave period and the time slot
            # Overlap exists if (LeaveStart < SlotEnd) and (LeaveEnd > SlotStart)
            if leave.StartDatetime < slot_end_dt and leave.EndDatetime > slot_start_dt:
                daily_availability[slot_name] = False
    
    return daily_availability
def get_doctor_leaves_for_month(db: Session, doctor_id: int, year: int, month: int) -> List[DoctorLeave]:
    """
    Retrieves all leave entries for a specific doctor for a given month and year.
    Considers leaves that are either 'approved' or 'pending'.
    """
    start_date = datetime.datetime(year, month, 1)
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    
    return db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.StartDatetime >= start_date,
        DoctorLeave.EndDatetime <= end_date,
        DoctorLeave.Status.in_(['approved', 'pending'])
    ).all()

def get_doctor_leaves_in_range(db: Session, doctor_id: int, start_date: datetime.date, end_date: datetime.date) -> List[DoctorLeave]:
    """
    Retrieves all approved or pending leave entries for a doctor within a given date range.
    """
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

    return db.query(DoctorLeave).filter(
        DoctorLeave.DoctorId == doctor_id,
        DoctorLeave.StartDatetime < end_datetime,
        DoctorLeave.EndDatetime > start_datetime,
        DoctorLeave.Status.in_(['approved', 'pending'])
    ).all()

def create_doctor_leave_entry(db: Session, doctor_id: int, start_datetime: datetime, end_datetime: datetime, reason: Optional[str], leave_type: str, status: str):
    db_leave = DoctorLeave(
        DoctorId=doctor_id,
        StartDatetime=start_datetime,
        EndDatetime=end_datetime,
        Reason=reason,
        LeaveType=leave_type,
        Status=status
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave