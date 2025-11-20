from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from pydantic import BaseModel # Import BaseModel

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    tags=["Doctor Appointments"]
)

class AppointmentStatusUpdate(BaseModel):
    status: str

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

@router.put("/appointments/{appointment_id}/status", response_model=dict)
def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Update the status of a specific appointment.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update appointment status.")
    
    doctor_id = current_user.id
    updated_appointment = business_logic.update_appointment_status_logic(
        db, 
        doctor_id=doctor_id, 
        appointment_id=appointment_id, 
        new_status=status_update.status
    )
    if "error" in updated_appointment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_appointment["error"])
    if not updated_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found or not associated with this doctor.")
    return {"message": "Appointment status updated successfully", "appointment_id": appointment_id, "new_status": status_update.status}

