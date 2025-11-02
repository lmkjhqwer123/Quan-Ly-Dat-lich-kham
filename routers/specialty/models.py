from pydantic import BaseModel
from typing import Optional

class SpecialtyCreateRequest(BaseModel):
    Name: str
    description: Optional[str] = None

class SpecialtyUpdateRequest(BaseModel):
    Name: Optional[str] = None
    description: Optional[str] = None

class SpecialtyDto(BaseModel):
    SpecialtyId: int
    Name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
