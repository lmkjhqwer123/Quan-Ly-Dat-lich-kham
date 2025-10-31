-- =================================================================
--      DATABASE SCRIPT FOR ONLINE BOOKING SYSTEM
--      Re-ordered for logical dependency.
--      Converted for Microsoft SQL Server (T-SQL).
-- =================================================================

-- Create and use the database first
CREATE DATABASE QuanLyDatLichDB;
GO

USE QuanLyDatLichDB;
GO

-- =================================================================
--  Step 1: Create tables with no external dependencies
-- =================================================================

CREATE TABLE tn_specialities (
  id INT IDENTITY(1,1) PRIMARY KEY,
  name NVARCHAR(30) NULL,
  description NVARCHAR(255) NULL,
  image NVARCHAR(255) NULL
);
GO

CREATE TABLE tn_rooms (
  id INT IDENTITY(1,1) PRIMARY KEY,
  name NVARCHAR(15) NULL,
  location NVARCHAR(255) NULL
);
GO

CREATE TABLE tn_services (
  id INT IDENTITY(1,1) PRIMARY KEY,
  name NVARCHAR(255) NULL,
  image NVARCHAR(255) NULL,
  description NVARCHAR(MAX) NULL
);
GO

CREATE TABLE tn_drugs (
  id INT IDENTITY(1,1) PRIMARY KEY,
  name NVARCHAR(255) NULL
);
GO

CREATE TABLE tn_patients (
  id INT IDENTITY(1,1) PRIMARY KEY,
  email NVARCHAR(255) NULL,
  phone NVARCHAR(15) NULL,
  password NVARCHAR(255) NULL,
  name NVARCHAR(50) NULL,
  gender INT NULL,
  birthday NVARCHAR(10) NULL,
  address NVARCHAR(255) NULL,
  avatar NVARCHAR(255) NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL
);
GO

-- =================================================================
--  Step 2: Create tables with dependencies on Step 1 tables
-- =================================================================

CREATE TABLE tn_doctors (
  id INT IDENTITY(1,1) PRIMARY KEY,
  email NVARCHAR(255) NULL,
  phone NVARCHAR(15) NULL,
  password NVARCHAR(255) NULL,
  name NVARCHAR(50) NULL,
  description NVARCHAR(255) NULL,
  price INT NULL,
  role NVARCHAR(10) NULL,
  active INT NULL,
  avatar NVARCHAR(255) NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL,
  speciality_id INT NULL,
  room_id INT NULL,
  recovery_token NVARCHAR(255) NULL
);
GO

CREATE TABLE tn_booking (
  id INT IDENTITY(1,1) PRIMARY KEY,
  service_id INT NULL,
  patient_id INT NULL,
  appointment_date NVARCHAR(10) NULL,
  appointment_hour NVARCHAR(5) NULL,
  status NVARCHAR(15) NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL
);
GO

CREATE TABLE tn_notifications (
  id INT IDENTITY(1,1) PRIMARY KEY,
  message NVARCHAR(MAX) NULL,
  record_id INT NULL,
  record_type NVARCHAR(20) NULL,
  patient_id INT NULL,
  is_read INT NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL
);
GO

-- =================================================================
--  Step 3: Create tables with dependencies on Step 2 tables
-- =================================================================

CREATE TABLE tn_doctor_and_service (
  id INT IDENTITY(1,1) PRIMARY KEY,
  service_id INT NULL,
  doctor_id INT NULL
);
GO

CREATE TABLE tn_booking_photo (
  id INT IDENTITY(1,1) PRIMARY KEY,
  url NVARCHAR(255) NULL,
  booking_id INT NULL
);
GO

CREATE TABLE tn_appointments (
  id INT IDENTITY(1,1) PRIMARY KEY,
  booking_id INT NULL,
  doctor_id INT NULL,
  patient_id INT NULL,
  numerical_order INT NULL,
  position INT NULL,
  appointment_time NVARCHAR(20) NULL,
  date NVARCHAR(10) NULL,
  status NVARCHAR(15) NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL
);
GO

