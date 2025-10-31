from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.doctor.models import DoctorDto

router = APIRouter()

@router.get("/doctors/{doctor_id}", response_model=DoctorDto)
def get_doctor(doctor_id: int, db: Session = Depends(data_access.get_db)):
    """
    Get a doctor by ID.
    """
    db_doctor = business_logic.get_doctor(db, doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor
