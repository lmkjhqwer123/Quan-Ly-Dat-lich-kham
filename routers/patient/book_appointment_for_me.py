from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth
from routers.patient.models import BookAppointmentDto

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)

@router.post("/me/appointments")
def book_appointment_for_me(booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    result = business_logic.book_appointment_logic(db, current_user.PatientId, booking_dto.model_dump())
    return result
