from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.doctor.models import DoctorDto, DoctorUpdateRequest
from auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=DoctorDto)
def get_doctor_profile(current_user = Depends(get_current_user), db: Session = Depends(data_access.get_db)):
    """
    Get the profile of the currently authenticated doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can access this profile.")
    
    doctor_id = current_user.id
    db_doctor = business_logic.get_doctor_profile_logic(db, doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")
    return db_doctor

@router.put("/profile", response_model=DoctorDto)
def update_doctor_profile(
    doctor_request: DoctorUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(data_access.get_db)
):
    """
    Update the profile of the currently authenticated doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update their profile.")
    
    doctor_id = current_user.id
    db_doctor = business_logic.update_doctor(db, doctor_id, doctor_request)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found.")
    return db_doctor
