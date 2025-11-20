from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth
from routers.patient.models import BookAppointmentDto
import secrets

router = APIRouter(
    tags=["Patients"]
)

@router.post("/me/appointments")
def book_appointment_for_me(booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db), current_user = Depends(auth.get_current_user)):
    # Generate a unique booking code
    booking_code = secrets.token_urlsafe(8)

    result = business_logic.book_appointment_logic(db, current_user.PatientId, booking_dto.model_dump(), booking_code)
    return result
