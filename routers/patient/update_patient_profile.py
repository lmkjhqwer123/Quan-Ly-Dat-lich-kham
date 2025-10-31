from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth
from routers.patient.models import PatientUpdateRequest

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)

@router.put("/me", status_code=status.HTTP_204_NO_CONTENT)
def update_patient_profile(
    request: PatientUpdateRequest,
    db: Session = Depends(data_access.get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    result = business_logic.update_patient_profile_logic(db, current_user.id, request.model_dump())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return
