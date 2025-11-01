from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from pydantic import BaseModel

from DataAccessLayer import data_access
from BusinessLogicLayer import business_logic
import auth
from routers.patient import update_patient_profile

# Define a Pydantic model for the patient profile DTO
class PatientProfileDto(BaseModel):
    PatientId: int
    FullName: str
    Email: str
    Phone: str
    birth_date: Optional[datetime.date] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"]
)

router.include_router(update_patient_profile.router)

@router.get("/me", response_model=PatientProfileDto)
def get_patient_profile(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(data_access.get_db)):
    # The logic for checking role and fetching profile remains the same
    if current_user.role != "Patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Only for patients.")
    patient_profile = business_logic.get_patient_profile_logic(db, current_user.id)
    if not patient_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient_profile

