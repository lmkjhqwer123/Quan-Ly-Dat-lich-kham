-- =================================================================
--      ADDITIONAL TABLES FOR INTELLIGENT MEDICAL CHATBOT
--      Sử dụng cho Chatbot Y tế thông minh (Gemini + Function Calling)
-- =================================================================

USE QuanLyKhamBenhDB;
GO

-- =================================================================
-- 1. BẢNG TRIỆU CHỨNG (SYMPTOMS)
-- Dùng để sàng lọc triệu chứng bệnh nhân
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SYMPTOMS')
BEGIN
    CREATE TABLE SYMPTOMS (
        symptom_id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(200) NOT NULL,
        description NVARCHAR(MAX) NULL,
        -- Keyword search (VD: "đau đầu", "đau_đầu", "headache")
        keywords NVARCHAR(MAX) NULL,
        -- Liên kết đến chuyên khoa phù hợp
        specialty_id INT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 DEFAULT GETDATE(),

        CONSTRAINT FK_Symptoms_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id)
    );
    PRINT N'✅ Bảng SYMPTOMS đã được tạo.';
END
GO

-- =================================================================
-- 2. BẢNG SLOT KHÁM (APPOINTMENT_SLOTS)
-- Các khe thời gian khám trống của bác sĩ
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'APPOINTMENT_SLOTS')
BEGIN
    CREATE TABLE APPOINTMENT_SLOTS (
        slot_id INT IDENTITY(1,1) PRIMARY KEY,
        doctor_id INT NOT NULL,
        specialty_id INT NOT NULL,
        -- Ngày giờ bắt đầu của slot
        slot_datetime DATETIME2 NOT NULL,
        -- Thời lượng khám (phút) - thường là 30 hoặc 60 phút
        duration_minutes INT NOT NULL DEFAULT 30,
        -- Trạng thái: 'available' = trống, 'booked' = đã đặt, 'closed' = khóa
        status NVARCHAR(20) NOT NULL DEFAULT 'available',
        -- Giá dịch vụ
        price DECIMAL(10, 2) NULL,
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),

        CONSTRAINT FK_Slots_Doctors FOREIGN KEY (doctor_id) REFERENCES DOCTORS(doctor_id),
        CONSTRAINT FK_Slots_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id),
        CONSTRAINT CHK_Slot_Status CHECK (status IN ('available', 'booked', 'closed')),
        -- Đảm bảo không có 2 slot giống nhau cho một bác sĩ
        CONSTRAINT UQ_Slot_DateTime UNIQUE (doctor_id, slot_datetime)
    );
    PRINT N'✅ Bảng APPOINTMENT_SLOTS đã được tạo.';
END
GO

-- =================================================================
-- 3. BẢNG HƯỚNG DẪN CHUẨN BỊ KHÁM (CONSULTATION_GUIDES)
-- Hướng dẫn chuẩn bị trước khi khám cho từng chuyên khoa
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CONSULTATION_GUIDES')
BEGIN
    CREATE TABLE CONSULTATION_GUIDES (
        guide_id INT IDENTITY(1,1) PRIMARY KEY,
        specialty_id INT NOT NULL,
        service_id INT NULL,
        -- Tiêu đề hướng dẫn (VD: "Hướng dẫn chuẩn bị khám Tim mạch")
        title NVARCHAR(300) NOT NULL,
        -- Nội dung chi tiết (VD: "Mang theo: ..., Chuẩn bị: ...")
        content NVARCHAR(MAX) NOT NULL,
        -- Danh sách những gì cần mang (dạng JSON hoặc text)
        items_to_bring NVARCHAR(MAX) NULL,
        -- Những chuẩn bị khác
        preparation_notes NVARCHAR(MAX) NULL,
        -- Thời gian ước tính cho khám (phút)
        estimated_duration_minutes INT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 DEFAULT GETDATE(),
        updated_at DATETIME2 DEFAULT GETDATE(),

        CONSTRAINT FK_Guides_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id),
        CONSTRAINT FK_Guides_Services FOREIGN KEY (service_id) REFERENCES SERVICES(service_id)
    );
    PRINT N'✅ Bảng CONSULTATION_GUIDES đã được tạo.';
END
GO

-- =================================================================
-- 4. BẢNG LỊCH SỬ HỘI THOẠI CHATBOT (CHAT_CONVERSATIONS)
-- Lưu trữ cuộc hội thoại giữa người dùng và chatbot
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CHAT_CONVERSATIONS')
BEGIN
    CREATE TABLE CHAT_CONVERSATIONS (
        conversation_id INT IDENTITY(1,1) PRIMARY KEY,
        patient_id INT NULL, -- Nullable nếu user chưa đăng nhập
        session_id NVARCHAR(100) NULL, -- Session ID cho user ẩn danh
        -- Trạng thái cuộc chat: 'active', 'closed', 'archived'
        status NVARCHAR(20) NOT NULL DEFAULT 'active',
        -- Chuyên khoa được gợi ý (từ chatbot)
        recommended_specialty_id INT NULL,
        -- Bác sĩ được gợi ý
        recommended_doctor_id INT NULL,
        -- Có tạo lịch hẹn không
        appointment_created BIT NOT NULL DEFAULT 0,
        created_at DATETIME2 DEFAULT GETDATE(),
        ended_at DATETIME2 NULL,

        CONSTRAINT FK_ChatConv_Patients FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id),
        CONSTRAINT FK_ChatConv_Specialties FOREIGN KEY (recommended_specialty_id) REFERENCES SPECIALTIES(specialty_id),
        CONSTRAINT FK_ChatConv_Doctors FOREIGN KEY (recommended_doctor_id) REFERENCES DOCTORS(doctor_id)
    );
    PRINT N'✅ Bảng CHAT_CONVERSATIONS đã được tạo.';
