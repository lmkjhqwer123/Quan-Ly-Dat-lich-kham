// medical_history.js

if (typeof window.initMedicalHistoryPage === 'undefined') {
    window.initMedicalHistoryPage = function() {
        const historyList = document.getElementById('history-list');
        const detailModal = document.getElementById('medical-record-detail-modal');

        if (!historyList || !detailModal) {
            console.error('Required elements (history-list or medical-record-detail-modal) not found.');
            return;
        }

        const closeButtons = detailModal.querySelectorAll('.close-modal-btn');

        const fetchMedicalRecordDetails = async (recordId) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    alert('Vui lòng đăng nhập để xem chi tiết.');
                    // window.location.href = '/login.html'; // Optionally redirect
                    return;
                }

                // The endpoint should be specific to the logged-in patient
                const response = await fetch(`/api/patients/me/medical-records/${recordId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Không thể tải chi tiết bệnh án.');
                }

                const record = await response.json();
                populateModal(record);

            } catch (error) {
                console.error('Error fetching medical record details:', error);
                alert(`Lỗi: ${error.message}`);
            }
        };

        const populateModal = (record) => {
            // Header
            detailModal.querySelector('#modal-record-id').textContent = `#EMR-${record.MedicalRecordId}`;
            detailModal.querySelector('#modal-booking-code').textContent = `#AP-${record.BookingCode || 'N/A'}`;
            detailModal.querySelector('#modal-doctor-name').textContent = `BS. ${record.DoctorName}`;
            detailModal.querySelector('#modal-specialty-name').textContent = `Khoa ${record.SpecialtyName}`;

            // I. Hành chính
            detailModal.querySelector('#modal-patient-name').value = record.PatientName;
            const examDate = new Date(record.ExaminationDate);
            detailModal.querySelector('#modal-patient-dob').value = record.PatientBirthDate ? record.PatientBirthDate.split('T')[0] : 'N/A';
            detailModal.querySelector('#modal-patient-phone').value = record.PatientPhone;
            detailModal.querySelector('#modal-patient-address').value = record.PatientAddress || 'N/A';

            // II. Lý do vào viện
            detailModal.querySelector('#modal-patient-symptoms').value = record.PatientSymptoms || 'Không có';
            detailModal.querySelector('#modal-doctor-hpi-notes').value = record.DoctorHPINotes || 'Chưa có ghi nhận';

            // III. Khám bệnh & Chẩn đoán
            detailModal.querySelector('#modal-vitals-pulse').value = record.PulseRate || '';
            detailModal.querySelector('#modal-vitals-temperature').value = record.Temperature || '';
            detailModal.querySelector('#modal-vitals-bp').value = record.BloodPressureMMHG || '';
            detailModal.querySelector('#modal-vitals-spo2').value = record.SPO2Percent || '';
            detailModal.querySelector('#modal-physical-exam-notes').value = record.PhysicalExaminationNotes || 'Chưa có ghi nhận';
            detailModal.querySelector('#modal-diagnosis-out').value = record.DiagnosisOut || 'Chưa có chẩn đoán';

            // IV. Hướng xử trí
            detailModal.querySelector('#modal-treatment-summary').value = record.TreatmentSummary || 'Chưa có';

            // Show the modal
            detailModal.classList.remove('hidden');
        };

        const openModal = (recordId) => {
            // For now, using mock data. Replace with API call.
            console.log(`Fetching details for record ID: ${recordId}`);
            // In a real scenario, you would call:
            // fetchMedicalRecordDetails(recordId);

            // Using mock data for demonstration
            const mockRecord = {
                MedicalRecordId: recordId, BookingCode: '98765', DoctorName: 'Nguyễn Văn A', SpecialtyName: 'Tim mạch',
                PatientName: 'Nguyễn Thị C', PatientBirthDate: '1990-05-20T00:00:00', PatientPhone: '0905123456', PatientAddress: '123 Đà Nẵng, Việt Nam',
                ExaminationDate: '2024-06-15T09:30:00', PatientSymptoms: 'Đau ngực, khó thở khi gắng sức.',
                DoctorHPINotes: 'Bệnh nhân khai đau ngực âm ỉ, xuất hiện sau khi leo cầu thang.',
                PulseRate: 88, Temperature: 37.1, BloodPressureMMHG: '130/85', SPO2Percent: 98,
                PhysicalExaminationNotes: 'Tim đều, phổi trong, không ran.',
                DiagnosisOut: 'Theo dõi bệnh mạch vành',
                TreatmentSummary: 'Tái khám sau 1 tháng. Uống thuốc theo đơn. Hạn chế gắng sức.'
            };
            populateModal(mockRecord);
        };

        const closeModal = () => {
            detailModal.classList.add('hidden');
        };

        historyList.addEventListener('click', (event) => {
            const viewButton = event.target.closest('.view-record-btn');
            if (viewButton) {
                event.preventDefault();
                const recordId = viewButton.dataset.recordId;
                openModal(recordId);
            }
        });

        closeButtons.forEach(btn => btn.addEventListener('click', closeModal));
    };
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initMedicalHistoryPage);
} else {
    window.initMedicalHistoryPage();
}