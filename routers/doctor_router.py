from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter()

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
