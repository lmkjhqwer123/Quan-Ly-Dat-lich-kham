from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.doctor.models import DoctorUpdateRequest, DoctorDto

router = APIRouter()

@router.put("/doctors/{doctor_id}", response_model=DoctorDto)
def update_doctor(doctor_id: int, doctor_request: DoctorUpdateRequest, db: Session = Depends(data_access.get_db)):
    """
    Update a doctor.
    """
    db_doctor = business_logic.update_doctor(db, doctor_id, doctor_request)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor
