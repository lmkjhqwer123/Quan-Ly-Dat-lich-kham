


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from typing import List, Optional

import datetime
from routers import patient_router

from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv


from BusinessLogicLayer import business_logic

from DataAccessLayer import data_access

import auth
from routers.auth import auth_router
from routers.auth import update_password



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



class DoctorCreateRequest(BaseModel):

    FullName: str

    Email: str

    Phone: str

    SpecialtyId: int

    Qualifications: str

    Password: str



class DoctorUpdateRequest(BaseModel):

    FullName: str

    Email: str

    Phone: str

    SpecialtyId: int

    Qualifications: str



class DoctorDto(BaseModel):

    DoctorId: int

    FullName: str

    Email: str

    Phone: str

    SpecialtyId: int

    SpecialtyName: Optional[str] = None

    Qualifications: str



    class Config:

        from_attributes = True



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



app.mount("/GUI", StaticFiles(directory="PresentationLayer/GUI"), name="gui")
app.mount("/Js", StaticFiles(directory="PresentationLayer/Js"), name="js")
app.mount("/", StaticFiles(directory="PresentationLayer/GUI"), name="root_gui")

# --- API Endpoints ---







# --- Users Endpoints ---











# --- Doctors Endpoints ---



@app.get("/api/doctors", response_model=List[DoctorDto])

def get_all_doctors(db: Session = Depends(data_access.get_db)):

    return business_logic.get_all_doctors_logic(db)



@app.get("/api/doctors/{id}", response_model=DoctorDto, tags=["Doctors"])

def get_doctor_by_id(id: int, db: Session = Depends(data_access.get_db)):

    doctor = business_logic.get_doctor_by_id_logic(db, id)

    if doctor:

        return doctor

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bác sĩ.")



@app.post("/api/doctors", response_model=DoctorDto, status_code=status.HTTP_201_CREATED, tags=["Doctors"])

def create_new_doctor(request: DoctorCreateRequest, db: Session = Depends(data_access.get_db)):

    result = business_logic.create_new_doctor_logic(db, request.model_dump())

    if "error" in result:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result



@app.put("/api/doctors/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Doctors"])

def update_doctor_info(id: int, request: DoctorUpdateRequest, db: Session = Depends(data_access.get_db)):

    result = business_logic.update_doctor_info_logic(db, id, request.model_dump())

    if result and "error" in result:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    if not result:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bác sĩ.")

    return



@app.delete("/api/doctors/{id}", tags=["Doctors"])

def delete_doctor_by_id(id: int, db: Session = Depends(data_access.get_db)):

    result = business_logic.delete_doctor_by_id_logic(db, id)

    if "error" in result:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result



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




