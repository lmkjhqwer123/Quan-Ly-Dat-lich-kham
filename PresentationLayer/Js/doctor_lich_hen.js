// doctor_lich_hen.js

if (typeof window.initDoctorLichHenPage === 'undefined') {
    window.initDoctorLichHenPage = function() {
        const appointmentTableBody = document.getElementById('appointment-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');
        const sortStatusSelect = document.getElementById('sort-status');
        const sortServiceSelect = document.getElementById('sort-service');
        const examDateInput = document.getElementById('exam-date');

        // Appointment Detail Modal Elements
        const appointmentDetailModal = document.getElementById('appointment-detail-modal');
        const closeAppointmentDetailModalBtn = document.getElementById('close-appointment-detail-modal');
        const closeAppointmentDetailBtn = document.getElementById('close-appointment-detail-btn');

        const fetchServicesAndPopulateDropdown = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    return;
                }

                const response = await fetch('/api/services', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error(`HTTP error! status: ${response.status}, errorData:`, errorData);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const services = await response.json();
                sortServiceSelect.innerHTML = '<option value="" disabled selected>Chọn...</option>'; // Clear existing options
                services.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service.id;
                    option.textContent = service.name;
                    sortServiceSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching services:', error);
            }
        };

        const fetchAppointments = async (searchQuery = '', sortDir = '', sortBy = '', status = '', service = '', examDate = '') => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    // Optionally redirect to login page
                    // window.location.href = '/login.html';
                    return;
                }

                let url = '/api/doctor/appointments/me'; // Doctor-specific endpoint
                const params = new URLSearchParams();

                if (searchQuery) {
                    params.append('query', searchQuery);
                }
                if (sortDir) {
                    params.append('sort_direction', sortDir);
                }
                if (sortBy) {
                    params.append('sort_by', sortBy);
                }
                if (status) {
                    params.append('status', status);
                }
                if (service) {
                    params.append('service', service);
                }
                if (examDate) {
                    params.append('exam_date', examDate);
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
                    const errorData = await response.json();
                    console.error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}, errorData:`, errorData);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const appointments = await response.json();
                console.log('Fetched appointments:', appointments);
                appointmentTableBody.innerHTML = ''; // Clear existing rows

                if (appointments.length === 0) {
                    appointmentTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-gray-500">Không tìm thấy lịch hẹn nào.</td></tr>`;
                    return;
                }

                appointments.forEach(appointment => {
                    const row = appointmentTableBody.insertRow();
                    row.className = 'border-b border-gray-200 hover:bg-gray-50';

                    const appointmentDatetime = appointment.AppointmentDatetime ? new Date(appointment.AppointmentDatetime).toLocaleString() : 'N/A';
                    const serviceNames = appointment.Services.map(s => s.name).join(', ');

                    row.innerHTML = `
                        <td class="py-4 px-6 font-medium">${appointment.AppointmentId}</td>
                        <td class="py-4 px-6">${appointment.PatientName}</td>
                        <td class="py-4 px-6">${appointment.SpecialtyName}</td>
                        <td class="py-4 px-6">${appointmentDatetime}</td>
                        <td class="py-4 px-6">${serviceNames}</td>
                        <td class="py-4 px-6">${appointment.Status}</td>
                        <td class="py-4 px-6 text-center space-x-3">
                            <button class="btn-action btn-detail action-link-detail" data-id="${appointment.AppointmentId}">Chi tiết</button>
                        </td>
                    `;
                });

            } catch (error) {
                console.error('Error fetching appointments:', error);
                appointmentTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu lịch hẹn. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;
            }
        };

        const fetchAppointmentDetails = async (appointmentId) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    return;
                }

                const response = await fetch(`/api/doctor/appointments/${appointmentId}`, { // Doctor-specific endpoint
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);
                }

                const appointment = await response.json();

                document.getElementById('detail-appointment-id').textContent = appointment.AppointmentId;
                document.getElementById('detail-patient-name').textContent = appointment.PatientName;
                document.getElementById('detail-doctor-name').textContent = appointment.DoctorName;
                document.getElementById('detail-specialty-name').textContent = appointment.SpecialtyName;
                document.getElementById('detail-appointment-datetime').textContent = new Date(appointment.AppointmentDatetime).toLocaleString();
                document.getElementById('detail-status').textContent = appointment.Status;
                document.getElementById('detail-symptoms').textContent = appointment.Symptoms;

                const detailServicesList = document.getElementById('detail-services');
                detailServicesList.innerHTML = ''; // Clear previous services
                if (appointment.Services && appointment.Services.length > 0) {
                    appointment.Services.forEach(service => {
                        const listItem = document.createElement('li');
                        listItem.textContent = `${service.name} (Số lượng: ${service.quantity})`;
                        detailServicesList.appendChild(listItem);
                    });
                } else {
                    const listItem = document.createElement('li');
                    listItem.textContent = 'Không có dịch vụ nào được đặt.';
                    detailServicesList.appendChild(listItem);
                }

                appointmentDetailModal.classList.remove('hidden');

            } catch (error) {
                console.error('Lỗi khi tải chi tiết lịch hẹn:', error);
                alert('Lỗi khi tải chi tiết lịch hẹn. Vui lòng kiểm tra console.');
            }
        };

        // Initial fetch with current filter/sort values
        fetchServicesAndPopulateDropdown();
        fetchAppointments(
            searchInput.value.trim(),
            sortDirectionSelect.value,
            sortValueSelect.value,
            sortStatusSelect.value,
            sortServiceSelect.value,
            examDateInput.value
        );

        // Event Listeners
        searchButton.addEventListener('click', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });

        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                fetchAppointments(
                    searchInput.value.trim(),
                    sortDirectionSelect.value,
                    sortValueSelect.value,
                    sortStatusSelect.value,
                    sortServiceSelect.value,
                    examDateInput.value
                );
            }
        });

        refreshButton.addEventListener('click', () => {
            searchInput.value = '';
            sortDirectionSelect.value = '';
            sortValueSelect.value = '';
            sortStatusSelect.value = '';
            sortServiceSelect.value = '';
            examDateInput.value = '';
            fetchAppointments();
        });

        appointmentTableBody.addEventListener('click', async (event) => {
            const target = event.target;
            if (target.classList.contains('action-link-detail')) {
                event.preventDefault();
                const appointmentId = target.dataset.id;
                fetchAppointmentDetails(appointmentId);
            }
        });

        closeAppointmentDetailModalBtn.addEventListener('click', () => {
            appointmentDetailModal.classList.add('hidden');
        });

        closeAppointmentDetailBtn.addEventListener('click', () => {
            appointmentDetailModal.classList.add('hidden');
        });

        // Add event listeners for sort and filter changes
        sortDirectionSelect.addEventListener('change', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });

        sortValueSelect.addEventListener('change', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });

        sortStatusSelect.addEventListener('change', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });

        sortServiceSelect.addEventListener('change', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });

        examDateInput.addEventListener('change', () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        });
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorLichHenPage);
} else {
    window.initDoctorLichHenPage();
}
