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

-- =================================================================
--  Step 4: Chèn dữ liệu mẫu (đã cập nhật)
-- =================================================================

-- Chèn Chuyên khoa [cite: 253]
INSERT INTO SPECIALTIES (name, description) VALUES
(N'Khoa Nội tổng hợp', N'Chẩn đoán và điều trị các bệnh nội khoa.'),
(N'Khoa Ngoại tổng quát', N'Thực hiện các ca phẫu thuật tổng quát.'),
(N'Khoa Sản', N'Chăm sóc sức khỏe sinh sản cho phụ nữ.'),
(N'Khoa Nhi', N'Khám và điều trị cho trẻ em.'),
(N'Khoa Da liễu', N'Điều trị các bệnh về da.'),
(N'Răng-Hàm-Mặt', N'Chăm sóc sức khỏe răng miệng.'),
(N'Tai-Mũi-Họng', N'Điều trị các bệnh liên quan đến tai, mũi, họng.');
GO

-- Chèn Thuốc (đã có tồn kho và giá) [cite: 263]
INSERT INTO MEDICINES (name, description, price, stock_quantity) VALUES
(N'Paracetamol 500mg', N'Hạ sốt, giảm đau', 1500, 1000),
(N'Amoxicillin 250mg', N'Kháng sinh', 3000, 500),
(N'Berberin', N'Trị tiêu chảy', 2000, 800);
GO

-- Chèn 1 Admin (mật khẩu mẫu là "admin123" - đây là 1 chuỗi hash giả)
INSERT INTO ADMINS (username, email, password_hash) VALUES
(N'admin', N'admin@benhvien.com', N'CHUOI_HASH_CUA_ADMIN123');
GO

-- Chèn 1 Bệnh nhân (mật khẩu mẫu là "benhnhanA")
INSERT INTO PATIENTS (full_name, email, phone, birth_date, address, password_hash) VALUES
(N'Nguyễn Văn An', 'an.nguyen@example.com', '0912345678', '1990-01-15', N'123 Đường Láng, Hà Nội', N'CHUOI_HASH_CUA_BENHNHANA');
GO

-- Chèn 1 Bác sĩ (mật khẩu mẫu là "bacsiB")
INSERT INTO DOCTORS (full_name, email, phone, specialty_id, qualifications, password_hash) VALUES
(N'Bác sĩ Trần Thị B', 'bs.b@example.com', '0987654321', 1, N'Tiến sĩ, Bác sĩ Nội trú', N'CHUOI_HASH_CUA_BACSIB');
GO


-- Chèn 1 Lịch hẹn mẫu
INSERT INTO APPOINTMENTS (patient_id, doctor_id, specialty_id, appointment_datetime, status, symptoms)
VALUES
(1, 1, 1, '2025-10-30T09:30:00', 'confirmed', N'Ho, sốt, đau họng');
GO

-- Chèn 1 Đơn thuốc cho lịch hẹn trên [cite: 265]
INSERT INTO PRESCRIPTIONS (appointment_id, medicine_id, quantity, instructions)
VALUES
(1, 1, 20, N'Uống 2 viên/lần khi sốt trên 38.5 độ'),
(1, 2, 14, N'Uống 1 viên/lần, 2 lần/ngày sau ăn');
GO

-- Chèn 1 Thanh toán cho lịch hẹn trên [cite: 268]
INSERT INTO PAYMENTS (appointment_id, amount, payment_method, status)
VALUES
(1, 150000, N'Chuyển khoản', 'completed');
GO

-- Chèn 1 Gợi ý AI mẫu [cite: 274]
INSERT INTO AI_RECOMMENDATIONS (patient_id, symptoms_input, specialty_id, recommendation_date)
VALUES
(1, N'Đau bụng âm ỉ, ợ chua', 1, GETDATE());
GO

INSERT INTO SERVICES (name, description, price) VALUES
(N'Xét nghiệm máu', N'Kiểm tra tổng phân tích máu', 120000),
(N'Chụp X-Quang', N'Chụp X-Quang chuẩn đoán', 250000),
(N'Siêu âm bụng tổng quát', N'Kiểm tra ổ bụng bằng siêu âm', 300000);
GO

