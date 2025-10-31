
from fastapi import FastAPI, Depends, HTTPException, status

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from typing import List, Optional

import datetime

from fastapi.staticfiles import StaticFiles



from BusinessLogicLayer import business_logic

from DataAccessLayer import data_access



app = FastAPI(

    title="QuanLyKhamBenh API",

    description="API for managing appointments in a hospital.",

    version="1.0.0"

)



# --- Pydantic Models (DTOs) ---

class LoginRequest(BaseModel):

    Phone: Optional[str] = None

    Username: Optional[str] = None

    Password: str



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



# --- API Endpoints ---



@app.post("/api/auth/login", tags=["Auth"])

def login(login_request: LoginRequest, db: Session = Depends(data_access.get_db)):

    user = business_logic.login_user(db, login_request.model_dump())

    if user:

        return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Thông tin đăng nhập không đúng.")



@app.get("/api/doctors", response_model=List[DoctorDto], tags=["Doctors"])

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

    # Note: In a real app, you'd verify the logged-in user has permission to do this.

    result = business_logic.book_appointment_logic(db, patient_id, booking_dto.model_dump())

    return result



@app.post("/api/patients/me/appointments", tags=["Patients"])

def book_appointment_for_me(booking_dto: BookAppointmentDto, db: Session = Depends(data_access.get_db)):

    # Note: This requires authentication to get the current user's ID.

    # Hardcoding patient_id=1 for demonstration as authentication is not fully implemented here.

    current_patient_id = 1 

    result = business_logic.book_appointment_logic(db, current_patient_id, booking_dto.model_dump())

    return result



@app.get("/api/patients/me/history", response_model=List[AppointmentHistoryDto], tags=["Patients"])

def get_my_history(db: Session = Depends(data_access.get_db)):

    # Note: This requires authentication to get the current user's ID.

    # Hardcoding patient_id=1 for demonstration.

    current_patient_id = 1

    return business_logic.get_my_history_logic(db, current_patient_id)



app.mount("/", StaticFiles(directory="PresentationLayer"), name="presentation")


