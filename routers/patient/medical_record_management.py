from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    tags=["Patients"],
)

@router.get("/me/medical-records/{appointment_id}")
def get_my_medical_record_details(
    appointment_id: int,
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    # Debug: Log current_user info
    print(f"DEBUG: current_user type = {type(current_user)}")
    print(f"DEBUG: current_user = {current_user}")
    print(f"DEBUG: hasattr PatientId = {hasattr(current_user, 'PatientId')}")
    if hasattr(current_user, 'PatientId'):
        print(f"DEBUG: current_user.PatientId = {current_user.PatientId}")
    
    # current_user là object Patient, không phải dict
    if not hasattr(current_user, 'PatientId'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access their medical records."
        )
    
    patient_id = current_user.PatientId
    print(f"DEBUG: patient_id for check = {patient_id}, appointment_id = {appointment_id}")

    try:
        medical_record_details = business_logic.get_medical_record_details_logic(db, appointment_id, patient_id)
        return medical_record_details
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/me/medical-records")
def get_my_medical_records(
    db: Session = Depends(data_access.get_db),
    current_user = Depends(auth.get_current_user)
):
    # current_user là object Patient, không phải dict
    if not hasattr(current_user, 'PatientId'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access their medical records."
        )
    
    patient_id = current_user.PatientId

    try:
        medical_records = business_logic.get_medical_records_for_patient_logic(db, patient_id)
        return medical_records
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
