
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from DataAccessLayer import data_access

import os

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set. Please set a strong, random key.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30  # Change to 30 days
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class TokenData(BaseModel):
    id: int | None = None
    role: str | None = None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_password_reset_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(data_access.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    user = None
    if token_data.role == "Patient":
        user = data_access.get_patient_by_id(db, patient_id=token_data.id)
    elif token_data.role == "Doctor":
        user = data_access.get_doctor_by_id(db, doctor_id=token_data.id)
    elif token_data.role == "Admin":
        user = data_access.get_admin_by_id(db, admin_id=token_data.id)

    if user is None:
        raise credentials_exception
    
    # Add role and id to the user object itself for consistent access
    user.role = token_data.role
    if hasattr(user, 'PatientId'):
        user.id = user.PatientId
    elif hasattr(user, 'DoctorId'):
        user.id = user.DoctorId
    elif hasattr(user, 'AdminId'):
        user.id = user.AdminId
    else:
        user.id = token_data.id # Fallback

    return user

def get_current_admin_user(current_user = Depends(get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized, admin role required")
    return current_user
