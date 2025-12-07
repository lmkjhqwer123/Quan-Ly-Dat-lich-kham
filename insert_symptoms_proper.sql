-- Insert sample symptoms data with proper Unicode handling
-- Dữ liệu mẫu cho bảng SYMPTOMS

SET DATEFORMAT mdy;

-- Khoa Nội tổng hợp (Specialty ID = 1)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Sốt', N'sốt, sốt cao, sốt kéo dài, fever, cảm cúm', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Ho', N'ho, cough, ho có đờm, ho khan, ho lâu ngày', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Đau đầu', N'đau đầu, migraine, đau nửa đầu, nhức đầu', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Huyết áp cao', N'huyết áp cao, cao máu, blood pressure, huyết áp', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Khó thở', N'khó thở, dyspnea, hụt hơi, đoạn hơi', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Chóng mặt', N'chóng mặt, buồn nôn, mất thăng bằng, vertigo', 1, 1);

-- Khoa Ngoại tổng quát (Specialty ID = 2)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Chấn thương', N'chấn thương, injury, va chạm, bị thương', 2, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Gãy xương', N'gãy xương, fracture, xương gãy, vỡ xương', 2, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Chảy máu', N'chảy máu, bleeding, máu chảy, hemorrhage', 2, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm vết mổ', N'viêm vết mổ, infection, vết mổ bị nhiễm', 2, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Phù nề', N'phù nề, swelling, sưng phù, tích nước', 2, 1);

-- Khoa Sản (Specialty ID = 3)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Đau bụng kỳ kinh', N'đau bụng kỳ kinh, dysmenorrhea, đau kinh nguyệt', 3, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Rong kinh', N'rong kinh, menorrhagia, chảy máu bất thường', 3, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Vô sinh', N'vô sinh, infertility, không có con', 3, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Khí hư bất thường', N'khí hư bất thường, abnormal discharge, viêm phụ khoa', 3, 1);

-- Khoa Nhi (Specialty ID = 4)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Sốt cao ở trẻ', N'sốt cao ở trẻ, fever in children, cháy sốt', 4, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Tiêu chảy', N'tiêu chảy, diarrhea, phân lỏng, rối loạn tiêu hóa', 4, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Nôn', N'nôn, vomiting, buồn nôn, trớ sữa', 4, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm đường hô hấp', N'viêm đường hô hấp, respiratory infection, cảm lạnh', 4, 1);

-- Khoa Da liễu (Specialty ID = 5)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Mụn', N'mụn, acne, mụn trứng cá, mụn viêm', 5, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm da', N'viêm da, dermatitis, viêm da dị ứng, eczema', 5, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Khô da', N'khô da, dry skin, da khô, chứng khô', 5, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Nám da', N'nám da, melasma, tàn nhang, lão hóa da', 5, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Lang ben', N'lang ben, tinea versicolor, bệnh nấm', 5, 1);

-- Răng-Hàm-Mặt (Specialty ID = 6)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Đau răng', N'đau răng, toothache, sâu răng, viêm nướu', 6, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm nướu', N'viêm nướu, gingivitis, chảy máu chân răng', 6, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Cao răng', N'cao răng, tartar, mảng bám, vôi răng', 6, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Hôi miệng', N'hôi miệng, bad breath, mùi từ miệng', 6, 1);

-- Tai-Mũi-Họng (Specialty ID = 7)
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm họng', N'viêm họng, đau họng, throat pain, sore throat', 7, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm amidan', N'viêm amidan, tonsillitis, amidan sưng to', 7, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Viêm xoang', N'viêm xoang, sinusitis, xoang sưng, chứng xoang', 7, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Ù tai', N'ù tai, hearing loss, nặng tai, điếc một tai', 7, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Sổi mũi', N'sổi mũi, rhinitis, cảm lạnh, chảy nước mũi', 7, 1);

-- Additional common symptoms to fill out specialties
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Tức ngực', N'tức ngực, chest pain, đau lồng ngực', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Đau lưng', N'đau lưng, back pain, đau vùng thắt lưng', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Đau bụng', N'đau bụng, abdominal pain, đau vùng bụng', 1, 1);
INSERT INTO SYMPTOMS (name, keywords, specialty_id, is_active) VALUES (N'Chân tay tê', N'chân tay tê, numbness, tê ở tay chân', 1, 1);

PRINT 'Inserted 37 symptoms successfully!';
SELECT COUNT(*) as [Total Symptoms] FROM SYMPTOMS;
