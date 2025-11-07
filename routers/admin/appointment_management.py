from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from pydantic import BaseModel

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Appointments"]
)

class ServiceDto(BaseModel):
    id: int
    name: str
    quantity: int

class AdminAppointmentDto(BaseModel):
    AppointmentId: int
    AppointmentDatetime: datetime.datetime
    Status: str
    DoctorName: Optional[str] = None
    SpecialtyName: Optional[str] = None
    Symptoms: str
    PatientName: Optional[str] = None
    Services: List[ServiceDto] = []

    class Config:
        from_attributes = True

@router.get("/appointments", response_model=List[AdminAppointmentDto])
def get_all_appointments(db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all appointments")
    return business_logic.get_all_appointments_logic(db)

@router.get("/appointments/{appointment_id}", response_model=AdminAppointmentDto)
def get_appointment_by_id(appointment_id: int, db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view appointment details")
    
    appointment = business_logic.get_appointment_by_id_logic(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment