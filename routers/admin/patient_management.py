from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from DataAccessLayer.data_access import get_db, Patient, hash_password # Import hash_password
from pydantic import BaseModel
import BusinessLogicLayer.business_logic as business_logic
from auth import get_current_user

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Patient Management"]
)

class PatientDto(BaseModel):
    PatientId: int
    FullName: str
    Email: str
    Phone: str
    birth_date: Optional[datetime.date] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

class PatientCreateDto(BaseModel):
    FullName: str
    Email: str
    Phone: str
    password: str  # Add password field
    birth_date: Optional[datetime.date] = None
    address: Optional[str] = None

@router.get("/patients/{patient_id}", response_model=PatientDto)
def get_patient_by_id(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = business_logic.get_patient_profile_logic(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

@router.post("/patients", response_model=PatientDto, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreateDto, db: Session = Depends(get_db)):
    hashed_password = hash_password(patient.password) # Use the imported hash_password function

    db_patient = Patient(
        FullName=patient.FullName,
        Email=patient.Email,
        Phone=patient.Phone,
        PasswordHash=hashed_password, # Corrected to PasswordHash
        birth_date=patient.birth_date,
        address=patient.address
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/patients", response_model=List[PatientDto])
def get_all_patients(
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    if current_user.role == "Doctor":
        # If the user is a doctor, get only their patients
        patients = business_logic.get_patients_for_doctor_logic(db, current_user.id, query, sort_by, sort_direction)
    else:
        # For other roles (like Admin), get all patients
        if query:
            patients = business_logic.search_patients_logic(db, query, sort_by, sort_direction)
        else:
            patients = business_logic.get_all_patients_logic(db, sort_by, sort_direction)
    return patients