-- =================================================================
--  Step 4: Create tables with dependencies on Step 3 tables
-- =================================================================

CREATE TABLE tn_treatments (
  id INT IDENTITY(1,1) PRIMARY KEY,
  appointment_id INT NULL,
  name NVARCHAR(50) NULL,
  type NVARCHAR(20) NULL,
  times INT NULL,
  purpose NVARCHAR(50) NULL,
  instruction NVARCHAR(255) NULL,
  repeat_days NVARCHAR(255) NULL,
  repeat_time NVARCHAR(5) NULL
);
GO

CREATE TABLE tn_appointment_records (
  id INT IDENTITY(1,1) PRIMARY KEY,
  appointment_id INT NULL,
  reason NVARCHAR(100) NULL,
  description NVARCHAR(MAX) NULL,
  status_before NVARCHAR(255) NULL,
  status_after NVARCHAR(255) NULL,
  create_at DATETIME NULL,
  update_at DATETIME NULL
);
GO

-- =================================================================
--  Step 5: ADD ALL FOREIGN KEY CONSTRAINTS
-- =================================================================

ALTER TABLE tn_doctors
  ADD CONSTRAINT fk_doctors_specialities FOREIGN KEY (speciality_id) REFERENCES tn_specialities (id);
GO
ALTER TABLE tn_doctors
  ADD CONSTRAINT fk_doctors_rooms FOREIGN KEY (room_id) REFERENCES tn_rooms (id);
GO
  
ALTER TABLE tn_booking
  ADD CONSTRAINT fk_booking_patients FOREIGN KEY (patient_id) REFERENCES tn_patients (id);
GO
ALTER TABLE tn_booking
  ADD CONSTRAINT fk_booking_services FOREIGN KEY (service_id) REFERENCES tn_services (id);
GO
  
ALTER TABLE tn_notifications
  ADD CONSTRAINT fk_notifications_patients FOREIGN KEY (patient_id) REFERENCES tn_patients (id);
GO

ALTER TABLE tn_doctor_and_service
  ADD CONSTRAINT fk_doctor_service_services FOREIGN KEY (service_id) REFERENCES tn_services (id);
GO
ALTER TABLE tn_doctor_and_service
  ADD CONSTRAINT fk_doctor_service_doctors FOREIGN KEY (doctor_id) REFERENCES tn_doctors (id);
GO
  
ALTER TABLE tn_booking_photo
  ADD CONSTRAINT fk_booking_photo_booking FOREIGN KEY (booking_id) REFERENCES tn_booking (id);
GO
  
ALTER TABLE tn_appointments
  ADD CONSTRAINT fk_appointments_doctors FOREIGN KEY (doctor_id) REFERENCES tn_doctors (id);
GO
ALTER TABLE tn_appointments
  ADD CONSTRAINT fk_appointments_patients FOREIGN KEY (patient_id) REFERENCES tn_patients (id);
GO
  
ALTER TABLE tn_treatments
  ADD CONSTRAINT fk_treatments_appointments FOREIGN KEY (appointment_id) REFERENCES tn_appointments (id);
GO

ALTER TABLE tn_appointment_records
  ADD CONSTRAINT fk_appointment_records_appointments FOREIGN KEY (appointment_id) REFERENCES tn_appointments (id);
GO

GO

-- Insert 7 Specialities
INSERT INTO tn_specialities (name, description) VALUES
(N'Khoa Nội tổng hợp', N'Chẩn đoán và điều trị các bệnh nội khoa.'),
(N'Khoa Ngoại tổng quát', N'Thực hiện các ca phẫu thuật tổng quát.'),
(N'Khoa Sản', N'Chăm sóc sức khỏe sinh sản cho phụ nữ.'),
(N'Khoa Nhi', N'Khám và điều trị cho trẻ em.'),
(N'Khoa Da liễu', N'Điều trị các bệnh về da.'),
(N'Răng-Hàm-Mặt', N'Chăm sóc sức khỏe răng miệng.'),
(N'Tai-Mũi-Họng', N'Điều trị các bệnh liên quan đến tai, mũi, họng.');
GO

