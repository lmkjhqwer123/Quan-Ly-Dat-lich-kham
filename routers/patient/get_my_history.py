from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth
from routers.patient.models import AppointmentHistoryDto

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)

@router.get("/me/history", response_model=List[AppointmentHistoryDto])
def get_my_history(db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):
    return business_logic.get_my_history_logic(db, current_user.PatientId)
