from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.specialty.models import SpecialtyDto
from routers.doctor_router import DoctorDto

router = APIRouter(
    prefix="/api",
    tags=["Public"]
)

@router.get("/specialties/", response_model=List[SpecialtyDto])
def get_all_specialties(db: Session = Depends(data_access.get_db)):
    """
    Get all specialties.
    """
    return business_logic.get_all_specialties_logic(db)

@router.get("/doctors/", response_model=List[DoctorDto])
def get_all_doctors(
    db: Session = Depends(data_access.get_db),
    sort_speciality: Optional[int] = None
):
    """
    Get all doctors with optional filtering by specialty.
    """
    return business_logic.get_all_doctors_logic(db, sort_speciality=sort_speciality)
