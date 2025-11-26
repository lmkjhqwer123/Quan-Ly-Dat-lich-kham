-- Kiểm tra appointment_id 25
SELECT 
    a.appointment_id,
    a.patient_id,
    a.doctor_id,
    a.status,
    a.appointment_datetime,
    p.full_name AS PatientName,
    d.full_name AS DoctorName,
    CASE WHEN mr.medical_record_id IS NOT NULL THEN 'Có' ELSE 'Không' END AS CoBehnAn
FROM APPOINTMENTS a
LEFT JOIN PATIENTS p ON a.patient_id = p.patient_id
LEFT JOIN DOCTORS d ON a.doctor_id = d.doctor_id
LEFT JOIN MEDICAL_RECORDS mr ON a.appointment_id = mr.appointment_id
WHERE a.appointment_id = 25;

-- Nếu status khác 'completed', sửa nó
IF (SELECT status FROM APPOINTMENTS WHERE appointment_id = 25) != 'completed'
BEGIN
    UPDATE APPOINTMENTS
    SET status = 'completed'
    WHERE appointment_id = 25;
    PRINT N'✅ Đã update appointment_id 25 status thành "completed"';
END
ELSE
BEGIN
    PRINT N'✅ Appointment_id 25 đã có status = "completed"';
END
