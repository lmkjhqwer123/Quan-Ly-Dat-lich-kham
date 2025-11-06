from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access

router = APIRouter()

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class Service(ServiceBase):
    id: int

    class Config:
        orm_mode = True

@router.post("/services/", response_model=Service, status_code=status.HTTP_201_CREATED, tags=["Services"])
def create_service(service: ServiceCreate, db: Session = Depends(data_access.get_db)):
    try:
        new_service = business_logic.create_service_logic(db, service.dict())
        return new_service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/", response_model=List[Service], tags=["Services"])
def get_all_services(
    name: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: Optional[str] = None,
    db: Session = Depends(data_access.get_db)
):
    try:
        services = business_logic.get_all_services_logic(db, query=name, sort_by=sort_by, sort_direction=sort_direction)
        if not services:
            raise HTTPException(status_code=404, detail="No services found")
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/{service_id}", response_model=Service, tags=["Services"])
def get_service_by_id(service_id: int, db: Session = Depends(data_access.get_db)):
    try:
        service = business_logic.get_service_by_id_logic(db, service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/services/{service_id}", response_model=Service, tags=["Services"])
def update_service(service_id: int, service: ServiceUpdate, db: Session = Depends(data_access.get_db)):
    try:
        updated_service = business_logic.update_service_logic(db, service_id, service.dict(exclude_unset=True))
        if not updated_service:
            raise HTTPException(status_code=404, detail="Service not found")
        return updated_service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Services"])
def delete_service(service_id: int, db: Session = Depends(data_access.get_db)):
    try:
        success = business_logic.delete_service_logic(db, service_id)
        if not success:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