END
GO

-- =================================================================
-- 5. BẢNG CHI TIẾT TIN NHẮN HỘI THOẠI (CHAT_MESSAGES)
-- Mỗi dòng thoại một message
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CHAT_MESSAGES')
BEGIN
    CREATE TABLE CHAT_MESSAGES (
        message_id INT IDENTITY(1,1) PRIMARY KEY,
        conversation_id INT NOT NULL,
        -- 'user' hoặc 'bot'
        sender_type NVARCHAR(10) NOT NULL,
        -- Nội dung tin nhắn
        message_text NVARCHAR(MAX) NOT NULL,
        -- Tool được gọi (nếu là bot response): VD 'get_specialty_for_symptoms'
        tool_used NVARCHAR(100) NULL,
        -- JSON data trả về từ tool (nếu có)
        tool_response NVARCHAR(MAX) NULL,
        created_at DATETIME2 DEFAULT GETDATE(),

        CONSTRAINT FK_ChatMsg_Conversations FOREIGN KEY (conversation_id) REFERENCES CHAT_CONVERSATIONS(conversation_id),
        CONSTRAINT CHK_Sender_Type CHECK (sender_type IN ('user', 'bot'))
    );
    PRINT N'✅ Bảng CHAT_MESSAGES đã được tạo.';
END
GO

-- =================================================================
-- 6. BẢNG SYMPTOM_SPECIALTY MAPPING (Triệu chứng - Chuyên khoa)
-- Liên kết N:N giữa triệu chứng và chuyên khoa
-- =================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SYMPTOM_SPECIALTY_MAPPING')
BEGIN
    CREATE TABLE SYMPTOM_SPECIALTY_MAPPING (
        mapping_id INT IDENTITY(1,1) PRIMARY KEY,
        symptom_id INT NOT NULL,
        specialty_id INT NOT NULL,
        -- Độ liên quan (1-10): 10 là liên quan nhất
        relevance_score INT NULL DEFAULT 5,
        created_at DATETIME2 DEFAULT GETDATE(),

        CONSTRAINT FK_Mapping_Symptoms FOREIGN KEY (symptom_id) REFERENCES SYMPTOMS(symptom_id),
        CONSTRAINT FK_Mapping_Specialties FOREIGN KEY (specialty_id) REFERENCES SPECIALTIES(specialty_id),
        CONSTRAINT UQ_Symptom_Specialty UNIQUE (symptom_id, specialty_id),
        CONSTRAINT CHK_Relevance CHECK (relevance_score >= 1 AND relevance_score <= 10)
    );
    PRINT N'✅ Bảng SYMPTOM_SPECIALTY_MAPPING đã được tạo.';
END
GO

-- =================================================================
-- 7. INSERT DỮ LIỆU MẪU CHO SYMPTOMS
-- =================================================================

-- Kiểm tra nếu chưa có dữ liệu trong SYMPTOMS
IF (SELECT COUNT(*) FROM SYMPTOMS) = 0
BEGIN
    INSERT INTO SYMPTOMS (name, description, keywords, specialty_id, is_active)
    VALUES
        (N'Đau đầu', N'Cảm thấy đau, nặng nề ở vùng đầu', N'đau đầu,đau_đầu,headache,migraine', 1, 1),
        (N'Đau ngực', N'Cảm thấy đau ở vùng ngực', N'đau ngực,đau_ngực,chest pain,angina', 1, 1),
        (N'Đau cơ', N'Cơ thể bị đau nhức', N'đau cơ,đau_cơ,muscle pain,myalgia', 2, 1),
        (N'Huyết áp cao', N'Chỉ số huyết áp cao hơn bình thường', N'huyết áp cao,cao_huyết_áp,hypertension,high blood pressure', 1, 1),
        (N'Mệt mỏi', N'Cảm thấy mệt, thiếu năng lượng', N'mệt mỏi,mệt,fatigue,tired', 3, 1),
        (N'Buồn nôn', N'Cảm thấy muốn nôn', N'buồn nôn,nôn,nausea,vomiting', 3, 1),
        (N'Ho', N'Tình trạng ho dai dẳng', N'ho,cough,flu', 4, 1),
        (N'Sốt', N'Nhiệt độ cơ thể cao', N'sốt,sốt cao,fever,temperature', 4, 1);
    PRINT N'✅ Đã chèn dữ liệu mẫu cho SYMPTOMS.';
