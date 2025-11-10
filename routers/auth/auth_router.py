from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import datetime

from DataAccessLayer import data_access
from BusinessLogicLayer import business_logic
import auth

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)

# --- Pydantic Models (DTOs) for Auth ---
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

class DoctorCreateRequest(BaseModel):
    FullName: str
    Email: str
    Phone: str
    SpecialtyId: int
    Qualifications: str
    Password: str

class RegisterRequest(BaseModel):
    role: str = Field(..., pattern="^(patient|doctor)$")
    patient_data: Optional[PatientCreateRequest] = None
    doctor_data: Optional[DoctorCreateRequest] = None


# --- Auth API Endpoints ---
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(data_access.get_db)):
    user = business_logic.login_user(db, {"Phone": form_data.username, "Password": form_data.password})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"user_id": user['userId'], "role": user['role']}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
def login(login_request: LoginRequest, db: Session = Depends(data_access.get_db)):
    user = business_logic.login_user(db, login_request.model_dump())

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"user_id": user['userId'], "role": user['role']}
    )
    
    user_role = user['role'].lower()
    if user_role == 'admin':
        redirect_url = "/admin.html"
    elif user_role == 'doctor':
        redirect_url = "/doctor.html"
    else:
        redirect_url = "/home.html"
    
    return {"access_token": access_token, "token_type": "bearer", "user": user, "redirect_url": redirect_url}

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(request: RegisterRequest, db: Session = Depends(data_access.get_db)):
    result = business_logic.register_user(db, request.model_dump())
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result["error"]
        )
    return result

@router.post("/request-password-reset")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(data_access.get_db)):
    result = business_logic.request_password_reset_logic(db, request.email)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result

@router.post("/reset-password")
def reset_password(request: PasswordReset, db: Session = Depends(data_access.get_db)):
    result = business_logic.reset_password_logic(db, request.token, request.new_password)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result