-- =================================================================
--      DATABASE SCRIPT FOR ONLINE BOOKING SYSTEM
--      Đã sửa đổi để khớp với yêu cầu của Báo cáo Project 1
--      Dựa trên Sơ đồ ERD và các bảng mô tả (Bảng 14-19)
--      Dành cho Microsoft SQL Server (T-SQL)
-- =================================================================

-- Tạo và sử dụng cơ sở dữ liệu
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'QuanLyKhamBenhDB')
BEGIN
    CREATE DATABASE QuanLyKhamBenhDB;
END
GO

USE QuanLyKhamBenhDB;
GO

-- =================================================================
--  Step 1: Tạo các bảng cơ sở (Không có khóa ngoại)
-- =================================================================

-- Bảng Bệnh nhân (PATIENTS) [cite: 250, 251]
CREATE TABLE PATIENTS (
    patient_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    phone NVARCHAR(15) NOT NULL UNIQUE,
    -- SỬA LỖI: Chuyển từ NVARCHAR sang DATE để có thể tính toán
    birth_date DATE NOT NULL,
    address NVARCHAR(MAX) NULL,
    -- SỬA LỖI BẢO MẬT: Không bao giờ lưu mật khẩu, chỉ lưu chuỗi đã băm
    password_hash NVARCHAR(255) NOT NULL
);
GO

-- Bảng Chuyên khoa (SPECIALTIES) [cite: 253, 254]
CREATE TABLE SPECIALTIES (
    specialty_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX) NULL
);
GO

-- Bảng Thuốc (MEDICINES) [cite: 262, 263]
-- SỬA LỖI: Sửa lại bảng thuốc để khớp với yêu cầu báo cáo (FR6) [cite: 136]
CREATE TABLE MEDICINES (
    medicine_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0
);
GO

-- Bảng Quản trị viên (ADMINS) - Dựa trên vai trò Admin trong Use Case 
CREATE TABLE ADMINS (
    admin_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(100) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL
);
GO

-- =================================================================
--  Step 2: Tạo các bảng phụ thuộc (Phụ thuộc Step 1)
-- =================================================================

-- Bảng Bác sĩ (DOCTORS) [cite: 256, 257]
CREATE TABLE DOCTORS (
    doctor_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    phone NVARCHAR(15) NOT NULL UNIQUE,
    specialty_id INT NULL,
    qualifications NVARCHAR(MAX) NULL,
    -- SỬA LỖI BẢO MẬT: Dùng password_hash
    password_hash NVARCHAR(255) NOT NULL,
    
    CONSTRAINT FK_Doctors_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id)
);
GO

-- Bảng Thông báo (NOTIFICATIONS) [cite: 271, 272]
CREATE TABLE NOTIFICATIONS (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_id INT NOT NULL,
    title NVARCHAR(200) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    -- SỬA LỖI: Dùng kiểu BIT (true/false) cho T-SQL
    is_read BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_Notifications_Patients FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id)
);
GO

-- Bảng Gợi ý AI (AI_RECOMMENDATIONS) 
-- THÊM MỚI: Bảng này có trong báo cáo nhưng thiếu trong file .sql
CREATE TABLE AI_RECOMMENDATIONS (
    recommendation_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_id INT NULL,
    symptoms_input NVARCHAR(MAX) NOT NULL,
    doctor_id INT NULL,
    specialty_id INT NULL,
    recommendation_date DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_AI_Patients FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id),
    CONSTRAINT FK_AI_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id),
    CONSTRAINT FK_AI_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id)
);
GO

-- =================================================================
--  Step 3: Tạo các bảng nghiệp vụ chính
-- =================================================================

-- Bảng Lịch hẹn (APPOINTMENTS) [cite: 259, 260]
CREATE TABLE APPOINTMENTS (
    appointment_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NULL, -- Có thể NULL nếu bệnh nhân chỉ chọn chuyên khoa
    specialty_id INT NOT NULL,
    -- SỬA LỖI: Gộp ngày và giờ vào một cột DATETIME2
    appointment_datetime DATETIME2 NOT NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',
    notes NVARCHAR(MAX) NULL,
    booking_code NVARCHAR(20) NULL UNIQUE,
    symptoms NVARCHAR(MAX) NULL,

    CONSTRAINT FK_Appointments_Patients FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id),
    CONSTRAINT FK_Appointments_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id),
    CONSTRAINT FK_Appointments_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id),
    CONSTRAINT CHK_Appointment_Status CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed'))
);
GO

-- Bảng Thanh toán (PAYMENTS) 
-- THÊM MỚI: Bảng này có trong báo cáo nhưng thiếu trong file .sql
CREATE TABLE PAYMENTS (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method NVARCHAR(50) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_date DATETIME2 DEFAULT GETDATE(),

    CONSTRAINT FK_Payments_Appointments FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id),
    CONSTRAINT CHK_Payment_Status CHECK (status IN ('pending', 'completed', 'failed'))
);
GO

