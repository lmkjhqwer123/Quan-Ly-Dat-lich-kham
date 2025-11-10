from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime
from routers.patient_router import PatientProfileDto
from routers.doctor import patient_management
from routers.doctor import appointment_management # Import the new router

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(prefix="/api/doctor")
router.include_router(patient_management.router)
router.include_router(appointment_management.router) # Include the new router

class DoctorCreateRequest(BaseModel):
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    Qualifications: str
    Password: str

class DoctorUpdateRequest(BaseModel):
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    Qualifications: str

class DoctorDto(BaseModel):
    DoctorId: int
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    SpecialtyName: Optional[str] = None
    Qualifications: str

    class Config:
        from_attributes = True

class AppointmentToday(BaseModel):
    AppointmentId: int
    PatientName: str
    AppointmentTime: str
    Status: str

class ExaminationQueueItem(BaseModel):
    AppointmentId: int
    PatientName: str
    AppointmentTime: str
    Status: str

class DoctorDashboardResponse(BaseModel):
    appointments_today: List[AppointmentToday]
    examination_queue: List[ExaminationQueueItem]

class DoctorAppointmentOut(BaseModel):
    AppointmentId: int
    AppointmentDatetime: datetime.datetime
    Status: str
    PatientName: Optional[str] = None
    SpecialtyName: Optional[str] = None
    Symptoms: str
    BookingCode: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/doctors/", response_model=DoctorDto, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_request: DoctorCreateRequest, db: Session = Depends(data_access.get_db), admin: dict = Depends(auth.get_current_admin_user)):
    """
    Create a new doctor. Admin access required.
    """
    return business_logic.create_new_doctor_logic(db, doctor_request.model_dump())

@router.get("/doctors/", response_model=List[DoctorDto])
def get_all_doctors(
    db: Session = Depends(data_access.get_db), 
    admin: dict = Depends(auth.get_current_admin_user),
    search: Optional[str] = None,
    sort_direction: Optional[str] = None,
    sort_value: Optional[str] = None,
    sort_status: Optional[str] = None,
    sort_speciality: Optional[int] = None,
    sort_room: Optional[str] = None,
    limit: Optional[int] = None
):
    """
    Get all doctors with optional filtering and sorting. Admin access required.
    """
    return business_logic.get_all_doctors_logic(
        db, 
        search=search,
        sort_direction=sort_direction,
        sort_value=sort_value,
        sort_status=sort_status,
        sort_speciality=sort_speciality,
        sort_room=sort_room,
        limit=limit
    )

@router.get("/doctors/{doctor_id}", response_model=DoctorDto)
def get_doctor(doctor_id: int, db: Session = Depends(data_access.get_db)):
    """
    Get a doctor by ID.
    """
    db_doctor = business_logic.get_doctor_by_id_logic(db, doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.put("/doctors/{doctor_id}", response_model=DoctorDto)
def update_doctor(doctor_id: int, doctor_request: DoctorUpdateRequest, db: Session = Depends(data_access.get_db), admin: dict = Depends(auth.get_current_admin_user)):
    """
    Update a doctor. Admin access required.
    """
    db_doctor = business_logic.update_doctor_info_logic(db, doctor_id, doctor_request.model_dump())
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(data_access.get_db), admin: dict = Depends(auth.get_current_admin_user)):
    """
    Delete a doctor. Admin access required.
    """
    success = business_logic.delete_doctor_by_id_logic(db, doctor_id)
    if "error" in success:
        raise HTTPException(status_code=404, detail=success["error"])
    return {"ok": True}

@router.get("/doctor/appointments", response_model=List[DoctorAppointmentOut])
def get_doctor_appointments(
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "desc",
    appointment_status: Optional[str] = None,
    limit: Optional[int] = None
):
    """
    Get all appointments for the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their appointments")
    
    doctor_id = current_user.id
    return business_logic.get_doctor_appointments_logic(
        db, 
        doctor_id=doctor_id,
        search=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        appointment_status=appointment_status,
        limit=limit
    )

@router.get("/doctor/appointments/{appointment_id}", response_model=DoctorAppointmentOut)
def get_doctor_appointment_by_id(
    appointment_id: int,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Get a specific appointment for the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their appointments")
    
    doctor_id = current_user.id
    appointment = business_logic.get_doctor_appointment_by_id_logic(db, doctor_id, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found or does not belong to this doctor")
    return appointment

@router.get("/doctor/examination-queue", response_model=List[ExaminationQueueItem])
def get_doctor_examination_queue(
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = "asc",
    appointment_statuses: Optional[str] = Query(None, description="Comma-separated list of appointment statuses"),
    appointment_date: Optional[datetime.date] = Query(None, description="Filter by appointment date (YYYY-MM-DD)"),
    limit: Optional[int] = None
):
    """
    Get the examination queue for the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their examination queue")
    
    doctor_id = current_user.id
    return business_logic.get_doctor_examination_queue_logic(
        db, 
        doctor_id=doctor_id,
        search=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        appointment_statuses=appointment_statuses,
        appointment_date=appointment_date,
        limit=limit
    )

class DoctorProfileUpdateRequest(BaseModel):
    FullName: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    SpecialtyId: Optional[int] = None
    Qualifications: Optional[str] = None

@router.get("/doctor/profile", response_model=DoctorDto)
def get_doctor_profile(
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Get the profile of the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their own profile")
    
    doctor_id = current_user.id
    doctor_profile = business_logic.get_doctor_profile_logic(db, doctor_id)
    if not doctor_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return doctor_profile

@router.put("/doctor/profile", response_model=DoctorDto)
def update_doctor_profile(
    profile_update: DoctorProfileUpdateRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Update the profile of the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update their own profile")
    
    doctor_id = current_user.id
    updated_profile = business_logic.update_doctor_profile_logic(db, doctor_id, profile_update.model_dump(exclude_unset=True))
    if "error" in updated_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_profile["error"])
    if not updated_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return updated_profile
