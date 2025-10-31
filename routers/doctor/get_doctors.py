from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.doctor.models import DoctorDto

router = APIRouter()

@router.get("/doctors/", response_model=List[DoctorDto])
def get_doctors(db: Session = Depends(data_access.get_db)):
    """
    Get all doctors.
    """
    return business_logic.get_doctors(db)
