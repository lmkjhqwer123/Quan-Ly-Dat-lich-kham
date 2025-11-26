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

@router.get("/me/appointments/history", response_model=List[AppointmentHistoryDto])
def get_appointment_history(db: Session = Depends(data_access.get_db), current_user = Depends(auth.get_current_user)):
    """
    Lấy lịch sử đặt lịch khám của bệnh nhân đang đăng nhập
    - Sắp xếp theo thời gian mới nhất trước
    - Bao gồm thông tin bác sĩ, khoa, triệu chứng, trạng thái
    """
    try:
        history = business_logic.get_my_history_logic(db, current_user.PatientId)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy lịch sử đặt lịch: {str(e)}"
        )