END
GO

-- =================================================================
-- 8. INSERT DỮ LIỆU MẪU CHO CONSULTATION_GUIDES
-- =================================================================

IF (SELECT COUNT(*) FROM CONSULTATION_GUIDES) = 0
BEGIN
    INSERT INTO CONSULTATION_GUIDES (specialty_id, title, content, items_to_bring, preparation_notes, estimated_duration_minutes, is_active)
    VALUES
        (1, N'Hướng dẫn chuẩn bị khám Tim mạch', 
         N'Khám Tim mạch đòi hỏi bệnh nhân chuẩn bị kỹ lưỡng để có kết quả chính xác nhất.',
         N'- Thẻ BHYT hoặc CMND
- Hóa đơn bệnh viện cũ (nếu có)
- Danh sách đơn thuốc hiện tại',
         N'- Tránh uống cà phê, trà trong 1 ngày trước khám
- Mặc trang phục rộng rãi
- Không tập thể dục nặng trước khám
- Đo huyết áp trước khám nếu có máy',
         45, 1),
        (2, N'Hướng dẫn chuẩn bị khám Thần kinh',
         N'Khám Thần kinh cần các bài test đơn giản để đánh giá tình trạng thần kinh.',
         N'- Thẻ BHYT
- Hình ảnh chụp CT/MRI (nếu có)',
         N'- Ngủ đủ giấc trước khám
- Tránh căng thẳng
- Mang theo ghi chép về triệu chứng',
         50, 1),
        (3, N'Hướng dẫn chuẩn bị khám Tiêu hóa',
         N'Cần chuẩn bị đặc biệt để kiểm tra dạ dày, ruột.',
         N'- CMND
- Kết quả xét nghiệm gần nhất',
         N'- Ăn nhẹ trong 1-2 ngày trước khám
- Không uống rượu bia
- Uống 1-2 lít nước trước khám
- Đến khám sáng sớm (6-8h sáng tốt nhất)',
         60, 1);
    PRINT N'✅ Đã chèn dữ liệu mẫu cho CONSULTATION_GUIDES.';
END
GO

-- =================================================================
-- 9. INSERT DỮ LIỆU MẪU CHO APPOINTMENT_SLOTS
-- (Tạo một số slot khám cho các bác sĩ)
-- =================================================================

-- Lấy ID của bác sĩ đầu tiên
DECLARE @DoctorID INT = (SELECT TOP 1 doctor_id FROM DOCTORS);
DECLARE @SpecialtyID INT = (SELECT TOP 1 specialty_id FROM DOCTORS WHERE doctor_id = @DoctorID);

IF @DoctorID IS NOT NULL
BEGIN
    -- Tạo slots cho 14 ngày tới
    DECLARE @Counter INT = 0;
    DECLARE @BaseDateTime DATETIME2 = CAST(GETDATE() AS DATETIME2);
    
    WHILE @Counter < 14
    BEGIN
        INSERT INTO APPOINTMENT_SLOTS (doctor_id, specialty_id, slot_datetime, duration_minutes, status, price)
        VALUES 
            (@DoctorID, @SpecialtyID, DATEADD(HOUR, 8 + (@Counter * 24), @BaseDateTime), 30, 'available', 150000),
            (@DoctorID, @SpecialtyID, DATEADD(HOUR, 9 + (@Counter * 24), @BaseDateTime), 30, 'available', 150000),
            (@DoctorID, @SpecialtyID, DATEADD(HOUR, 13 + (@Counter * 24), @BaseDateTime), 30, 'available', 150000),
            (@DoctorID, @SpecialtyID, DATEADD(HOUR, 14 + (@Counter * 24), @BaseDateTime), 30, 'available', 150000);
        SET @Counter = @Counter + 1;
    END;
    PRINT N'✅ Đã tạo dữ liệu mẫu cho APPOINTMENT_SLOTS.';
END
GO

-- =================================================================
-- 10. KIỂM TRA TỔNG QUAN
-- =================================================================

PRINT N'';
PRINT N'===== KẾT QUẢ TẠO BẢNG =====';
SELECT 
    'SYMPTOMS' AS [Table Name], COUNT(*) AS [Records]
FROM SYMPTOMS
UNION ALL
SELECT 'APPOINTMENT_SLOTS', COUNT(*) FROM APPOINTMENT_SLOTS
UNION ALL
SELECT 'CONSULTATION_GUIDES', COUNT(*) FROM CONSULTATION_GUIDES
UNION ALL
SELECT 'CHAT_CONVERSATIONS', COUNT(*) FROM CHAT_CONVERSATIONS
UNION ALL
SELECT 'CHAT_MESSAGES', COUNT(*) FROM CHAT_MESSAGES
UNION ALL
SELECT 'SYMPTOM_SPECIALTY_MAPPING', COUNT(*) FROM SYMPTOM_SPECIALTY_MAPPING;

PRINT N'';
PRINT N'✅ ===== HOÀN TẤT TẠO CÁC BẢNG CHO CHATBOT =====';