-- Bảng Đơn thuốc (PRESCRIPTIONS) [cite: 265, 266]
CREATE TABLE PRESCRIPTIONS (
    prescription_id INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id INT NOT NULL,
    -- SỬA LỖI: Dùng khóa ngoại medicine_id thay vì cột `name`
    medicine_id INT NOT NULL,
    quantity INT NOT NULL,
    instructions NVARCHAR(MAX) NULL,

    CONSTRAINT FK_Prescriptions_Appointments FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id),
    CONSTRAINT FK_Prescriptions_Medicines FOREIGN KEY (medicine_id) REFERENCES MEDICINES(medicine_id)
);
GO
-- Bảng Dịch vụ Khám (SERVICES)
CREATE TABLE SERVICES (
    service_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1
);
GO
-- Bảng Dịch vụ đi kèm Lịch hẹn (APPOINTMENT_SERVICES)
CREATE TABLE APPOINTMENT_SERVICES (
    appointment_service_id INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,       -- số lần / số lượt
    notes NVARCHAR(MAX) NULL,

    CONSTRAINT FK_AppSvc_Appointments FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id),
    CONSTRAINT FK_AppSvc_Services FOREIGN KEY (service_id) REFERENCES SERVICES(service_id)
);
GO
CREATE TABLE MEDICAL_RECORDS (
    medical_record_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Liên kết với cuộc hẹn (Quan trọng nhất)
    appointment_id INT NOT NULL UNIQUE, -- Mỗi lịch hẹn chỉ có một hồ sơ bệnh án
    doctor_id INT NOT NULL,             -- Bác sĩ lập hồ sơ
    
    -- THÔNG TIN CHẨN ĐOÁN
    diagnosis_in NVARCHAR(500) NULL,      -- Chẩn đoán vào viện (ban đầu)
    diagnosis_out NVARCHAR(500) NOT NULL, -- Chẩn đoán ra viện (cuối cùng)

    
    -- TÓM TẮT QUÁ TRÌNH ĐIỀU TRỊ
    treatment_summary NVARCHAR(MAX) NOT NULL, -- Tóm tắt Quá trình điều trị (thay thế cột 'conclusion' và 'diagnosis' cũ)
    
    -- THÔNG TIN KHÁC
    examination_date DATETIME2 DEFAULT GETDATE(), -- Ngày hồ sơ được tạo/hoàn thành

    -- Ràng buộc Khóa ngoại
    CONSTRAINT FK_MR_Appointments FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id),
    CONSTRAINT FK_MR_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id) 
);
GO


-- Bảng Lịch làm việc,nghỉ linh hoạt/bổ sung của từng Bác sĩ
CREATE TABLE DOCTOR_WORKING_HOURS (
    working_hour_id INT IDENTITY(1,1) PRIMARY KEY,
    doctor_id INT NOT NULL,
    -- Luu tru cac ngay lam viec khong co dinh (VD: 'SATURDAY', 'SUNDAY', 'MONDAY' neu co lam them)
    day_of_week NVARCHAR(10) NOT NULL, 
    start_time TIME NOT NULL, 
    end_time TIME NOT NULL,   
    
    CONSTRAINT FK_WH_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id),
    -- Ràng buộc: Đảm bảo không trùng lặp đăng ký
    CONSTRAINT UQ_WH_DoctorDayTime UNIQUE (doctor_id, day_of_week, start_time, end_time) 
);
GO
CREATE TABLE DOCTOR_LEAVES (
    leave_id INT IDENTITY(1,1) PRIMARY KEY,
    doctor_id INT NOT NULL,
    start_datetime DATETIME2 NOT NULL, 
    end_datetime DATETIME2 NOT NULL, 
    reason NVARCHAR(MAX) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    CONSTRAINT FK_Leaves_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id)
);
GO
-- Bảng lưu trữ Ngày lễ (nghỉ chung cho cả bệnh viện)
CREATE TABLE HOLIDAYS (
    holiday_id INT IDENTITY(1,1) PRIMARY KEY,
    holiday_date DATE NOT NULL UNIQUE, 
    name NVARCHAR(100) NOT NULL
);
GO
-- Thêm cột leave_type nếu chưa tồn tại
ALTER TABLE DOCTOR_LEAVES
ADD leave_type NVARCHAR(50) NOT NULL DEFAULT 'Other';
GO
ALTER TABLE DOCTOR_LEAVES
ADD CONSTRAINT CHK_Leave_Type 
CHECK (leave_type IN (
    'annual ', -- Nghỉ phép thường niên (Cần phê duyệt trước)
    'sick ',  -- Nghỉ ốm (Đăng ký gấp, cần chứng từ sau)
    'urgent ', -- Nghỉ đột xuất (Áp dụng quy tắc riêng, ví dụ: tang gia, việc gia đình)
    'other' -- Các loại khác
));
GO