-- Gán dịch vụ cho lịch hẹn mẫu (appointment_id = 1)
INSERT INTO APPOINTMENT_SERVICES (appointment_id, service_id, quantity) VALUES
(1, 1, 1),   -- Xét nghiệm máu
(1, 3, 1);   -- Siêu âm bụng
GO
-- Thêm Bệnh nhân mới (patient_id = 2) mật khẩu (123)
INSERT INTO PATIENTS (full_name, email, phone, birth_date, address, password_hash) VALUES
(N'Lê Thị Mai', 'mai.le@example.com', '0901112223', '1995-05-20', N'456 Đường Giải Phóng, Hà Nội', N'CHUOI_HASH_CUA_BENHNHANB');
GO

-- Thêm Bác sĩ mới (doctor_id = 2) vào Khoa Da liễu (specialty_id = 5) mật khẩu (newpass123)
INSERT INTO DOCTORS (full_name, email, phone, specialty_id, qualifications, password_hash) VALUES
(N'Bác sĩ Nguyễn Văn C', 'bs.c@example.com', '0905556667', 5, N'Thạc sĩ Da liễu', N'$2a$10$HASH_CUA_NEWPASS123');
GO
-- Chèn 1 Lịch hẹn mẫu đã hoàn thành (appointment_id = 1)
INSERT INTO APPOINTMENTS (patient_id, doctor_id, specialty_id, appointment_datetime, status, symptoms, booking_code)
VALUES
(9, 3, 5, '2025-11-10T14:00:00', 'completed', N'Nổi mẩn đỏ, ngứa da toàn thân',N'1');
GO
-- Gán dịch vụ cho lịch hẹn (appointment_id = 1): Bác sĩ chỉ định Xét nghiệm máu
INSERT INTO APPOINTMENT_SERVICES (appointment_id, service_id, quantity) VALUES
(9, 1, 1); -- service_id = 1 là 'Xét nghiệm máu'
GO

-- Kê Đơn thuốc (appointment_id = 1): Kê thuốc Amoxicillin
INSERT INTO PRESCRIPTIONS (appointment_id, medicine_id, quantity, instructions)
VALUES
(9, 2, 21, N'Uống 1 viên, 3 lần/ngày trong 7 ngày'); -- medicine_id = 2 là 'Amoxicillin 250mg'
GO
-- Chèn Hồ sơ Bệnh án (cho appointment_id = 1)
INSERT INTO MEDICAL_RECORDS (
    appointment_id, 
    doctor_id, 
    diagnosis_in, 
    diagnosis_out, 
    treatment_summary,
    examination_date -- Tự động lấy GETDATE() nếu không chỉ định, nhưng có thể chỉ định rõ
)
VALUES
(
    9, -- Lịch hẹn số 9
    3, -- Bác sĩ Nguyễn Văn C
    N'Viêm da dị ứng cấp tính', 
    N'Viêm da tiếp xúc dị ứng', 
    N'Bệnh nhân được chỉ định xét nghiệm máu để loại trừ các nguyên nhân toàn thân. Điều trị bằng kháng histamine (Loratadin 10mg) và kem bôi corticoid tại chỗ. Hướng dẫn tránh tiếp xúc với chất gây dị ứng tiềm tàng.',
    '2025-11-10T15:00:00' -- Giả định hồ sơ được hoàn thành lúc 15:00
);
GO


-- Lấy ID lịch hẹn tự tăng tiếp theo
DECLARE @NewBookingCode NVARCHAR(20) = 'APPT003';
-- Bạn nên điều chỉnh mã này để chắc chắn nó là duy nhất nếu APPT003 đã được sử dụng.

INSERT INTO APPOINTMENTS (patient_id, doctor_id, specialty_id, appointment_datetime, status, symptoms, booking_code)
VALUES
(
    1, -- patient_id: Nguyễn Văn An
    1, -- doctor_id: Bác sĩ Trần Thị B
    1, -- specialty_id: Khoa Nội tổng hợp
    '2025-11-10T16:00:00', -- Thời gian: 4:00 PM ngày 10/11/2025
    'pending', -- Trạng thái ban đầu là đang chờ duyệt
    N'Khó thở, tức ngực nhẹ',
    @NewBookingCode
);
GO

PRINT 'Đã chèn thành công lịch hẹn mới lúc 16:00 hôm nay (10/11/2025) với trạng thái PENDING.';


PRINT 'Database QuanLyKhamBenhDB created and seeded successfully.';