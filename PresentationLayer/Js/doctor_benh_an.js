// doctor_benh_an.js

if (typeof window.initDoctorBenhAnPage === 'undefined') {
    window.initDoctorBenhAnPage = function() {
        const tableBody = document.getElementById('medical-record-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');
        const resultCountSelect = document.getElementById('result-count');
        // Removed sortSpecialitySelect as it's not in doctor_benh_an.html

        const fetchMedicalRecords = async (searchQuery = '', sortDir = '', sortBy = '', limit = '') => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    // Optionally redirect to login or show an error
                    // window.location.href = '/login.html';
                    return;
                }

                let url = '/api/doctor/medical-records'; // This endpoint handles doctor-specific filtering based on role
                const params = new URLSearchParams();

                if (searchQuery) {
                    params.append('search', searchQuery);
                }
                if (sortDir) {
                    params.append('sort_direction', sortDir);
                }
                if (sortBy) {
                    params.append('sort_by', sortBy);
                }
                if (limit) {
                    params.append('limit', limit);
                }

                if (params.toString()) {
                    url += `?${params.toString()}`;
                }

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const records = await response.json();
                renderTable(records);

            } catch (error) {
                console.error('Error fetching medical records:', error);
                tableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu. Vui lòng thử lại.</td></tr>`;
            }
        };

        const renderTable = (records) => {
            tableBody.innerHTML = '';

            if (records.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không tìm thấy bệnh án nào.</td></tr>`;
                return;
            }

            records.forEach(record => {
                const row = tableBody.insertRow();
                row.className = 'border-b border-gray-200 hover:bg-gray-50';
                row.dataset.recordId = record.MedicalRecordId;

                const examDate = new Date(record.ExaminationDate).toLocaleDateString('vi-VN', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });

                row.innerHTML = `
                    <td class="py-4 px-6 font-medium">${record.BookingCode || '#N/A'}</td>
                    <td class="py-4 px-6">
                        <span class="font-medium">${record.PatientName}</span>
                    </td>
                    <td class="py-4 px-6">${record.SpecialtyName}</td>
                    <td class="py-4 px-6">${examDate}</td>
                    <td class="py-4 px-6 text-sm">${record.DiagnosisOut}</td>
                    <td class="py-4 px-6 text-center space-x-2">
                        <button class="btn-action btn-detail" data-id="${record.MedicalRecordId}">Xem chi tiết</button>
                    </td>
                `;
            });
        };

        const handleFilterChange = () => {
            fetchMedicalRecords(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                resultCountSelect.value
            );
        };

        // Event Listeners
        searchButton.addEventListener('click', handleFilterChange);
        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                handleFilterChange();
            }
        });
        refreshButton.addEventListener('click', () => {
            searchInput.value = '';
            sortDirectionSelect.value = '';
            sortValueSelect.value = '';
            resultCountSelect.value = '';
            fetchMedicalRecords();
        });
        sortDirectionSelect.addEventListener('change', handleFilterChange);
        sortValueSelect.addEventListener('change', handleFilterChange);
        resultCountSelect.addEventListener('change', handleFilterChange);

        // Initial Fetch
        fetchMedicalRecords();

        // Medical Record Detail Modal
        const detailModal = document.getElementById('medical-record-detail-modal');
        const closeDetailModalBtn = document.getElementById('close-medical-record-detail-modal');
        const closeDetailBtn = document.getElementById('close-medical-record-detail-btn');


        tableBody.addEventListener('click', async (event) => {
            if (event.target.classList.contains('btn-detail')) {
                const recordId = event.target.dataset.id;
                try {
                    const token = sessionStorage.getItem('accessToken');
                    const response = await fetch(`/api/doctor/medical-records/${recordId}`, { // Still using admin endpoint, backend filters
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (!response.ok) {
                        throw new Error('Failed to fetch record details.');
                    }
                    const record = await response.json();
                    
                    document.getElementById('detail-medical-record-id').textContent = record.MedicalRecordId;
                    document.getElementById('detail-booking-code').textContent = record.BookingCode || 'N/A';
                    document.getElementById('detail-patient-name').textContent = record.PatientName;
                    document.getElementById('detail-doctor-name').textContent = record.DoctorName;

                    const examDate = new Date(record.ExaminationDate).toLocaleDateString('vi-VN', {
                        day: '2-digit', month: '2-digit', year: 'numeric'
                    });
                    document.getElementById('detail-specialty-name').textContent = record.SpecialtyName;
                    document.getElementById('detail-examination-date').textContent = examDate;
                    document.getElementById('detail-diagnosis-out').textContent = record.DiagnosisOut || 'Chưa có chẩn đoán';
                    document.getElementById('detail-diagnosis-in').textContent = record.DiagnosisIn || 'N/A';
                    document.getElementById('detail-doctor-hpi-notes').textContent = record.DoctorHPINotes || 'N/A';
                    document.getElementById('detail-physical-examination-notes').textContent = record.PhysicalExaminationNotes || 'N/A';
                    document.getElementById('detail-treatment-summary').textContent = record.TreatmentSummary || 'N/A';
                    document.getElementById('detail-pulse-rate').textContent = record.PulseRate || 'N/A';
                    document.getElementById('detail-temperature').textContent = record.Temperature || 'N/A';
                    document.getElementById('detail-blood-pressure-mmhg').textContent = record.BloodPressureMMHG || 'N/A';
                    document.getElementById('detail-spo2-percent').textContent = record.SPO2Percent || 'N/A';

                    detailModal.classList.remove('hidden');
                } catch (error) {
                    console.error('Error fetching record details:', error);
                    alert('Không thể tải chi tiết bệnh án.');
                }
            }
        });

        closeDetailModalBtn.addEventListener('click', () => detailModal.classList.add('hidden'));
        closeDetailBtn.addEventListener('click', () => detailModal.classList.add('hidden'));
    }
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorBenhAnPage);
} else {
    window.initDoctorBenhAnPage();
}