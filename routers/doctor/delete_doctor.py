from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access

router = APIRouter()

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(data_access.get_db)):
    """
    Delete a doctor.
    """
    success = business_logic.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"ok": True}
