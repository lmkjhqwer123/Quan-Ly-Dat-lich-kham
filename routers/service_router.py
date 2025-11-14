from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
import auth

router = APIRouter(
    prefix="/api",
    tags=["Services"]
)

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

class ServiceCreateDto(ServiceBase):
    pass

class ServiceUpdateDto(ServiceBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class ServiceDto(ServiceBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/services", response_model=List[ServiceDto])
def get_all_services(db: Session = Depends(data_access.get_db),
                       current_user: dict = Depends(auth.get_current_user), # Keep for authentication check
                       query: Optional[str] = None,
                       sort_by: Optional[str] = None,
                       sort_direction: Optional[str] = None):
    # Allow all authenticated users (doctors and patients) to view services
    # Admins can also view, as they are authenticated.
    if not current_user: # Ensure user is authenticated
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    services = business_logic.get_all_services_logic(db, query, sort_by, sort_direction)
    return services

@router.get("/services/{service_id}", response_model=ServiceDto)
def get_service_by_id(service_id: int, db: Session = Depends(data_access.get_db),
                        current_user: dict = Depends(auth.get_current_user)):
    # Only admins can view service details for management purposes
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view service details")
    
    service = business_logic.get_service_by_id_logic(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service

@router.post("/services", response_model=ServiceDto, status_code=status.HTTP_201_CREATED)
def create_service(service_data: ServiceCreateDto, db: Session = Depends(data_access.get_db),
                   current_user: dict = Depends(auth.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create services")
    
    new_service = business_logic.create_service_logic(db, service_data.dict())
    return new_service

@router.put("/services/{service_id}", response_model=ServiceDto)
def update_service(service_id: int, service_data: ServiceUpdateDto, db: Session = Depends(data_access.get_db),
                   current_user: dict = Depends(auth.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update services")
    
    updated_service = business_logic.update_service_logic(db, service_id, service_data.dict(exclude_unset=True))
    if not updated_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return updated_service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: Session = Depends(data_access.get_db),
                   current_user: dict = Depends(auth.get_current_user)):
    if current_user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete services")
    
    result = business_logic.delete_service_logic(db, service_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found or could not be deleted")
    return