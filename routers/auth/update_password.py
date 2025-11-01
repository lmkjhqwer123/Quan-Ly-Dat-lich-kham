from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth
from routers.patient.models import PasswordUpdateRequest

router = APIRouter(
    prefix="/api",
    tags=["Patients"],
)

@router.put("/users/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    request: PasswordUpdateRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    result = business_logic.update_user_password_logic(db, current_user.id, current_user.role, request.model_dump())
    if result and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return