ALTER TABLE MEDICAL_RECORDS
ADD 
    -- 1. DỮ LIỆU SINH TỒN (Theo yêu cầu: Chỉ điền 1 lần)
    -- Đây là cách tối ưu nhất thay vì tạo bảng VITAL_SIGNS riêng
    pulse_rate INT NULL,                        -- Mạch (Lần/phút)
    temperature DECIMAL(4, 2) NULL,             -- Nhiệt độ (°C)
    blood_pressure_mmhg NVARCHAR(10) NULL,      -- Huyết áp (VD: 120/80)
    spo2_percent DECIMAL(4, 1) NULL,            -- SpO2 (%)
    
    -- 2. GHI NHẬN BỔ SUNG CỦA BÁC SĨ (HPI - History of Present Illness)
    -- Thùng chứa các ghi chú lâm sàng của bác sĩ dựa trên Triệu chứng BN
    doctor_hpi_notes NVARCHAR(MAX) NULL,
    -- 3. KẾT QUẢ KHÁM THỰC THỂ (Objective Findings)
    -- Lưu trữ mô tả của bác sĩ về tình trạng bệnh nhân (Nghe tim, phổi, sờ bụng...)
    physical_examination_notes NVARCHAR(MAX) NULL; 
    
GO

PRINT N'✅ Đã thêm các trường Dấu hiệu Sinh tồn và Ghi nhận bổ sung vào bảng MEDICAL_RECORDS.';





























-- Xóa bản ghi nghỉ phép của Bác sĩ D nếu có
DELETE FROM DOCTOR_LEAVES
WHERE doctor_id IN (
    SELECT doctor_id FROM DOCTORS WHERE full_name IN (N'Bác sĩ Lê Thị D')
);

-- Xóa bản ghi Bác sĩ C và D (nếu chúng đã tồn tại)
DELETE FROM DOCTORS
WHERE full_name IN (N'Bác sĩ Lê Thị D');
GO

-- =================================================================
-- 2. TẠO BÁC SĨ E VÀ BÁC SĨ D VÀ CHÈN ĐƠN NGHỈ PHÉP
-- =================================================================

-- Khai báo các hằng số cần dùng
-- Giả định specialty_id=1 là Khoa Nội tổng hợp (của Bác sĩ B)
DECLARE @KhoaNoiTongHopID INT = 1; 
DECLARE @HashedPassword NVARCHAR(255) = 'CHUOI_HASH_CUA_123'; 
DECLARE @LeaveType NVARCHAR(50) = 'annual'; 

-- -----------------------------------------------------------------
-- 2.1. TẠO BÁC SĨ E và D
-- -----------------------------------------------------------------

-- Tạo Bác sĩ E (thay thế cho Bác sĩ C)
INSERT INTO DOCTORS (full_name, email, phone, specialty_id, qualifications, password_hash)
VALUES (N'Bác sĩ Phan Văn E', 'bs.pvanE@example.com', '0901112224', @KhoaNoiTongHopID, N'Thạc sĩ Nội khoa', @HashedPassword);

-- Tạo Bác sĩ D
INSERT INTO DOCTORS (full_name, email, phone, specialty_id, qualifications, password_hash)
VALUES (N'Bác sĩ Lê Thị D', 'bs.lthid@example.com', '0903334440', @KhoaNoiTongHopID, N'Bác sĩ chuyên khoa I', @HashedPassword);
GO

-- -----------------------------------------------------------------
-- 2.2. CHÈN BẢN GHI NGHỈ PHÉP
-- -----------------------------------------------------------------

-- Lấy ID của Bác sĩ E và D vừa tạo (Đây là cách an toàn nhất)
DECLARE @DoctorEID INT = (SELECT doctor_id FROM DOCTORS WHERE full_name = N'Bác sĩ Phan Văn E');
DECLARE @DoctorDID INT = (SELECT doctor_id FROM DOCTORS WHERE full_name = N'Bác sĩ Lê Thị D');
DECLARE @LeaveType NVARCHAR(50) = 'annual'; 
-- Đơn nghỉ của Bác sĩ E: 12/12/2025, 07:00 – 15:00
INSERT INTO DOCTOR_LEAVES (doctor_id, start_datetime, end_datetime, reason, status, leave_type)
VALUES (
    @DoctorEID, 
    '2025-12-12 07:00:00', 
    '2025-12-12 15:00:00', 
    N'Nghỉ phép thường niên theo giờ (8 tiếng)', 
    'pending', 
    @LeaveType
);

-- Đơn nghỉ của Bác sĩ D: 13/12/2025, 09:00 – 17:00
INSERT INTO DOCTOR_LEAVES (doctor_id, start_datetime, end_datetime, reason, status, leave_type)
VALUES (
    @DoctorDID, 
    '2025-12-13 09:00:00', 
    '2025-12-13 17:00:00', 
    N'Nghỉ phép thường niên theo giờ (8 tiếng)', 
    'pending', 
    @LeaveType
);
GO

-- =================================================================
-- 3. TRUY VẤN XÁC NHẬN DỮ LIỆU
-- =================================================================

PRINT N'✅ Đã chèn thành công Bác sĩ E, D và đơn nghỉ phép.';