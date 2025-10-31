from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.doctor.models import DoctorCreateRequest, DoctorDto

router = APIRouter()

@router.post("/doctors/", response_model=DoctorDto, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_request: DoctorCreateRequest, db: Session = Depends(data_access.get_db)):
    """
    Create a new doctor.
    """
    return business_logic.create_doctor(db, doctor_request)
