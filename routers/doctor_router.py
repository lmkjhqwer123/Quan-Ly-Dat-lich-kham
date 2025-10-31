from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access

router = APIRouter()

class DoctorCreateRequest(BaseModel):
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    Qualifications: str
    Password: str

class DoctorUpdateRequest(BaseModel):
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    Qualifications: str

class DoctorDto(BaseModel):
    DoctorId: int
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    SpecialtyName: Optional[str] = None
    Qualifications: str

    class Config:
        from_attributes = True

@router.post("/doctors/", response_model=DoctorDto, status_code=status.HTTP_201_CREATED)
def create_doctor(doctor_request: DoctorCreateRequest, db: Session = Depends(data_access.get_db)):
    """
    Create a new doctor.
    """
    return business_logic.create_doctor(db, doctor_request)

@router.get("/doctors/", response_model=List[DoctorDto])
def get_doctors(db: Session = Depends(data_access.get_db)):
    """
    Get all doctors.
    """
    return business_logic.get_doctors(db)

@router.get("/doctors/{doctor_id}", response_model=DoctorDto)
def get_doctor(doctor_id: int, db: Session = Depends(data_access.get_db)):
    """
    Get a doctor by ID.
    """
    db_doctor = business_logic.get_doctor(db, doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.put("/doctors/{doctor_id}", response_model=DoctorDto)
def update_doctor(doctor_id: int, doctor_request: DoctorUpdateRequest, db: Session = Depends(data_access.get_db)):
    """
    Update a doctor.
    """
    db_doctor = business_logic.update_doctor(db, doctor_id, doctor_request)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(data_access.get_db)):
    """
    Delete a doctor.
    """
    success = business_logic.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"ok": True}
