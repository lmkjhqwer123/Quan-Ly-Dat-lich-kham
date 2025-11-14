from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime

from BusinessLogicLayer import business_logic
from BusinessLogicLayer.business_logic import AppointmentStatus
from DataAccessLayer import data_access
import auth

router = APIRouter(
    tags=["Doctor Patients"]
)

class DoctorPatientDto(BaseModel):
    PatientId: int
    FullName: str
    Email: str
    Phone: str
    birth_date: Optional[datetime.date] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/patients/me", response_model=List[DoctorPatientDto])
def get_my_patients(
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user),
    query: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
    limit: Optional[int] = None
):
    doctor_id = current_user.id
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their patients.")
    patients = business_logic.get_patients_for_doctor_logic(
        db, 
        doctor_id=doctor_id,
        search_query=query,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit
    )
    return patients

@router.get("/patients/{patient_id}", response_model=DoctorPatientDto)
def get_patient_details_for_doctor(
    patient_id: int,
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Get details of a specific patient associated with the logged-in doctor.
    """
    
    doctor_id = current_user.id
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their patients.")
    patient = business_logic.get_patient_details_for_doctor_logic(db, doctor_id, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found or not associated with this doctor.")
    return patient

@router.get("/examination-queue", response_model=List[dict])
def get_doctor_examination_queue(
    appointment_statuses: str = Query(..., description="Comma-separated list of appointment statuses (e.g., 'confirmed,pending')"),
    appointment_date: Optional[datetime.date] = Query(None, description="Date for which to retrieve the examination queue (YYYY-MM-DD)"),
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Retrieve the examination queue for the logged-in doctor based on appointment statuses and date.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their examination queue.")
    
    doctor_id = current_user.id
    statuses = [AppointmentStatus[s.strip().upper()] for s in appointment_statuses.split(',')]
    
    queue = business_logic.get_doctor_examination_queue_logic(db, doctor_id, statuses, appointment_date)
    return queue

