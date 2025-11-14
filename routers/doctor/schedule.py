from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import auth
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access

router = APIRouter()

def get_current_doctor_user(current_user = Depends(auth.get_current_user)):
    if current_user.role != "Doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/schedule", response_model=List[dict])
def get_doctor_schedule(
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(get_current_doctor_user)
):
    """
    API endpoint to get the schedule for the currently logged-in doctor.
    """
    schedule = business_logic.get_doctor_schedule_logic(db, doctor_id=current_user.id)
    return schedule
