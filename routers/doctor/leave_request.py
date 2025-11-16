from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import datetime

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter()

class LeaveScheduleItem(BaseModel):
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class DoctorLeaveRequest(BaseModel):
    leave_type: str
    description: Optional[str] = None
    schedules: List[LeaveScheduleItem]

class DoctorLeaveResponse(BaseModel):
    leave_id: int
    doctor_id: int
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    reason: Optional[str] = None
    leave_type: str
    status: str

    class Config:
        from_attributes = True

@router.post("/leave-request", response_model=List[DoctorLeaveResponse], status_code=status.HTTP_201_CREATED)
def submit_doctor_leave(
    leave_request: DoctorLeaveRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Allows a doctor to submit a leave request for one or more days/time slots.
    """
    if current_user.role != "Doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can submit leave requests")
    
    doctor_id = current_user.id
    
    try:
        created_leaves = business_logic.submit_doctor_leave_request_logic(
            db,
            doctor_id,
            leave_request.leave_type,
            leave_request.description,
            leave_request.schedules
        )
        return created_leaves
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
