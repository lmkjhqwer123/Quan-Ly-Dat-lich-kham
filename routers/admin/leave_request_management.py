from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from DataAccessLayer.data_access import dax
from BusinessLogicLayer.business_logic import business_logic
from auth import get_current_user

router = APIRouter()

@router.get("/admin/leave-requests", response_model=List[Dict[str, Any]])
async def get_leave_requests(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    try:
        leave_requests = dax.get_all_leave_requests()
        return business_logic.format_leave_requests(leave_requests)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/admin/leave-requests/{leave_id}/approve")
async def approve_leave_request(leave_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    try:
        dax.update_leave_request_status(leave_id, "approved")
        return {"message": "Leave request approved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/admin/leave-requests/{leave_id}/reject")
async def reject_leave_request(leave_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    try:
        dax.update_leave_request_status(leave_id, "rejected")
        return {"message": "Leave request rejected successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
