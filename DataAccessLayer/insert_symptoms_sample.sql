-- =================================================================
-- INSERT SAMPLE DATA INTO SYMPTOMS TABLE
-- Dữ liệu mẫu cho bảng SYMPTOMS
-- =================================================================

USE QuanLyKhamBenhDB;
GO

-- Xóa dữ liệu cũ (nếu có)
DELETE FROM SYMPTOMS;
GO

-- INSERT dữ liệu mẫu
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active, created_at)
VALUES
    -- Khoa Nội tổng hợp (Specialty ID = 1)
    (N'Sốt', N'sốt, sốt cao, sốt kéo dài, fever, cảm cúm', 1, 1, GETDATE()),
    (N'Ho', N'ho, cough, ho có đờm, ho khan, ho lâu ngày', 1, 1, GETDATE()),
    (N'Đau đầu', N'đau đầu, migraine, đau nửa đầu, nhức đầu', 1, 1, GETDATE()),
    (N'Huyết áp cao', N'huyết áp cao, cao máu, blood pressure, huyết áp', 1, 1, GETDATE()),
    (N'Khó thở', N'khó thở, dyspnea, hụt hơi, đoạn hơi', 1, 1, GETDATE()),
    (N'Chóng mặt', N'chóng mặt, buồn nôn, mất thăng bằng, vertigo', 1, 1, GETDATE()),
    
    -- Khoa Ngoại tổng quát (Specialty ID = 2)
    (N'Chấn thương', N'chấn thương, injury, va chạm, bị thương', 2, 1, GETDATE()),
    (N'Gãy xương', N'gãy xương, fracture, xương gãy, vỡ xương', 2, 1, GETDATE()),
    (N'Chảy máu', N'chảy máu, bleeding, máu chảy, hemorrhage', 2, 1, GETDATE()),
    (N'Viêm vết mổ', N'viêm vết mổ, infection, vết mổ bị nhiễm', 2, 1, GETDATE()),
    (N'Phù nề', N'phù nề, swelling, sưng phù, tích nước', 2, 1, GETDATE()),
    
    -- Khoa Sản (Specialty ID = 3)
    (N'Đau bụng kỳ kinh', N'đau bụng kỳ kinh, dysmenorrhea, đau kinh nguyệt', 3, 1, GETDATE()),
    (N'Rong kinh', N'rong kinh, menorrhagia, chảy máu bất thường', 3, 1, GETDATE()),
    (N'Vô sinh', N'vô sinh, infertility, không có con', 3, 1, GETDATE()),
    (N'Khí hư bất thường', N'khí hư bất thường, abnormal discharge, viêm phụ khoa', 3, 1, GETDATE()),
    
    -- Khoa Nhi (Specialty ID = 4)
    (N'Sốt cao ở trẻ', N'sốt cao ở trẻ, fever in children, cháy sốt', 4, 1, GETDATE()),
    (N'Tiêu chảy', N'tiêu chảy, diarrhea, phân lỏng, rối loạn tiêu hóa', 4, 1, GETDATE()),
    (N'Nôn', N'nôn, vomiting, buồn nôn, trớ sữa', 4, 1, GETDATE()),
    (N'Viêm đường hô hấp', N'viêm đường hô hấp, respiratory infection, cảm lạnh', 4, 1, GETDATE()),
    
    -- Khoa Da liễu (Specialty ID = 5)
    (N'Mụn', N'mụn, acne, mụn trứng cá, mụn viêm', 5, 1, GETDATE()),
    (N'Viêm da', N'viêm da, dermatitis, viêm da dị ứng, eczema', 5, 1, GETDATE()),
    (N'Khô da', N'khô da, dry skin, da khô, chứng khô', 5, 1, GETDATE()),
    (N'Nám da', N'nám da, melasma, tàn nhang, lão hóa da', 5, 1, GETDATE()),
    (N'Lang ben', N'lang ben, tinea versicolor, bệnh nấm', 5, 1, GETDATE()),
    
    -- Răng-Hàm-Mặt (Specialty ID = 6)
    (N'Đau răng', N'đau răng, toothache, sâu răng, viêm nướu', 6, 1, GETDATE()),
    (N'Viêm nướu', N'viêm nướu, gingivitis, chảy máu chân răng', 6, 1, GETDATE()),
    (N'Cao răng', N'cao răng, tartar, mảng bám, vôi răng', 6, 1, GETDATE()),
    (N'Hôi miệng', N'hôi miệng, bad breath, mùi từ miệng', 6, 1, GETDATE()),
    
    -- Tai-Mũi-Họng (Specialty ID = 7)
    (N'Viêm họng', N'viêm họng, đau họng, throat pain, sore throat', 7, 1, GETDATE()),
    (N'Viêm amidan', N'viêm amidan, tonsillitis, amidan sưng to', 7, 1, GETDATE()),
    (N'Viêm xoang', N'viêm xoang, sinusitis, xoang sưng, chứng xoang', 7, 1, GETDATE()),
    (N'Ù tai', N'ù tai, hearing loss, nặng tai, điếc một tai', 7, 1, GETDATE()),
    (N'Sổi mũi', N'sổi mũi, rhinitis, cảm lạnh, chảy nước mũi', 7, 1, GETDATE());

GO

PRINT N'✅ Đã thêm 28 triệu chứng mẫu vào bảng SYMPTOMS';

-- Verify
SELECT COUNT(*) as TotalSymptoms FROM SYMPTOMS;
