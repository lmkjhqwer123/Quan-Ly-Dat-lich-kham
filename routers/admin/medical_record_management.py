
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from DataAccessLayer.data_access import get_raw_db_connection
import pyodbc
from auth import get_current_user # Import the dependency

# This is a comment to force recompilation
router = APIRouter()

# Định nghĩa một model Pydantic để trả về dữ liệu
from pydantic import BaseModel
from datetime import datetime

class MedicalRecordOut(BaseModel):
    MedicalRecordId: int
    AppointmentId: int
    BookingCode: Optional[str]
    PatientName: str
    DoctorName: str
    SpecialtyName: str
    ExaminationDate: datetime
    DiagnosisOut: str

@router.get("/api/admin/medical-records", response_model=List[MedicalRecordOut])
async def get_all_medical_records(
    search: Optional[str] = Query(None, description="Search by patient name, doctor name, or booking code"),
    sort_by: Optional[str] = Query(None, description="Sort by 'patient_name', 'doctor_name', 'examination_date'"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction: 'asc' or 'desc'"),
    specialty_name: Optional[str] = Query(None, description="Filter by specialty name"),
    limit: Optional[int] = Query(None, description="Limit the number of results"),
    db: pyodbc.Connection = Depends(get_raw_db_connection),
    current_user = Depends(get_current_user) # Add dependency
):
    try:
        cursor = db.cursor()
        
        query = """
            SELECT 
                mr.medical_record_id,
                mr.appointment_id,
                a.booking_code,
                p.full_name AS patient_name,
                d.full_name AS doctor_name,
                s.name AS specialty_name,
                mr.examination_date,
                mr.diagnosis_out
            FROM 
                MEDICAL_RECORDS mr
            JOIN 
                APPOINTMENTS a ON mr.appointment_id = a.appointment_id
            JOIN 
                PATIENTS p ON a.patient_id = p.patient_id
            JOIN 
                DOCTORS d ON mr.doctor_id = d.doctor_id
            JOIN 
                SPECIALTIES s ON a.specialty_id = s.specialty_id
        """

        params = []
        where_clauses = []

        # Filter by doctor if the user is a doctor
        if current_user.role == "Doctor":
            where_clauses.append("mr.doctor_id = ?")
            params.append(current_user.id)

        if search:
            where_clauses.append("(p.full_name LIKE ? OR d.full_name LIKE ? OR a.booking_code LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if specialty_name:
            where_clauses.append("s.name = ?")
            params.append(specialty_name)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Sorting logic
        if sort_by and sort_by in ['patient_name', 'doctor_name', 'examination_date']:
            order_by_clause = f" ORDER BY {sort_by}"
            if sort_direction and sort_direction.lower() in ['asc', 'desc']:
                order_by_clause += f" {sort_direction.upper()}"
            else:
                order_by_clause += " DESC" # Default direction
            query += order_by_clause
        else:
            query += " ORDER BY mr.examination_date DESC"

        # Pagination logic
        if limit:
            # This syntax is for SQL Server. Adjust if using a different DB.
            query = query.replace("SELECT", f"SELECT TOP {limit}")

        cursor.execute(query, *params)
        
        records = []
        for row in cursor.fetchall():
            records.append(MedicalRecordOut(
                MedicalRecordId=row.medical_record_id,
                AppointmentId=row.appointment_id,
                BookingCode=row.booking_code,
                PatientName=row.patient_name,
                DoctorName=row.doctor_name,
                SpecialtyName=row.specialty_name,
                ExaminationDate=row.examination_date,
                DiagnosisOut=row.diagnosis_out
            ))
            
        return records

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi truy vấn cơ sở dữ liệu")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")
    finally:
        if 'cursor' in locals():
            cursor.close()

@router.get("/api/admin/medical-records/{record_id}", response_model=MedicalRecordOut)
async def get_medical_record_by_id(
    record_id: int,
    db: pyodbc.Connection = Depends(get_raw_db_connection)
):
    try:
        cursor = db.cursor()
        
        query = """
            SELECT 
                mr.medical_record_id,
                mr.appointment_id,
                a.booking_code,
                p.full_name AS patient_name,
                d.full_name AS doctor_name,
                s.name AS specialty_name,
                mr.examination_date,
                mr.diagnosis_out
            FROM 
                MEDICAL_RECORDS mr
            JOIN 
                APPOINTMENTS a ON mr.appointment_id = a.appointment_id
            JOIN 
                PATIENTS p ON a.patient_id = p.patient_id
            JOIN 
                DOCTORS d ON mr.doctor_id = d.doctor_id
            JOIN 
                SPECIALTIES s ON a.specialty_id = s.specialty_id
            WHERE mr.medical_record_id = ?
        """

        cursor.execute(query, record_id)
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy bệnh án")
            
        record = MedicalRecordOut(
            MedicalRecordId=row.medical_record_id,
            AppointmentId=row.appointment_id,
            BookingCode=row.booking_code,
            PatientName=row.patient_name,
            DoctorName=row.doctor_name,
            SpecialtyName=row.specialty_name,
            ExaminationDate=row.examination_date,
            DiagnosisOut=row.diagnosis_out
        )
            
        return record

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi truy vấn cơ sở dữ liệu")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")
    finally:
        if 'cursor' in locals():
            cursor.close()

