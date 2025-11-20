
if (typeof window.initLichHenPage === 'undefined') {
    window.initLichHenPage = function() {
        const appointmentTableBody = document.getElementById('appointment-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const createNewButton = document.getElementById('create-new-button');
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');
        const sortStatusSelect = document.getElementById('sort-status');
        const sortServiceSelect = document.getElementById('sort-service');
        const examDateInput = document.getElementById('exam-date');

        // Appointment Detail Modal Elements
        const appointmentDetailModal = document.getElementById('appointment-detail-modal');
        const closeAppointmentDetailModalBtn = document.getElementById('close-appointment-detail-modal');
        const closeAppointmentDetailBtn = document.getElementById('close-appointment-detail-btn');
        const detailAppointmentId = document.getElementById('detail-appointment-id');
        const detailPatientName = document.getElementById('detail-patient-name');
        const detailDoctorSpecialty = document.getElementById('detail-doctor-specialty');
        const detailAppointmentDatetime = document.getElementById('detail-appointment-datetime');
        const detailSymptoms = document.getElementById('detail-symptoms');

        // Add/Edit Modal Elements
        const appointmentModal = document.getElementById('appointment-modal');
        const closeModalBtn = document.getElementById('close-modal-btn');
        const cancelBtn = document.getElementById('cancel-btn');

        // --- Helper Functions ---

        const updateAppointmentStatus = async (appointmentId, newStatus) => {
            console.log(`Attempting to update appointment ${appointmentId} to status: ${newStatus}`);
            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch(`/api/admin/appointments/${appointmentId}/status`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ status: newStatus }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
                }

                alert(`Lịch hẹn đã được cập nhật thành công sang trạng thái: ${newStatus}`);
                appointmentDetailModal.classList.add('hidden');
                handleFilterChange(); // Refresh the table

            } catch (error) {
                console.error('Error updating appointment status:', error);
                alert(`Lỗi khi cập nhật trạng thái: ${error.message}`);
            }
        };

        const createStatusTag = (statusText) => {
            const status = statusText ? statusText.toLowerCase() : '';
            switch (status) {
                case 'pending':
                    return `<span class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">${statusText}</span>`;
                case 'completed':
                    return `<span class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">${statusText}</span>`;
                case 'confirmed':
                    return `<span class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-green-100 text-green-800">${statusText}</span>`;
                case 'cancelled':
                    return `<span class="px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full bg-red-100 text-red-800">${statusText}</span>`;
                default:
                    return `<span>${statusText}</span>`;
            }
        };

        const renderAppointmentActions = (appointment) => {
            const actionsContainer = document.getElementById('appointment-actions');
            actionsContainer.innerHTML = '<h4 class="text-lg font-medium text-gray-800">Hành động</h4>'; // Reset
            const status = appointment.Status ? appointment.Status.toLowerCase() : '';

            if (status === 'pending') {
                actionsContainer.innerHTML += `<button id="confirm-appointment-btn" class="w-full px-4 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors">Xác nhận Lịch hẹn</button>`;
                actionsContainer.innerHTML += `<button id="cancel-appointment-btn" class="w-full px-4 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors mt-2">Hủy Lịch hẹn</button>`;
            } else if (status === 'confirmed') {
                actionsContainer.innerHTML += `<button id="cancel-appointment-btn" class="w-full px-4 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors">Hủy Lịch hẹn</button>`;
            }
        };

        const handleFilterChange = () => {
            fetchAppointments(
                searchInput.value.trim(),
                sortDirectionSelect.value,
                sortValueSelect.value,
                sortStatusSelect.value,
                sortServiceSelect.value,
                examDateInput.value
            );
        };

        // --- Main Functions ---

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

                let url = '/api/admin/appointments';
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
                    appointmentTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không tìm thấy lịch hẹn nào.</td></tr>`;
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
                    let rowClass = 'border-b border-gray-200';
                    let statusTag = '';

                    switch (status) {
                        case 'pending':
                            rowClass += ' bg-yellow-50 hover:bg-yellow-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">${appointment.Status}</span>`;
                            break;
                        case 'completed':
                            rowClass += ' bg-blue-50 hover:bg-blue-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">${appointment.Status}</span>`;
                            break;
                        case 'confirmed':
                            rowClass += ' bg-green-50 hover:bg-green-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">${appointment.Status}</span>`;
                            break;
                        case 'cancelled':
                            rowClass += ' bg-red-50 hover:bg-red-100';
                            statusTag = `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">${appointment.Status}</span>`;
                            break;
                        default:
                            rowClass += ' hover:bg-gray-50';
                            statusTag = `<span>${appointment.Status}</span>`;
                    }
                    row.className = rowClass;
 
                    const appointmentDatetime = appointment.AppointmentDatetime ? new Date(appointment.AppointmentDatetime).toLocaleString() : 'N/A';
                    const serviceNames = appointment.Services.map(s => s.name).join(', ');

                    row.innerHTML = `
                        <td class="py-4 px-6 font-medium">${appointment.AppointmentId}</td>
                        <td class="py-4 px-6">${appointment.DoctorName}</td>
                        <td class="py-4 px-6">${appointment.SpecialtyName}</td>
                        <td class="py-4 px-6">${appointmentDatetime}</td>
                        <td class="py-4 px-6">${serviceNames}</td>
                        <td class="py-4 px-6">${statusTag}</td>
                        <td class="py-4 px-6 text-center space-x-3">
                            <button class="btn-action btn-detail action-link-detail" data-id="${appointment.AppointmentId}">Chi tiết</button>
                        </td>
                    `;
                });
 
            } catch (error) {
                console.error('Error fetching appointments:', error);
                appointmentTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu lịch hẹn. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;
            }
        };

        const fetchAppointmentDetails = async (appointmentId) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    return;
                }

                const response = await fetch(`/api/admin/appointments/${appointmentId}`, {
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

                // Sửa lỗi: Sử dụng đúng các ID của modal chi tiết đã được thiết kế lại
                detailAppointmentId.textContent = `#${appointment.AppointmentId}`;
                detailPatientName.textContent = appointment.PatientName;
                detailDoctorSpecialty.textContent = `${appointment.DoctorName} - ${appointment.SpecialtyName}`;
                detailAppointmentDatetime.textContent = new Date(appointment.AppointmentDatetime).toLocaleString('vi-VN', { dateStyle: 'full', timeStyle: 'short' });
                detailSymptoms.textContent = appointment.Symptoms || 'Không có';
                // Cập nhật tag trạng thái
                document.getElementById('detail-status-tag').innerHTML = createStatusTag(appointment.Status);

                const detailServicesList = document.getElementById('detail-services');
                detailServicesList.innerHTML = ''; // Clear previous services
                if (appointment.Services && appointment.Services.length > 0) {
                    appointment.Services.forEach(service => {
                        const listItem = document.createElement('li');
                        listItem.textContent = service.name + (service.quantity > 1 ? ` (Số lượng: ${service.quantity})` : '');
                        detailServicesList.appendChild(listItem);
                    });
                } else {
                    const listItem = document.createElement('li');
                    listItem.textContent = 'Không có dịch vụ nào được đặt.';
                    detailServicesList.appendChild(listItem);
                }
 
                // 1. Hiển thị các nút hành động phù hợp với trạng thái
                renderAppointmentActions(appointment);
 
                // 2. Gán sự kiện cho các nút hành động vừa được tạo
                const confirmBtn = document.getElementById('confirm-appointment-btn');
                if (confirmBtn) {
                    // Xóa listener cũ để tránh gọi nhiều lần
                    confirmBtn.replaceWith(confirmBtn.cloneNode(true));
                    document.getElementById('confirm-appointment-btn').addEventListener('click', () => {
                        updateAppointmentStatus(appointment.AppointmentId, 'Confirmed');
                    });
                }

                const cancelBtn = document.getElementById('cancel-appointment-btn');
                if (cancelBtn) {
                    // Xóa listener cũ để tránh gọi nhiều lần
                    cancelBtn.replaceWith(cancelBtn.cloneNode(true));
                    document.getElementById('cancel-appointment-btn').addEventListener('click', () => {
                        if (confirm('Bạn có chắc chắn muốn hủy lịch hẹn này không?')) {
                            updateAppointmentStatus(appointment.AppointmentId, 'Cancelled');
                        }
                    });
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
            handleFilterChange();
        });

        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                handleFilterChange();
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

        // --- Add/Edit Modal Logic ---
        createNewButton.addEventListener('click', () => {
            appointmentModal.classList.remove('hidden');
        });

        closeModalBtn.addEventListener('click', () => {
            appointmentModal.classList.add('hidden');
        });
        cancelBtn.addEventListener('click', () => {
            appointmentModal.classList.add('hidden');
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
            handleFilterChange();
        });

        sortValueSelect.addEventListener('change', () => {
            handleFilterChange();
        });

        sortStatusSelect.addEventListener('change', () => {
            handleFilterChange();
        });

        sortServiceSelect.addEventListener('change', () => {
            handleFilterChange();
        });

        examDateInput.addEventListener('change', () => {
            handleFilterChange();
        });
    };
}

initLichHenPage();
