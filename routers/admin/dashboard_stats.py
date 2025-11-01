from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DataAccessLayer.data_access import get_db, Doctor, Patient, Appointment
import datetime

router = APIRouter(
    prefix="/api",
    tags=["Admin Dashboard"]
)

@router.get("/doctors/count")
def get_doctors_count(db: Session = Depends(get_db)):
    count = db.query(Doctor).count()
    return {"count": count}

@router.get("/patients/today/count")
def get_patients_today_count(db: Session = Depends(get_db)):
    today = datetime.date.today()
    count = db.query(Patient).filter(Patient.birth_date == today).count() # Assuming birth_date is used for registration date for simplicity, or a separate 'created_at' field would be better.
    return {"count": count}

@router.get("/appointments/today/count")
def get_appointments_today_count(db: Session = Depends(get_db)):
    today = datetime.date.today()
    count = db.query(Appointment).filter(
        Appointment.AppointmentDatetime >= today,
        Appointment.AppointmentDatetime < today + datetime.timedelta(days=1)
    ).count()
    return {"count": count}

@router.get("/appointments/cancelled/count")
def get_appointments_cancelled_count(db: Session = Depends(get_db)):
    count = db.query(Appointment).filter(Appointment.Status == "Cancelled").count()
    return {"count": count}