-- Insert 10 Rooms
INSERT INTO tn_rooms (name, location) VALUES
(N'Phòng 101', N'Tầng 1, Khu A'),
(N'Phòng 102', N'Tầng 1, Khu A'),
(N'Phòng 201', N'Tầng 2, Khu A'),
(N'Phòng 202', N'Tầng 2, Khu A'),
(N'Phòng 301', N'Tầng 3, Khu B'),
(N'Phòng 302', N'Tầng 3, Khu B'),
(N'Phòng 401', N'Tầng 4, Khu C'),
(N'Phòng 402', N'Tầng 4, Khu C'),
(N'Phòng 501', N'Tầng 5, Khu D'),
(N'Phòng 502', N'Tầng 5, Khu D');
GO

-- Insert 3 Services
INSERT INTO tn_services (name, description) VALUES
(N'Khám sức khỏe tổng quát', N'Kiểm tra toàn diện các chỉ số sức khỏe.'),
(N'Xét nghiệm máu', N'Phân tích các thành phần trong máu để chẩn đoán bệnh.'),
(N'Chụp X-quang', N'Sử dụng tia X để xem hình ảnh bên trong cơ thể.');
GO

-- Insert 20 Patients
INSERT INTO tn_patients (name, email, phone, password, gender, birthday, address, create_at, update_at) VALUES
(N'Nguyễn Văn An', 'an.nguyen@example.com', '0912345678', 'pass123', 1, '1990-01-15', N'123 Đường Láng, Hà Nội', GETDATE(), GETDATE()),
(N'Trần Thị Bình', 'binh.tran@example.com', '0987654321', 'pass123', 0, '1992-05-20', N'456 Đường Nguyễn Trãi, Hà Nội', GETDATE(), GETDATE()),
(N'Lê Văn Cường', 'cuong.le@example.com', '0905123456', 'pass123', 1, '1985-11-30', N'789 Đường Cầu Giấy, Hà Nội', GETDATE(), GETDATE()),
(N'Phạm Thị Dung', 'dung.pham@example.com', '0934567890', 'pass123', 0, '1998-07-22', N'101 Đường Kim Mã, Hà Nội', GETDATE(), GETDATE()),
(N'Hoàng Văn Em', 'em.hoang@example.com', '0945678901', 'pass123', 1, '2000-03-10', N'202 Đường Lê Văn Lương, Hà Nội', GETDATE(), GETDATE()),
(N'Vũ Thị Giang', 'giang.vu@example.com', '0967890123', 'pass123', 0, '1995-09-05', N'303 Đường Tây Sơn, Hà Nội', GETDATE(), GETDATE()),
(N'Đỗ Văn Hùng', 'hung.do@example.com', '0978901234', 'pass123', 1, '1988-12-12', N'404 Đường Giải Phóng, Hà Nội', GETDATE(), GETDATE()),
(N'Bùi Thị Ian', 'ian.bui@example.com', '0989012345', 'pass123', 0, '1993-02-28', N'505 Đường Trường Chinh, Hà Nội', GETDATE(), GETDATE()),
(N'Ngô Văn Kiên', 'kien.ngo@example.com', '0911223344', 'pass123', 1, '1991-08-18', N'606 Đường Minh Khai, Hà Nội', GETDATE(), GETDATE()),
(N'Đặng Thị Lan', 'lan.dang@example.com', '0922334455', 'pass123', 0, '1996-04-25', N'707 Đường Đại Cồ Việt, Hà Nội', GETDATE(), GETDATE()),
(N'Trịnh Văn Mạnh', 'manh.trinh@example.com', '0933445566', 'pass123', 1, '1987-06-14', N'808 Đường Bạch Mai, Hà Nội', GETDATE(), GETDATE()),
(N'Mai Thị Nga', 'nga.mai@example.com', '0944556677', 'pass123', 0, '1999-10-01', N'909 Đường Phố Huế, Hà Nội', GETDATE(), GETDATE()),
(N'Lý Văn Oai', 'oai.ly@example.com', '0955667788', 'pass123', 1, '1986-07-07', N'111 Đường Bà Triệu, Hà Nội', GETDATE(), GETDATE()),
(N'Chu Thị Phương', 'phuong.chu@example.com', '0966778899', 'pass123', 0, '1994-01-19', N'222 Đường Hai Bà Trưng, Hà Nội', GETDATE(), GETDATE()),
(N'Tô Văn Quân', 'quan.to@example.com', '0977889900', 'pass123', 1, '1989-03-03', N'333 Đường Trần Hưng Đạo, Hà Nội', GETDATE(), GETDATE()),
(N'Nguyễn Thị Rung', 'rung.nguyen@example.com', '0988990011', 'pass123', 0, '1997-11-11', N'444 Đường Quang Trung, Hà Đông', GETDATE(), GETDATE()),
(N'Dương Văn Sáng', 'sang.duong@example.com', '0912345000', 'pass123', 1, '1984-05-05', N'555 Đường Nguyễn Văn Cừ, Long Biên', GETDATE(), GETDATE()),
(N'Lưu Thị Tâm', 'tam.luu@example.com', '0987654111', 'pass123', 0, '2001-02-14', N'666 Đường Ngọc Lâm, Long Biên', GETDATE(), GETDATE()),
(N'Hồ Văn Toàn', 'toan.ho@example.com', '0905123222', 'pass123', 1, '1983-10-20', N'777 Đường Ngô Gia Tự, Long Biên', GETDATE(), GETDATE()),
(N'Vương Thị Uyên', 'uyen.vuong@example.com', '0934567333', 'pass123', 0, '2002-08-08', N'888 Đường Nguyễn Sơn, Long Biên', GETDATE(), GETDATE());
GO

