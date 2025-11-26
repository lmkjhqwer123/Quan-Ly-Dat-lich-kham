// medical_history.js

if (typeof window.initMedicalHistoryPage === 'undefined') {
    window.initMedicalHistoryPage = function() {
        const historyList = document.getElementById('history-list');
        const detailModal = document.getElementById('medical-record-detail-modal');
        const searchInput = document.querySelector('input[placeholder*="Tìm kiếm"]');
        const dateFilter = document.getElementById('date-filter');
        const statusFilter = document.getElementById('status-filter');

        if (!historyList || !detailModal) {
            console.error('Required elements (history-list or medical-record-detail-modal) not found.');
            return;
        }

        const closeButtons = detailModal.querySelectorAll('.close-modal-btn');
        
        // Lưu trữ tất cả appointments
        let allAppointments = [];

        // Hàm lấy lịch sử đặt lịch khám từ API
        const fetchAppointmentHistory = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    alert('Vui lòng đăng nhập để xem lịch sử đặt lịch.');
                    return;
                }

                const response = await fetch('/api/patients/me/appointments/history', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Không thể tải lịch sử đặt lịch.');
                }

                const appointments = await response.json();
                displayAppointmentHistory(appointments);

            } catch (error) {
                console.error('Error fetching appointment history:', error);
                historyList.innerHTML = `<p class="error-message">Lỗi: ${error.message}</p>`;
            }
        };

        // Hàm hiển thị lịch sử đặt lịch khám
        const displayAppointmentHistory = (appointments) => {
            if (!appointments || appointments.length === 0) {
                historyList.innerHTML = '<p class="no-data-message">Chưa có lịch hẹn nào.</p>';
                return;
            }

            allAppointments = appointments;
            applyFiltersAndDisplay();
        };
        
        // Hàm lọc và hiển thị dữ liệu
        const applyFiltersAndDisplay = () => {
            const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
            const selectedDate = dateFilter ? dateFilter.value : '';
            const selectedStatus = statusFilter ? statusFilter.value : '';
            
            // Lọc dữ liệu
            let filteredAppointments = allAppointments.filter(appointment => {
                // Lọc theo tìm kiếm
                const matchesSearch = !searchTerm || 
                    (appointment.DoctorName && appointment.DoctorName.toLowerCase().includes(searchTerm)) ||
                    (appointment.SpecialtyName && appointment.SpecialtyName.toLowerCase().includes(searchTerm)) ||
                    (appointment.Symptoms && appointment.Symptoms.toLowerCase().includes(searchTerm));
                
                // Lọc theo ngày
                const appointmentDate = new Date(appointment.AppointmentDatetime).toISOString().split('T')[0];
                const matchesDate = !selectedDate || appointmentDate === selectedDate;
                
                // Lọc theo trạng thái
                const matchesStatus = !selectedStatus || appointment.Status === selectedStatus;
                
                return matchesSearch && matchesDate && matchesStatus;
            });
            
            renderAppointments(filteredAppointments);
        };
        
        // Hàm render appointments
        const renderAppointments = (appointments) => {
            if (!appointments || appointments.length === 0) {
                historyList.innerHTML = '<p class="no-data-message">Không tìm thấy lịch hẹn phù hợp.</p>';
                return;
            }

            historyList.innerHTML = '';

            appointments.forEach(appointment => {
                const appointmentElement = document.createElement('div');
                appointmentElement.className = 'appointment-history-item';

                const appointmentDate = new Date(appointment.AppointmentDatetime);
                const formattedDate = appointmentDate.toLocaleDateString('vi-VN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit'
                });
                const formattedTime = appointmentDate.toLocaleTimeString('vi-VN', {
                    hour: '2-digit',
                    minute: '2-digit'
                });

                const statusLabel = getStatusLabel(appointment.Status);
                const statusClass = getStatusClass(appointment.Status);
                
                // Chỉ hiển thị nút "Xem chi tiết" nếu lịch hẹn đã hoàn thành
                const isCompleted = appointment.Status === 'completed';
                const actionButtonHTML = isCompleted 
                    ? `<button class="view-record-btn" data-appointment-id="${appointment.AppointmentId}">Xem chi tiết bệnh án</button>`
                    : `<span class="text-gray-500 text-sm">Chưa có bệnh án</span>`;

                appointmentElement.innerHTML = `
                    <div class="appointment-header">
                        <div class="appointment-info">
                            <h4>Khám chuyên khoa ${appointment.SpecialtyName || 'N/A'}</h4>
                            <p class="appointment-datetime">
                                <i class="icon-calendar"></i> ${formattedDate} - ${formattedTime}
                            </p>
                            <p class="appointment-doctor">
                                <i class="icon-doctor"></i> Bác sĩ: ${appointment.DoctorName || 'Chưa xác định'}
                            </p>
                        </div>
                        <div class="appointment-status">
                            <span class="status-badge ${statusClass}">${statusLabel}</span>
                        </div>
                    </div>
                    <div class="appointment-symptoms">
                        <strong>Triệu chứng:</strong> ${appointment.Symptoms || 'Không ghi nhận'}
                    </div>
                    <div class="appointment-actions">
                        ${actionButtonHTML}
                    </div>
                `;

                historyList.appendChild(appointmentElement);
            });
        };

        // Hàm xác định nhãn trạng thái
        const getStatusLabel = (status) => {
            const statusMap = {
                'pending': 'Chờ xác nhận',
                'confirmed': 'Đã xác nhận',
                'completed': 'Hoàn thành',
                'cancelled': 'Đã hủy'
            };
            return statusMap[status] || status;
        };

        // Hàm xác định class CSS cho trạng thái
        const getStatusClass = (status) => {
            const classMap = {
                'pending': 'status-pending',
                'confirmed': 'status-confirmed',
                'completed': 'status-completed',
                'cancelled': 'status-cancelled'
            };
            return classMap[status] || 'status-unknown';
        };

        // Hàm lấy chi tiết bệnh án
        const fetchMedicalRecordDetails = async (appointmentId) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    alert('Vui lòng đăng nhập để xem chi tiết bệnh án.');
                    return;
                }

                const response = await fetch(`/api/patients/me/medical-records/${appointmentId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Không thể tải chi tiết bệnh án.');
                }

                const record = await response.json();
                populateModal(record);
                detailModal.classList.remove('hidden');

            } catch (error) {
                console.error('Error fetching medical record details:', error);
                alert(`Lỗi: ${error.message}`);
            }
        };

        // Hàm điền dữ liệu vào modal
        const populateModal = (record) => {
            // Header
            detailModal.querySelector('#modal-record-id').textContent = `#EMR-${record.MedicalRecordId || 'N/A'}`;
            detailModal.querySelector('#modal-booking-code').textContent = `#AP-${record.BookingCode || 'N/A'}`;
            detailModal.querySelector('#modal-doctor-name').textContent = `BS. ${record.DoctorName || 'N/A'}`;
            detailModal.querySelector('#modal-specialty-name').textContent = `Khoa ${record.SpecialtyName || 'N/A'}`;

            // I. Hành chính
            detailModal.querySelector('#modal-patient-name').value = record.PatientName || '';
            detailModal.querySelector('#modal-patient-dob').value = record.PatientBirthDate ? record.PatientBirthDate.split('T')[0] : '';
            detailModal.querySelector('#modal-patient-phone').value = record.PatientPhone || '';
            detailModal.querySelector('#modal-patient-address').value = record.PatientAddress || '';

            // II. Lý do vào viện
            detailModal.querySelector('#modal-patient-symptoms').value = record.PatientSymptoms || '';
            detailModal.querySelector('#modal-doctor-hpi-notes').value = record.DoctorHPINotes || '';

            // III. Khám bệnh & Chẩn đoán
            detailModal.querySelector('#modal-vitals-pulse').value = record.PulseRate || '';
            detailModal.querySelector('#modal-vitals-temperature').value = record.Temperature || '';
            detailModal.querySelector('#modal-vitals-bp').value = record.BloodPressureMMHG || '';
            detailModal.querySelector('#modal-vitals-spo2').value = record.SPO2Percent || '';
            detailModal.querySelector('#modal-physical-exam-notes').value = record.PhysicalExaminationNotes || '';
            detailModal.querySelector('#modal-diagnosis-out').value = record.DiagnosisOut || '';

            // IV. Hướng xử trí
            detailModal.querySelector('#modal-treatment-summary').value = record.TreatmentSummary || '';
        };

        const openModal = (appointmentId) => {
            // Fetch chi tiết bệnh án từ API
            console.log(`Fetching medical record for appointment ID: ${appointmentId}`);
            fetchMedicalRecordDetails(appointmentId);
        };

        const closeModal = () => {
            detailModal.classList.add('hidden');
        };

        historyList.addEventListener('click', (event) => {
            const viewButton = event.target.closest('.view-record-btn');
            if (viewButton) {
                event.preventDefault();
                const appointmentId = viewButton.dataset.appointmentId;
                openModal(appointmentId);
            }
        });

        closeButtons.forEach(btn => btn.addEventListener('click', closeModal));
        
        // Thêm event listeners cho search và filter
        if (searchInput) {
            searchInput.addEventListener('input', applyFiltersAndDisplay);
        }
        if (dateFilter) {
            dateFilter.addEventListener('change', applyFiltersAndDisplay);
        }
        if (statusFilter) {
            statusFilter.addEventListener('change', applyFiltersAndDisplay);
        }

        // Tải lịch sử đặt lịch khám khi trang được khởi tạo
        fetchAppointmentHistory();
    };
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initMedicalHistoryPage);
} else {
    window.initMedicalHistoryPage();
}