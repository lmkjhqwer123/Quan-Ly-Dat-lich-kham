from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

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
