from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from pydantic import BaseModel

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Schedule"]
)

class DoctorLeaveDto(BaseModel):
    leave_id: int
    doctor_name: str
    specialty_name: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    reason: str
    leave_type: str
    status: str

    class Config:
        from_attributes = True

@router.get("/leave-requests", response_model=List[DoctorLeaveDto])
def get_all_leave_requests(
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_admin_user),
    status: Optional[str] = None,
    leave_date: Optional[datetime.date] = None
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view leave requests")
    
    leaves = business_logic.get_all_doctor_leaves_logic(db, status=status, leave_date=leave_date)
    return leaves
