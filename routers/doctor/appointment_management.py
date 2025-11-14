from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    tags=["Doctor Appointments"]
)

@router.get("/appointments/me", response_model=List[dict])
def get_my_appointments(
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user),
    query: Optional[str] = None,
    sort_direction: Optional[str] = None,
    sort_by: Optional[str] = None,
    status: Optional[str] = None,
    exam_date: Optional[datetime.date] = Query(None, description="Date for which to retrieve appointments (YYYY-MM-DD)")
):
    """
    Get a list of appointments for the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view their appointments.")
    
    doctor_id = current_user.id
    appointments = business_logic.get_doctor_appointments_logic(
        db, 
        doctor_id=doctor_id,
        search=query,
        sort_direction=sort_direction,
        sort_by=sort_by,
        appointment_status=status,
        appointment_date=exam_date
    )
    return appointments

@router.get("/appointments/{appointment_id}", response_model=dict)
def get_my_appointment_details(
    appointment_id: int,
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Get details of a specific appointment for the logged-in doctor.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view appointment details.")
    
    doctor_id = current_user.id
    appointment = business_logic.get_doctor_appointment_by_id_logic(db, doctor_id, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found or not associated with this doctor.")
    return appointment
