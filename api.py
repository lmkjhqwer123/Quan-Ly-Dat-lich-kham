


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel, Field



from sqlalchemy.orm import Session



from typing import List, Optional



import datetime

from routers import patient_router, doctor_router, specialty_router



from fastapi.staticfiles import StaticFiles



from dotenv import load_dotenv





from BusinessLogicLayer import business_logic



from DataAccessLayer import data_access



import auth

from routers.auth import auth_router

from routers.auth import update_password

from routers.admin import dashboard_stats

from routers.admin import patient_management

from routers.doctor.models import DoctorCreateRequest, DoctorUpdateRequest, DoctorDto





load_dotenv()  # Load environment variables from .env file







app = FastAPI(



    title="QuanLyKhamBenh API",



    description="API for managing appointments in a hospital.",



    version="1.0.0",

    docs_url="/api/docs",

    redoc_url="/api/redoc"



)







# --- Pydantic Models (DTOs) ---







class Token(BaseModel):



    access_token: str



    token_type: str







class LoginRequest(BaseModel):



    Phone: Optional[str] = None



    Username: Optional[str] = None



    Password: str







class PasswordResetRequest(BaseModel):



    email: str







class PasswordReset(BaseModel):



    token: str



    new_password: str











class PatientCreateRequest(BaseModel):



    FullName: str



    Email: str



    Phone: str



    Password: str



    birth_date: Optional[datetime.date] = None



    address: Optional[str] = None







class RegisterRequest(BaseModel):



    role: str = Field(..., pattern="^(patient|doctor)$")



    patient_data: Optional[PatientCreateRequest] = None



    doctor_data: Optional[DoctorCreateRequest] = None







class BookAppointmentDto(BaseModel):



    DoctorId: int



    SpecialtyId: int



    AppointmentDatetime: datetime.datetime



    Symptoms: str







class AppointmentHistoryDto(BaseModel):



    AppointmentId: int



    AppointmentDatetime: datetime.datetime



    Status: str



    DoctorName: Optional[str] = None



    SpecialtyName: Optional[str] = None



    Symptoms: str







class PatientUpdateRequest(BaseModel):



    FullName: Optional[str] = None



    Email: Optional[str] = None



    Phone: Optional[str] = None



    address: Optional[str] = None







class PasswordUpdateRequest(BaseModel):



    current_password: str



    new_password: str







app.include_router(patient_router.router)

app.include_router(auth_router.router)

app.include_router(update_password.router)

app.include_router(dashboard_stats.router)

app.include_router(patient_management.router)

app.include_router(doctor_router.router, prefix="/api")

app.include_router(specialty_router.router, prefix="/api")





app.mount("/GUI", StaticFiles(directory="PresentationLayer/GUI"), name="gui")

app.mount("/Js", StaticFiles(directory="PresentationLayer/Js"), name="js")

app.mount("/", StaticFiles(directory="PresentationLayer/GUI"), name="root_gui")



# --- API Endpoints ---



















# --- Users Endpoints ---







































@app.post("/api/patients/{patient_id}/appointments", tags=["Patients"])



def book_appointment_for_patient(patient_id: int, booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db)):



    result = business_logic.book_appointment_logic(db, patient_id, booking_dto.model_dump())



    return result











@app.post("/api/patients/me/appointments", tags=["Patients"])



def book_appointment_for_me(booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):



    result = business_logic.book_appointment_logic(db, current_user.PatientId, booking_dto.model_dump())



    return result











@app.get("/api/patients/me/history", response_model=List[AppointmentHistoryDto], tags=["Patients"])



def get_my_history(db: Session = Depends(data_access.get_db), current_user: dict = Depends(auth.get_current_user)):



    return business_logic.get_my_history_logic(db, current_user.PatientId)
















