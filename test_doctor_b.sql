-- Test kiểm tra dữ liệu ngày 30/11 cho bác sĩ B
-- doctor_id = 2

USE QuanLyKhamBenhDB;
GO

PRINT '=== DOCTOR B APPOINTMENTS ngay 30/11/2025 ===';
SELECT appointment_id, patient_id, doctor_id, appointment_datetime, status
FROM APPOINTMENTS
WHERE doctor_id = 2
  AND CAST(appointment_datetime AS DATE) = '2025-11-30';

PRINT '';
PRINT '=== DOCTOR B DOCTOR_LEAVES ngay 30/11/2025 ===';
SELECT leave_id, doctor_id, start_datetime, end_datetime, status
FROM DOCTOR_LEAVES
WHERE doctor_id = 2
  AND (CAST(start_datetime AS DATE) = '2025-11-30' 
       OR CAST(end_datetime AS DATE) = '2025-11-30'
       OR (start_datetime < '2025-11-30 23:59:59' AND end_datetime > '2025-11-30 00:00:00'));

PRINT '';
PRINT '=== TEST slot 07:00-09:00 ngay 30/11 ===';
DECLARE @slot_start DATETIME2 = '2025-11-30 07:00:00';
DECLARE @slot_end DATETIME2 = '2025-11-30 09:00:00';

SELECT 'Appointments matching' as check_type, COUNT(*) as count
FROM APPOINTMENTS
WHERE doctor_id = 2
  AND status IN ('pending', 'confirmed')
  AND (appointment_datetime >= @slot_start AND appointment_datetime < @slot_end)

UNION ALL

SELECT 'Leaves matching', COUNT(*)
FROM DOCTOR_LEAVES
WHERE doctor_id = 2
  AND status IN ('pending', 'approved')
  AND (
    (start_datetime <= @slot_end AND end_datetime > @slot_start)
    OR (start_datetime < @slot_end AND end_datetime >= @slot_start)
    OR (start_datetime >= @slot_start AND end_datetime <= @slot_end)
  );
