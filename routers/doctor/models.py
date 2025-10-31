from pydantic import BaseModel
from typing import Optional, List

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
