
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from DataAccessLayer import data_access

SECRET_KEY = "your-secret-key"  # Replace with a strong, secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class TokenData(BaseModel):
    id: int | None = None
    role: str | None = None

def create_access_token(data: dict):
    to_encode = data.copy()
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
    
    if token_data.role == "Patient":
        user.id = user.PatientId
    elif token_data.role == "Doctor":
        user.id = user.DoctorId
    elif token_data.role == "Admin":
        user.id = user.AdminId
        
    user.role = token_data.role
    return user
