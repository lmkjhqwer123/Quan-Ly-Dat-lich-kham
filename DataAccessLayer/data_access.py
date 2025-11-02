
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import bcrypt
import datetime
from typing import Optional

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
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    specialty = relationship("Specialty")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_role = Column(String(50), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# --- Data Access Functions ---

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
def get_all_doctors(db):
    return db.query(Doctor).all()

def get_doctor_by_id(db, doctor_id: int):
    return db.query(Doctor).filter(Doctor.DoctorId == doctor_id).first()

def get_doctor_by_email(db, email: str):
    return db.query(Doctor).filter(Doctor.Email == email).first()

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
def get_all_specialties(db):
    return db.query(Specialty).all()

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
    db_appointment = Appointment(**appointment_data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments_by_patient_id(db, patient_id: int):
    return db.query(Appointment).filter(Appointment.PatientId == patient_id).all()

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
