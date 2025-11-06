
if (typeof window.initChuyenKhoaPage === 'undefined') {
    window.initChuyenKhoaPage = function() {
        console.log("Script in chuyen_khoa.html is running!");
        // DOM Elements
        const specialtyTableBody = document.getElementById('specialty-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshBtn = document.getElementById('refresh-button');
        const sortDirectionDropdown = document.getElementById('sort-direction');
        const sortValueDropdown = document.getElementById('sort-value');
        const createButton = document.querySelector('button.bg-gray-700');

        // Modals
        const createModal = document.getElementById('create-modal');
        const cancelCreateButton = document.getElementById('cancel-create-button');
        const saveCreateButton = document.getElementById('save-create-button');
        const createNameInput = document.getElementById('create-name');
        const createDescriptionInput = document.getElementById('create-description');

        const editModal = document.getElementById('edit-modal');
        const cancelEditButton = document.getElementById('cancel-edit-button');
        const saveEditButton = document.getElementById('save-edit-button');
        const editIdInput = document.getElementById('edit-id');
        const editNameInput = document.getElementById('edit-name');
        const editDescriptionInput = document.getElementById('edit-description');

        // API URL
        const API_URL = '/api/admin/specialties/';

        // Functions
        const fetchSpecialties = async (searchQuery = '', sortDirection = '', sortBy = '') => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    // Redirect to login or show an error
                    return;
                }

                const params = new URLSearchParams();
                if (searchQuery) params.append('query', searchQuery);
                if (sortDirection) params.append('sort_direction', sortDirection);
                if (sortBy) params.append('sort_by', sortBy);

                const url = `${API_URL}?${params.toString()}`;
                const response = await fetch(url, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const specialties = await response.json();
                renderSpecialtyTable(specialties);
            } catch (error) {
                console.error('Error fetching specialties:', error);
                specialtyTableBody.innerHTML = `<tr><td colspan="4" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu chuyên khoa.</td></tr>`;
            }
        };

        const renderSpecialtyTable = (specialties) => {
            specialtyTableBody.innerHTML = ''; // Clear existing data

            if (!specialties || specialties.length === 0) {
                specialtyTableBody.innerHTML = `<tr><td colspan="4" class="py-3 px-6 text-center text-gray-500">Không tìm thấy chuyên khoa nào.</td></tr>`;
                return;
            }

            specialties.forEach(specialty => {
                const row = document.createElement('tr');
                row.className = 'border-b border-gray-200 hover:bg-gray-50';
                row.innerHTML = `
                    <td class="py-4 px-6 font-medium">${specialty.SpecialtyId}</td>
                    <td class="py-4 px-6">${specialty.Name}</td>
                    <td class="py-4 px-6">${specialty.description || ''}</td>
                    <td class="py-4 px-6 space-x-2">
                        <button class="btn-action btn-edit" data-id="${specialty.SpecialtyId}" data-name="${specialty.Name}" data-description="${specialty.description || ''}">Sửa</button>
                        <button class="btn-action btn-delete" data-id="${specialty.SpecialtyId}">Xóa</button>
                    </td>
                `;
                specialtyTableBody.appendChild(row);
            });
        };

        const handleApiAction = async (url, options, successMessage, failureMessage) => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    alert('Authentication error. Please log in again.');
                    return false;
                }

                const response = await fetch(url, {
                    ...options,
                    headers: {
                        ...options.headers,
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }
                
                if (response.status !== 204) { // No content for DELETE
                    await response.json();
                }

                // alert(successMessage); // Optional
                fetchSpecialties(); // Refresh table
                return true;
            } catch (error) {
                console.error(failureMessage, error);
                alert(`${failureMessage}: ${error.message}`);
                return false;
            }
        };

        const createSpecialty = async (name, description) => {
            const success = await handleApiAction(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Name: name, description: description })
            }, 'Tạo chuyên khoa thành công!', 'Tạo chuyên khoa thất bại');
            
            if (success) {
                createModal.classList.add('hidden');
                createNameInput.value = '';
                createDescriptionInput.value = '';
            }
        };

        const updateSpecialty = async (id, name, description) => {
            const success = await handleApiAction(`${API_URL}${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ Name: name, description: description })
            }, 'Cập nhật chuyên khoa thành công!', 'Cập nhật chuyên khoa thất bại');

            if (success) {
                editModal.classList.add('hidden');
            }
        };

        const deleteSpecialty = (id) => {
            if (confirm('Bạn có chắc chắn muốn xóa chuyên khoa này không?')) {
                handleApiAction(`${API_URL}${id}`, { method: 'DELETE' }, 'Xóa chuyên khoa thành công!', 'Xóa chuyên khoa thất bại.');
            }
        };
        
        const openEditModal = (target) => {
            editIdInput.value = target.dataset.id;
            editNameInput.value = target.dataset.name;
            editDescriptionInput.value = target.dataset.description;
            editModal.classList.remove('hidden');
        };

        // Event Listeners
        const setupEventListeners = () => {
            // Use a flag to prevent duplicate listeners
            if (searchButton.dataset.listenerAttached) {
                return;
            }
            searchButton.dataset.listenerAttached = 'true';

            searchButton.addEventListener('click', () => {
                fetchSpecialties(searchInput.value.trim(), sortDirectionDropdown.value, sortValueDropdown.value);
            });

            searchInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    searchButton.click();
                }
            });

            refreshBtn.addEventListener('click', () => {
                searchInput.value = '';
                sortDirectionDropdown.value = '';
                sortValueDropdown.value = '';
                fetchSpecialties();
            });

            sortDirectionDropdown.addEventListener('change', () => searchButton.click());
            sortValueDropdown.addEventListener('change', () => searchButton.click());

            // Modal listeners
            createButton.addEventListener('click', () => createModal.classList.remove('hidden'));
            cancelCreateButton.addEventListener('click', () => createModal.classList.add('hidden'));
            saveCreateButton.addEventListener('click', () => {
                createSpecialty(createNameInput.value, createDescriptionInput.value);
            });

            cancelEditButton.addEventListener('click', () => editModal.classList.add('hidden'));
            saveEditButton.addEventListener('click', () => {
                updateSpecialty(editIdInput.value, editNameInput.value, editDescriptionInput.value);
            });

            // Event Delegation for table actions
            specialtyTableBody.addEventListener('click', (e) => {
                const target = e.target;
                if (target.classList.contains('btn-edit')) {
                    openEditModal(target);
                } else if (target.classList.contains('btn-delete')) {
                    deleteSpecialty(target.dataset.id);
                }
            });
        };

        // Initial Load
        setupEventListeners();
        fetchSpecialties();
    }
}
initChuyenKhoaPage();