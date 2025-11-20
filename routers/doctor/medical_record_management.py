from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from BusinessLogicLayer.business_logic import create_medical_record_bl
from DataAccessLayer import data_access
from auth import get_current_user

router = APIRouter()

class Vitals(BaseModel):
    pulse: Optional[int] = Field(None, description="Mạch (lần/phút)")
    temperature: Optional[float] = Field(None, description="Nhiệt độ (°C)")
    blood_pressure: Optional[str] = Field(None, description="Huyết áp (VD: 120/80)")
    spo2: Optional[float] = Field(None, description="SpO2 (%)")

class MedicalRecordCreate(BaseModel):
    appointment_id: int
    patient_symptoms: Optional[str] = Field(None, description="Triệu chứng bệnh nhân khai báo (diagnosis_in)")
    doctor_notes: Optional[str] = Field(None, description="Ghi nhận bổ sung của Bác sĩ (doctor_hpi_notes)")
    clinical_summary: Optional[str] = Field(None, description="Tóm tắt kết quả khám lâm sàng (physical_examination_notes)")
    preliminary_diagnosis: str = Field(..., description="Chẩn đoán sơ bộ (diagnosis_out)")
    doctor_advice: Optional[str] = Field(None, description="Lời dặn của bác sĩ & Lịch tái khám (treatment_summary)")
    vitals: Optional[Vitals] = None

class MedicalRecordResponse(BaseModel):
    MedicalRecordId: int
    BookingCode: Optional[str] = None
    PatientName: str
    DoctorName: str
    SpecialtyName: str
    ExaminationDate: datetime
    DiagnosisOut: str
    DiagnosisIn: Optional[str] = None
    DoctorHPINotes: Optional[str] = None
    PhysicalExaminationNotes: Optional[str] = None
    TreatmentSummary: Optional[str] = None
    PulseRate: Optional[int] = None
    Temperature: Optional[float] = None
    BloodPressureMMHG: Optional[str] = None
    SPO2Percent: Optional[float] = None

@router.post("/medical-records", status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    medical_record_data: MedicalRecordCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(data_access.get_db)
):
    """
    Tạo một bệnh án mới cho một lịch hẹn đã hoàn thành.
    """
    if current_user.role != "Doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ bác sĩ mới có quyền tạo bệnh án."
        )
    try:
        doctor_id = current_user.id
        if not doctor_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không tìm thấy ID bác sĩ trong token."
            )
        
        # Prepare data for business logic layer
        mr_data = {
            "appointment_id": medical_record_data.appointment_id,
            "doctor_id": doctor_id,
            "diagnosis_in": medical_record_data.patient_symptoms,
            "doctor_hpi_notes": medical_record_data.doctor_notes,
            "physical_examination_notes": medical_record_data.clinical_summary,
            "diagnosis_out": medical_record_data.preliminary_diagnosis,
            "treatment_summary": medical_record_data.doctor_advice,
            "pulse_rate": medical_record_data.vitals.pulse if medical_record_data.vitals else None,
            "temperature": medical_record_data.vitals.temperature if medical_record_data.vitals else None,
            "blood_pressure_mmhg": medical_record_data.vitals.blood_pressure if medical_record_data.vitals else None,
            "spo2_percent": medical_record_data.vitals.spo2 if medical_record_data.vitals else None,
        }

        medical_record_id = await create_medical_record_bl(db=db, medical_record_data=mr_data)
        return {"message": "Bệnh án đã được tạo thành công", "medical_record_id": medical_record_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/medical-records", response_model=List[MedicalRecordResponse])
async def get_medical_records_for_doctor(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(data_access.get_db),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên bệnh nhân hoặc chẩn đoán"),
    sort_by: Optional[str] = Query(None, description="Sắp xếp theo trường (e.g., ExaminationDate, PatientName)"),
    sort_direction: Optional[str] = Query(None, description="Hướng sắp xếp (asc hoặc desc)"),
    limit: int = Query(10, ge=1, description="Số lượng bệnh án mỗi trang")
):
    """
    Lấy danh sách bệnh án cho bác sĩ đã đăng nhập, có hỗ trợ tìm kiếm, sắp xếp và phân trang.
    """
    if current_user.role != "Doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ bác sĩ mới có quyền xem bệnh án."
        )
    
    doctor_id = current_user.id
    if not doctor_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy ID bác sĩ trong token."
        )

    medical_records = data_access.get_medical_records_by_doctor_id(
        db,
        doctor_id=doctor_id,
        search_query=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit
    )
    return medical_records

@router.get("/medical-records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record_detail_for_doctor(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(data_access.get_db)
):
    """
    Lấy chi tiết một bệnh án cụ thể cho bác sĩ đã đăng nhập.
    """
    if current_user.role != "Doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ bác sĩ mới có quyền xem chi tiết bệnh án."
        )
    
    doctor_id = current_user.id
    if not doctor_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không tìm thấy ID bác sĩ trong token."
        )

    medical_record = data_access.get_medical_record_by_id_and_doctor_id(db, record_id, doctor_id)
    if not medical_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy bệnh án hoặc bạn không có quyền truy cập.")
    
    return medical_record
