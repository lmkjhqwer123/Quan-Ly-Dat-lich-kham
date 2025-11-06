from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from BusinessLogicLayer import business_logic
from DataAccessLayer import data_access
from routers.specialty.models import SpecialtyCreateRequest, SpecialtyUpdateRequest, SpecialtyDto

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Specialty Management"]
)

@router.post("/specialties/", response_model=SpecialtyDto, status_code=status.HTTP_201_CREATED)
def create_specialty(specialty_request: SpecialtyCreateRequest, db: Session = Depends(data_access.get_db)):
    """
    Create a new specialty.
    """
    result = business_logic.create_new_specialty_logic(db, specialty_request.model_dump())
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result

@router.get("/specialties/", response_model=List[SpecialtyDto])
def get_all_specialties(db: Session = Depends(data_access.get_db), query: Optional[str] = None, sort_by: Optional[str] = None, sort_direction: Optional[str] = None):
    """
    Get all specialties, with optional search and sorting.
    """
    if query:
        return business_logic.search_specialties_logic(db, query, sort_by, sort_direction)
    else:
        return business_logic.get_all_specialties_logic(db, sort_by, sort_direction)

@router.get("/specialties/{specialty_id}", response_model=SpecialtyDto)
def get_specialty(specialty_id: int, db: Session = Depends(data_access.get_db)):
    """
    Get a specialty by ID.
    """
    db_specialty = business_logic.get_specialty_by_id_logic(db, specialty_id)
    if db_specialty is None:
        raise HTTPException(status_code=404, detail="Specialty not found")
    return db_specialty

@router.put("/specialties/{specialty_id}", response_model=SpecialtyDto)
def update_specialty(specialty_id: int, specialty_request: SpecialtyUpdateRequest, db: Session = Depends(data_access.get_db)):
    """
    Update a specialty.
    """
    result = business_logic.update_specialty_info_logic(db, specialty_id, specialty_request.model_dump())
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return result

@router.delete("/specialties/{specialty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_specialty(specialty_id: int, db: Session = Depends(data_access.get_db)):
    """
    Delete a specialty.
    """
    result = business_logic.delete_specialty_by_id_logic(db, specialty_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
    return {"ok": True}
