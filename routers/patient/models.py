from pydantic import BaseModel, Field, ValidationError, validator
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
    current_password: str = Field(..., min_length=1, strip_whitespace=True, description="Current password cannot be empty")
    new_password: str = Field(..., min_length=1, strip_whitespace=True, description="New password cannot be empty")
    confirm_new_password: str = Field(..., min_length=1, strip_whitespace=True, description="Confirm new password cannot be empty")

    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
