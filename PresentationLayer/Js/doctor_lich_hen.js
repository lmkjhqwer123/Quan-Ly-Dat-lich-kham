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
        const modalConfirmBtn = document.getElementById('modal-confirm-appointment-btn');
        const modalCancelBtn = document.getElementById('modal-cancel-appointment-btn');
        const modalCompleteBtn = document.getElementById('modal-complete-appointment-btn');

        // EMR (Medical Record) Modal Elements
        const emrModal = document.getElementById('create-medical-record-modal');
        const closeEmrModalBtn = document.getElementById('close-emr-modal');
        const emrForm = document.getElementById('emr-form');

        let currentAppointmentId = null; // To store the ID of the appointment in the modal

        // Hide buttons by default, show them based on status
        modalConfirmBtn.style.display = 'none';
        modalCancelBtn.style.display = 'none';
        modalCompleteBtn.style.display = 'none';
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
                sortServiceSelect.innerHTML = '<option value="">Tất cả</option>'; // Clear existing options
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
                    console.error('No access token found.');
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

                // --- Sắp xếp ưu tiên hiển thị ---
                const getPriority = (appointment) => {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);

                    const appointmentDate = new Date(appointment.AppointmentDatetime);
                    appointmentDate.setHours(0, 0, 0, 0);

                    // Ưu tiên 1: Lịch hẹn của ngày hôm nay
                    if (appointmentDate.getTime() === today.getTime()) {
                        return 1;
                    }
                    // Ưu tiên 2: Lịch hẹn đang chờ xử lý (pending)
                    if (appointment.Status && appointment.Status.toLowerCase() === 'pending') {
                        return 2;
                    }
                    // Ưu tiên 3: Các lịch hẹn khác
                    return 3;
                };

                appointments.sort((a, b) => {
                    const priorityA = getPriority(a);
                    const priorityB = getPriority(b);

                    if (priorityA !== priorityB) {
                        return priorityA - priorityB; // Sắp xếp theo mức độ ưu tiên
                    }

                    // Nếu cùng mức ưu tiên, sắp xếp theo thời gian hẹn (gần nhất lên trước)
                    return new Date(a.AppointmentDatetime) - new Date(b.AppointmentDatetime);
                });

                appointments.forEach(appointment => {
                    const row = appointmentTableBody.insertRow();
                    
                    // --- Thêm màu sắc cho hàng và trạng thái ---
                    const status = appointment.Status ? appointment.Status.toLowerCase() : '';
                    let rowClass = 'border-b border-gray-200 transition-colors duration-200';
                    let statusTag = '';

                    switch (status) {
                        case 'pending':
                            rowClass += ' bg-yellow-50 hover:bg-yellow-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Chờ xác nhận</span>`;
                            break;
                        case 'confirmed':
                            rowClass += ' bg-blue-50 hover:bg-blue-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Đã xác nhận</span>`;
                            break;
                        case 'completed':
                            rowClass += ' bg-green-50 hover:bg-green-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Đã hoàn thành</span>`;
                            break;
                        case 'cancelled':
                            rowClass += ' bg-red-50 hover:bg-red-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Đã hủy</span>`;
                            break;
                        default:
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">${appointment.Status}</span>`;
                    }

                    row.className = rowClass;

                    const appointmentDatetime = appointment.AppointmentDatetime ? new Date(appointment.AppointmentDatetime).toLocaleString('vi-VN', {
                        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
                    }) : 'N/A';
                    const serviceNames = appointment.Services.map(s => s.name).join(', ');

                    // --- Tạo các nút hành động ---
                    let actionsHtml = `<button class="btn-action btn-view-detail action-link-detail" data-id="${appointment.AppointmentId}">Chi tiết</button>`;
                    if (status === 'confirmed') {
                        actionsHtml += ` <button class="btn-action btn-create-record" onclick="createMedicalRecord(${appointment.AppointmentId})">Tạo bệnh án</button>`;
                    }


                    row.innerHTML = `
                        <td class="py-4 px-6 font-medium">${appointment.AppointmentId}</td>
                        <td class="py-4 px-6">${appointment.PatientName}</td>
                        <td class="py-4 px-6">${appointment.SpecialtyName}</td>
                        <td class="py-4 px-6 whitespace-nowrap">${appointmentDatetime}</td>
                        <td class="py-4 px-6">${serviceNames}</td>
                        <td class="py-4 px-6">${statusTag}</td>
                        <td class="py-4 px-6 text-center space-x-3">
                            ${actionsHtml}
                        </td> 
                    `;
                });

            } catch (error) {
                console.error('Error fetching appointments:', error);
                appointmentTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu lịch hẹn.</td></tr>`;
            }
        };

        // --- Hàm xử lý cho nút "Tạo bệnh án" ---
        window.createMedicalRecord = function(appointmentId) {
            console.log(`Opening EMR modal for appointment ID: ${appointmentId}`);
            // Fetch appointment details and populate the EMR form
            populateAndShowEmrModal(appointmentId);
        };

        const populateAndShowEmrModal = async (appointmentId) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch(`/api/doctor/appointments/${appointmentId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch appointment details for EMR.');
                
                const appointment = await response.json();
                console.log('Appointment details for EMR:', appointment);

                // Populate EMR form
                document.getElementById('emr-appointment-id').textContent = `#AP-${appointment.AppointmentId}`;
                document.getElementById('emr-doctor-name').textContent = appointment.DoctorName;
                document.getElementById('emr-specialty-name').textContent = appointment.SpecialtyName;
                document.getElementById('emr-patient-name').value = appointment.PatientName;
                document.getElementById('emr-patient-dob').value = appointment.PatientBirthDate ? appointment.PatientBirthDate.split('T')[0] : '';
                // document.getElementById('emr-patient-gender').value = appointment.PatientGender;
                document.getElementById('emr-patient-phone').value = appointment.PatientPhone;
                document.getElementById('emr-patient-address').value = appointment.PatientAddress || 'Chưa cung cấp';
                document.getElementById('emr-patient-symptoms').value = appointment.Symptoms || 'Không có';

            } catch (error) {
                console.error('Error populating EMR modal:', error);
                alert('Không thể tải thông tin để tạo bệnh án. Vui lòng thử lại.');
            }

            // Hiển thị modal
            emrModal.classList.remove('hidden');
        };


        const fetchAppointmentDetails = async (appointmentId) => {
            currentAppointmentId = appointmentId; // Store the current ID
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

                // --- Populate Modal ---
                document.querySelector('#detail-appointment-id').textContent = appointment.AppointmentId;
                document.getElementById('detail-patient-name').textContent = appointment.PatientName;
                document.getElementById('detail-doctor-name').textContent = appointment.DoctorName;
                document.getElementById('detail-specialty-name').textContent = appointment.SpecialtyName;
                document.getElementById('detail-appointment-datetime').textContent = new Date(appointment.AppointmentDatetime).toLocaleString('vi-VN');
                document.getElementById('detail-symptoms').textContent = appointment.Symptoms;

                // --- Status Tag in Modal ---
                const statusSpan = document.getElementById('detail-status');
                const status = appointment.Status.toLowerCase();
                let statusTag = '';
                 switch (status) {
                    case 'pending':
                        statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-200 text-yellow-800">Pending</span>`;
                        modalConfirmBtn.style.display = 'inline-block';
                        modalCancelBtn.style.display = 'inline-block';
                        modalCompleteBtn.style.display = 'none';
                        break;
                    case 'confirmed':
                        statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-200 text-green-800">Confirmed</span>`;
                        modalConfirmBtn.style.display = 'none';
                        modalCancelBtn.style.display = 'inline-block';
                        modalCompleteBtn.style.display = 'inline-block';
                        break;
                    default: // completed, cancelled
                        statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-200 text-gray-800">${appointment.Status}</span>`;
                        modalConfirmBtn.style.display = 'none';
                        modalCancelBtn.style.display = 'none';
                        modalCompleteBtn.style.display = 'none';
                        break;
                }
                if (status === 'completed') statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-200 text-blue-800">Completed</span>`;
                if (status === 'cancelled') statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-200 text-red-800">Cancelled</span>`;
                statusSpan.innerHTML = statusTag;
                
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

        const updateAppointmentStatus = async (appointmentId, newStatus) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    alert('Phiên đăng nhập đã hết hạn.');
                    return;
                }

                const response = await fetch(`/api/doctor/appointments/${appointmentId}/status`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Cập nhật trạng thái thất bại.');
                }

                alert(`Lịch hẹn đã được cập nhật thành: ${newStatus}`);
                appointmentDetailModal.classList.add('hidden');
                // Refresh the list to show the changes
                fetchAppointments(
                    searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value,
                    sortStatusSelect.value, sortServiceSelect.value, examDateInput.value
                );

            } catch (error) {
                console.error('Error updating appointment status:', error);
                alert(`Lỗi: ${error.message}`);
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
            sortDirectionSelect.value = 'asc';
            sortValueSelect.value = 'time';
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

        // Modal action buttons
        modalConfirmBtn.addEventListener('click', () => {
            if (currentAppointmentId) {
                updateAppointmentStatus(currentAppointmentId, 'confirmed');
            }
        });

        modalCancelBtn.addEventListener('click', () => {
            if (currentAppointmentId && confirm('Bạn có chắc chắn muốn hủy lịch hẹn này?')) {
                updateAppointmentStatus(currentAppointmentId, 'cancelled');
            }
        });

        modalCompleteBtn.addEventListener('click', () => {
            if (currentAppointmentId) {
                updateAppointmentStatus(currentAppointmentId, 'completed');
            }
        });

        const handleFilterChange = () => {
            fetchAppointments(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value,
                              sortStatusSelect.value, sortServiceSelect.value, examDateInput.value);
        };

        [sortDirectionSelect, sortValueSelect, sortStatusSelect, sortServiceSelect, examDateInput].forEach(el => {
            el.addEventListener('change', handleFilterChange);
        });

        // EMR Modal close button
        closeEmrModalBtn.addEventListener('click', () => {
            emrModal.classList.add('hidden');
            emrForm.reset(); // Reset form fields when closing
        });

        // --- Xử lý sự kiện "Hoàn tất khám" ---
        emrForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Ngăn form gửi đi theo cách truyền thống

            const token = sessionStorage.getItem('accessToken');
            if (!token) {
                alert('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
                window.location.href = '/login.html'; // Redirect to login
                return;
            }

            const appointmentIdText = document.getElementById('emr-appointment-id').textContent;
            const appointmentId = parseInt(appointmentIdText.replace('#AP-', ''));

            const medicalRecordData = {
                appointment_id: appointmentId,
                patient_symptoms: document.getElementById('emr-patient-symptoms')?.value || null,
                doctor_notes: document.getElementById('emr-doctor-notes')?.value || null,
                clinical_summary: document.getElementById('emr-clinical-summary')?.value || null,
                preliminary_diagnosis: document.getElementById('emr-preliminary-diagnosis')?.value,
                doctor_advice: document.getElementById('emr-doctor-advice')?.value || null,
                vitals: {
                    pulse: parseInt(document.getElementById('emr-vitals-pulse')?.value) || null,
                    temperature: parseFloat(document.getElementById('emr-vitals-temperature')?.value) || null,
                    blood_pressure: document.getElementById('emr-vitals-bp')?.value || null,
                    spo2: parseFloat(document.getElementById('emr-vitals-spo2')?.value) || null,
                }
            };

            // Basic validation for required fields
            if (!medicalRecordData.preliminary_diagnosis) {
                alert('Vui lòng nhập chẩn đoán sơ bộ.');
                return;
            }

            try {
                const response = await fetch('/api/doctor/medical-records', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(medicalRecordData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Lỗi khi tạo bệnh án.');
                }

                const result = await response.json();
                alert(`Bệnh án đã được tạo thành công! Mã bệnh án: ${result.medical_record_id}`);
                
                // Ask doctor to update appointment status to completed
                const confirmCompletion = confirm('Bạn có muốn thay đổi trạng thái cuộc hẹn thành "Đã hoàn thành" không?');
                if (confirmCompletion && appointmentId) {
                    await updateAppointmentStatus(appointmentId, 'completed');
                }

                emrModal.classList.add('hidden'); // Close modal
                emrForm.reset(); // Reset form
                // Refresh appointment list to reflect status change
                fetchAppointments(
                    searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value,
                    sortStatusSelect.value, sortServiceSelect.value, examDateInput.value
                );

            } catch (error) {
                console.error('Error creating medical record:', error);
                alert(`Lỗi: ${error.message}`);
            }
        });

    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorLichHenPage);
} else {
    window.initDoctorLichHenPage();
}