-- Insert 20 Doctors
-- We will assign a random speciality (1-7) and room (1-10) to each doctor
INSERT INTO tn_doctors (name, email, phone, password, price, active, speciality_id, room_id, create_at, update_at) VALUES
(N'Bác sĩ Nguyễn Thị A', 'bs.a@example.com', '0911111111', 'bs_pass', 300000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Trần Văn B', 'bs.b@example.com', '0922222222', 'bs_pass', 400000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Lê Thị C', 'bs.c@example.com', '0933333333', 'bs_pass', 350000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Phạm Văn D', 'bs.d@example.com', '0944444444', 'bs_pass', 500000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Hoàng Thị E', 'bs.e@example.com', '0955555555', 'bs_pass', 450000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Vũ Văn F', 'bs.f@example.com', '0966666666', 'bs_pass', 300000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Đỗ Thị G', 'bs.g@example.com', '0977777777', 'bs_pass', 400000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Bùi Văn H', 'bs.h@example.com', '0988888888', 'bs_pass', 550000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Ngô Thị I', 'bs.i@example.com', '0912223334', 'bs_pass', 320000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Đặng Văn K', 'bs.k@example.com', '0923334445', 'bs_pass', 420000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Trịnh Thị L', 'bs.l@example.com', '0934445556', 'bs_pass', 380000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Mai Văn M', 'bs.m@example.com', '0945556667', 'bs_pass', 520000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Lý Thị N', 'bs.n@example.com', '0956667778', 'bs_pass', 480000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Chu Văn P', 'bs.p@example.com', '0967778889', 'bs_pass', 330000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Tô Thị Q', 'bs.q@example.com', '0978889990', 'bs_pass', 430000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Nguyễn Văn R', 'bs.r@example.com', '0989990001', 'bs_pass', 600000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Dương Thị S', 'bs.s@example.com', '0911234567', 'bs_pass', 370000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Lưu Văn T', 'bs.t@example.com', '0987654321', 'bs_pass', 470000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Hồ Thị U', 'bs.u@example.com', '0905654321', 'bs_pass', 570000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE()),
(N'Bác sĩ Vương Văn V', 'bs.v@example.com', '0934123456', 'bs_pass', 310000, 1, ABS(CHECKSUM(NEWID())) % 7 + 1, ABS(CHECKSUM(NEWID())) % 10 + 1, GETDATE(), GETDATE());
GO