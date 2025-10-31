from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from DataAccessLayer import data_access
from BusinessLogicLayer import business_logic
import auth

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)

# --- Pydantic Models (DTOs) for Patients ---
class BookAppointmentDto(BaseModel):
    DoctorId: int
    SpecialtyId: int
    AppointmentDatetime: datetime.datetime
    Symptoms: str

class AppointmentHistoryDto(BaseModel):
    AppointmentId: int
    AppointmentDatetime: datetime.datetime
    Status: str
    DoctorName: Optional[str] = None
    SpecialtyName: Optional[str] = None
    Symptoms: str

class PatientUpdateRequest(BaseModel):
    FullName: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    address: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_password: str

# --- Patient API Endpoints ---
@router.put("/me", status_code=status.HTTP_204_NO_CONTENT)
def update_patient_profile(
    request: PatientUpdateRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    result = business_logic.update_patient_profile_logic(db, current_user.id, request.model_dump())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return

@router.put("/users/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    request: PasswordUpdateRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    result = business_logic.update_user_password_logic(db, current_user.id, current_user.role, request.model_dump())
    if result and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return

@router.post("/{patient_id}/appointments")
def book_appointment_for_patient(patient_id: int, booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db)):
    result = business_logic.book_appointment_logic(db, patient_id, booking_dto.model_dump())
    return result

@router.post("/me/appointments")
def book_appointment_for_me(booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    result = business_logic.book_appointment_logic(db, current_user.PatientId, booking_dto.model_dump())
    return result

@router.get("/me/history", response_model=List[AppointmentHistoryDto])
def get_my_history(db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    return business_logic.get_my_history_logic(db, current_user.PatientId)