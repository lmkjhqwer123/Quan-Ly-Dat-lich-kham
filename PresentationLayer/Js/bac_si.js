// bac_si.js

if (typeof window.initBacSiPage === 'undefined') {
    window.initBacSiPage = function() {
        // DOM Elements
        const tableBody = document.getElementById('doctor-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const createNewButton = document.getElementById('create-new-button');
        
        // Filter and Sort Selects
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');
        // const sortStatusSelect = document.getElementById('sort-status');
        const sortSpecialitySelect = document.getElementById('sort-speciality');
        const sortRoomSelect = document.getElementById('sort-room');
        const resultCountSelect = document.getElementById('result-count');

        // Add/Edit Modal
        const modal = document.getElementById('doctor-modal');
        const modalTitle = document.getElementById('modal-title');
        const cancelButton = document.getElementById('cancel-btn');
        const doctorForm = document.getElementById('doctor-form');
        const doctorIdField = document.getElementById('doctor-id');
        const passwordField = document.getElementById('password-field');

        // Detail Modal
        const detailModal = document.getElementById('doctor-detail-modal');
        const closeDetailModalBtn = document.getElementById('close-doctor-detail-modal');
        const closeDetailBtn = document.getElementById('close-doctor-detail-btn');
        const detailContent = document.getElementById('doctor-detail-content');

        let specialties = [];

        // --- API Calls ---

        const fetchSpecialties = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch('/api/admin/specialties/', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch specialties.');
                specialties = await response.json();
                populateSpecialtySelects();
            } catch (error) {
                console.error('Error fetching specialties:', error);
            }
        };

        const fetchDoctors = async () => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found.');
                    tableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center">Vui lòng đăng nhập lại.</td></tr>`;
                    return;
                }

                let url = '/api/doctors/';
                const params = new URLSearchParams();

                const searchValue = searchInput.value.trim();
                if (searchValue) params.append('search', searchValue);

                const sortDir = sortDirectionSelect.value;
                if (sortDir) params.append('sort_direction', sortDir);

                const sortBy = sortValueSelect.value;
                if (sortBy) params.append('sort_value', sortBy);

                // const status = sortStatusSelect.value;
                // if (status) params.append('sort_status', status);

                const specialty = sortSpecialitySelect.value;
                if (specialty) params.append('sort_speciality', specialty);

                const room = sortRoomSelect.value;
                if (room) params.append('sort_room', room);

                const limit = resultCountSelect.value;
                if (limit) params.append('limit', limit);

                if (params.toString()) {
                    url += `?${params.toString()}`;
                }

                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const doctors = await response.json();
                renderTable(doctors);

            } catch (error) {
                console.error('Error fetching doctors:', error);
                tableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu. Vui lòng thử lại.</td></tr>`;
            }
        };

        const fetchDoctorDetails = async (id) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch(`/api/doctors/${id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Failed to fetch doctor details.');
                return await response.json();
            } catch (error) {
                console.error('Error fetching doctor details:', error);
                alert('Không thể tải thông tin chi tiết của bác sĩ.');
                return null;
            }
        };

        // --- UI Rendering ---

        const populateSpecialtySelects = () => {
            const specialtySelect = document.getElementById('specialty');
            
            specialtySelect.innerHTML = '<option value="" disabled selected>Chọn chuyên khoa</option>';
            sortSpecialitySelect.innerHTML = '<option value="">Tất cả chuyên khoa</option>';

            specialties.forEach(s => {
                const option = new Option(s.SpecialtyName, s.SpecialtyId);
                specialtySelect.add(option.cloneNode(true));
                sortSpecialitySelect.add(option);
            });
        };

        const renderTable = (doctors) => {
            tableBody.innerHTML = ''; // Clear existing rows

            if (!doctors || doctors.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không tìm thấy bác sĩ nào.</td></tr>`;
                return;
            }

            const rowsHtml = doctors.map(doctor => {
                // const statusClass = doctor.Status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
                // const statusText = doctor.Status === 'active' ? 'Hoạt động' : 'Không hoạt động';

                return `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="py-3 px-6"><img src="${doctor.Avatar || 'https://via.placeholder.com/40'}" alt="Avatar" class="w-10 h-10 rounded-full object-cover"></td>
                        <td class="py-3 px-6 font-medium">${doctor.SpecialtyName || 'N/A'}</td>
                        <td class="py-3 px-6">${doctor.FullName}</td>
                        <td class="py-3 px-6">${doctor.Phone}</td>
                        <td class="py-3 px-6">${doctor.Role || 'Bác sĩ'}</td>
                        <td class="py-3 px-6 text-center space-x-2">
                            <button class="action-link action-link-detail" data-id="${doctor.DoctorId}">Xem</button>
                            <button class="action-link action-link-edit" data-id="${doctor.DoctorId}">Sửa</button>
                            <button class="action-link action-link-delete" data-id="${doctor.DoctorId}">Xóa</button>
                        </td>
                    </tr>
                `;
            }).join('');

            tableBody.innerHTML = rowsHtml;
        };

        const showDetailModal = (doctor) => {
            if (!doctor) return;
            detailContent.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <p><strong>ID:</strong> ${doctor.DoctorId}</p>
                    <p><strong>Họ tên:</strong> ${doctor.FullName}</p>
                    <p><strong>Email:</strong> ${doctor.Email}</p>
                    <p><strong>Điện thoại:</strong> ${doctor.Phone}</p>
                    <p><strong>Chuyên khoa:</strong> ${doctor.SpecialtyName || 'N/A'}</p>
                    <p><strong>Bằng cấp:</strong> ${doctor.Qualifications || 'N/A'}</p>
                    <p><strong>Vai trò:</strong> ${doctor.Role || 'Bác sĩ'}</p>
                </div>
            `;
            detailModal.classList.remove('hidden');
        };

        // --- Modal Handling ---

        const openModalForCreate = () => {
            doctorForm.reset();
            doctorIdField.value = '';
            modalTitle.textContent = 'Thêm Bác sĩ';
            passwordField.style.display = 'block';
            modal.classList.remove('hidden');
        };

        const openModalForEdit = async (id) => {
            const doctor = await fetchDoctorDetails(id);
            if (!doctor) return;

            doctorForm.reset();
            document.getElementById('fullName').value = doctor.FullName;
            document.getElementById('email').value = doctor.Email;
            document.getElementById('phone').value = doctor.Phone;
            document.getElementById('specialty').value = doctor.SpecialtyId;
            document.getElementById('qualifications').value = doctor.Qualifications;
            document.getElementById('role').value = doctor.Role || 'Doctor';
            // document.getElementById('status').value = doctor.Status || 'active';
            doctorIdField.value = doctor.DoctorId;
            
            modalTitle.textContent = 'Sửa thông tin Bác sĩ';
            passwordField.style.display = 'none';
            modal.classList.remove('hidden');
        };

        const handleFormSubmit = async (event) => {
            event.preventDefault();
            const id = doctorIdField.value;
            const isCreating = !id;
            const token = sessionStorage.getItem('accessToken');

            const doctorData = {
                FullName: document.getElementById('fullName').value,
                Email: document.getElementById('email').value,
                Phone: document.getElementById('phone').value,
                SpecialtyId: parseInt(document.getElementById('specialty').value),
                Qualifications: document.getElementById('qualifications').value,
                Role: document.getElementById('role').value,
                // Status: document.getElementById('status').value,
            };

            if (isCreating) {
                doctorData.Password = document.getElementById('password').value;
            }

            const url = isCreating ? '/api/doctors/' : `/api/doctors/${id}`;
            const method = isCreating ? 'POST' : 'PUT';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(doctorData)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Lưu thông tin thất bại.');
                }

                modal.classList.add('hidden');
                fetchDoctors();
                alert(`Bác sĩ đã được ${isCreating ? 'tạo' : 'cập nhật'} thành công!`);

            } catch (error) {
                console.error('Error saving doctor:', error);
                alert(error.message);
            }
        };

        const handleDelete = async (id) => {
            if (!confirm('Bạn có chắc chắn muốn xóa bác sĩ này không?')) {
                return;
            }

            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch(`/api/doctors/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Xóa thất bại.');
                }
                
                fetchDoctors();
                alert('Bác sĩ đã được xóa thành công!');

            } catch (error) {
                console.error('Error deleting doctor:', error);
                alert(error.message);
            }
        };

        // --- Event Listeners ---
        const handleFilterChange = () => {
            fetchDoctors();
        };

        const setupEventListeners = () => {
            searchButton.addEventListener('click', handleFilterChange);
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    handleFilterChange();
                }
            });
            
            refreshButton.addEventListener('click', () => {
                searchInput.value = '';
                sortDirectionSelect.value = '';
                sortValueSelect.value = '';
                // sortStatusSelect.value = '';
                sortSpecialitySelect.value = '';
                sortRoomSelect.value = '';
                resultCountSelect.value = '';
                fetchDoctors();
            });

            [sortDirectionSelect, sortValueSelect, sortSpecialitySelect, sortRoomSelect, resultCountSelect].forEach(select => {
                select.addEventListener('change', handleFilterChange);
            });

            createNewButton.addEventListener('click', openModalForCreate);
            cancelButton.addEventListener('click', () => modal.classList.add('hidden'));
            doctorForm.addEventListener('submit', handleFormSubmit);

            tableBody.addEventListener('click', async (event) => {
                const button = event.target.closest('button[data-id]');
                if (!button) return;

                const id = button.dataset.id;

                if (button.classList.contains('action-link-detail')) {
                    const doctor = await fetchDoctorDetails(id);
                    showDetailModal(doctor);
                } else if (button.classList.contains('action-link-edit')) {
                    openModalForEdit(id);
                } else if (button.classList.contains('action-link-delete')) {
                    handleDelete(id);
                }
            });

            closeDetailModalBtn.addEventListener('click', () => detailModal.classList.add('hidden'));
            closeDetailBtn.addEventListener('click', () => detailModal.classList.add('hidden'));
        };

        // --- Initialization ---
        const init = () => {
            // Hide status field in the form
            const statusField = document.getElementById('status');
            if (statusField && statusField.parentElement) {
                statusField.parentElement.style.display = 'none';
            }

            setupEventListeners();
            fetchSpecialties().then(fetchDoctors);
        };

        init();
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initBacSiPage);
} else {
    window.initBacSiPage();
}
