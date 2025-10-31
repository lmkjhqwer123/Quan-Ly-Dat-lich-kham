from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.patient.models import BookAppointmentDto

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)

@router.post("/{patient_id}/appointments")
def book_appointment_for_patient(patient_id: int, booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db)):
    result = business_logic.book_appointment_logic(db, patient_id, booking_dto.model_dump())
    return result
