if (typeof window.initDichVuPage === 'undefined') {
    window.initDichVuPage = function() {
        const serviceTableBody = document.getElementById('service-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const createNewButton = document.getElementById('create-new-button');
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');
        // const resultCountSelect = document.getElementById('result-count'); // Commented out as it's commented in HTML

        // Create Service Modal Elements
        const createServiceModal = document.getElementById('create-service-modal');
        const closeCreateServiceModalBtn = document.getElementById('close-create-service-modal');
        const newServiceForm = document.getElementById('new-service-form');
        const cancelNewServiceBtn = document.getElementById('cancel-new-service');

        // Edit Service Modal Elements
        const editServiceModal = document.getElementById('edit-service-modal');
        const closeEditServiceModalBtn = document.getElementById('close-edit-service-modal');
        const editServiceForm = document.getElementById('edit-service-form');
        const cancelEditServiceBtn = document.getElementById('cancel-edit-service');

        // Service Detail Modal Elements
        const serviceDetailModal = document.getElementById('service-detail-modal');
        const closeServiceDetailModalBtn = document.getElementById('close-service-detail-modal');
        const closeServiceDetailBtn = document.getElementById('close-service-detail-btn');


        const fetchServices = async (searchQuery = '', sortDir = '', sortBy = '') => { // Removed limit parameter
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    // window.location.href = '/login.html'; // Redirect to login
                    return;
                }

                let url = '/api/services';
                const params = new URLSearchParams();

                if (searchQuery) {
                    params.append('name', searchQuery); // Assuming API supports searching by name
                }
                if (sortDir) {
                    params.append('sort_direction', sortDir);
                }
                if (sortBy) {
                    params.append('sort_by', sortBy);
                }
                // if (limit) { // Removed limit parameter
                //     params.append('limit', limit);
                // }

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

                const services = await response.json();
                serviceTableBody.innerHTML = ''; // Clear existing rows

                if (services.length === 0) {
                    serviceTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không tìm thấy dịch vụ nào.</td></tr>`;
                    return;
                }

                services.forEach(service => {
                    const row = serviceTableBody.insertRow();
                    row.className = 'border-b border-gray-200 hover:bg-gray-50';
                    row.dataset.serviceId = service.id; // Store service ID on the row

                    const statusText = service.is_active ? 'Đang hoạt động' : 'Không hoạt động';
                    const statusColor = service.is_active ? 'text-green-500' : 'text-red-500';
                    const statusIcon = service.is_active ? `
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ${statusColor} inline-block mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    ` : `
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ${statusColor} inline-block mr-1" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    `;

                    row.innerHTML = `
                        <td class="py-4 px-6">${service.id}</td>
                        <td class="py-4 px-6 font-medium">${service.name}</td>
                        <td class="py-4 px-6">${service.description || 'N/A'}</td>
                        <td class="py-4 px-6">${service.price}</td>
                        <td class="py-4 px-6">
                            ${statusIcon}
                            ${statusText}
                        </td>
                        <td class="py-4 px-6 text-center space-x-3">
                            <button class="btn-action btn-edit action-link-edit" data-id="${service.id}">Sửa</button>
                            <button class="btn-action btn-delete action-link-delete" data-id="${service.id}">Xóa</button>
                            <button class="btn-action btn-doctors action-link-detail" data-id="${service.id}">Chi tiết</button>
                        </td>
                    `;
                });

            } catch (error) {
                console.error('Error fetching services:', error);
                serviceTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu dịch vụ. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;
            }
        };

        // Initial fetch
        fetchServices();

        // Event Listeners
        searchButton.addEventListener('click', () => {
            fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value);
        });

        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value);
            }
        });

        refreshButton.addEventListener('click', () => {
            searchInput.value = '';
            sortDirectionSelect.value = '';
            sortValueSelect.value = '';
            // resultCountSelect.value = ''; // Removed
            fetchServices();
        });

        sortDirectionSelect.addEventListener('change', () => {
            fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value);
        });

        sortValueSelect.addEventListener('change', () => {
            fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value);
        });

        // resultCountSelect.addEventListener('change', () => { // Removed
        //     fetchServices(searchInput.value, sortDirectionSelect.value, sortValueSelect.value, resultCountSelect.value);
        // });

        // Create New Service
        createNewButton.addEventListener('click', () => {
            createServiceModal.classList.remove('hidden');
        });

        closeCreateServiceModalBtn.addEventListener('click', () => {
            createServiceModal.classList.add('hidden');
            newServiceForm.reset();
        });

        cancelNewServiceBtn.addEventListener('click', () => {
            createServiceModal.classList.add('hidden');
            newServiceForm.reset();
        });

        newServiceForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const name = document.getElementById('new-service-name').value;
            const description = document.getElementById('new-service-description').value;
            const price = parseFloat(document.getElementById('new-service-price').value);
            const isActive = document.getElementById('new-service-is-active').checked;

            if (!name || isNaN(price)) {
                alert('Tên dịch vụ và Giá là bắt buộc!');
                return;
            }

            const newService = {
                id: 0, // Temporary workaround: Backend API is unexpectedly requiring an ID for creation
                name: name,
                description: description,
                price: price,
                is_active: isActive
            };

            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch('/api/services', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newService)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);
                }

                alert('Dịch vụ đã được tạo thành công!');
                createServiceModal.classList.add('hidden');
                newServiceForm.reset();
                fetchServices(); // Refresh the list
            } catch (error) {
                console.error('Lỗi khi tạo dịch vụ:', error);
                alert('Lỗi khi tạo dịch vụ. Vui lòng kiểm tra console.');
            }
        });


        // Delegated event listeners for action buttons (Edit, Delete, Detail)
        serviceTableBody.addEventListener('click', async (event) => {
            const target = event.target;
            if (target.classList.contains('btn-action')) { // Changed from 'action-link' to 'btn-action' in HTML, but keeping 'action-link' for JS logic
                event.preventDefault();
                const serviceId = target.dataset.id;

                if (target.classList.contains('action-link-edit')) {
                    console.log(`Edit service with ID: ${serviceId}`);
                    try {
                        const token = sessionStorage.getItem('accessToken');
                        const response = await fetch(`/api/services/${serviceId}`, {
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

                        const service = await response.json();
                        document.getElementById('edit-service-id').value = service.id;
                        document.getElementById('edit-service-name').value = service.name;
                        document.getElementById('edit-service-description').value = service.description || '';
                        document.getElementById('edit-service-price').value = service.price;
                        document.getElementById('edit-service-is-active').checked = service.is_active;

                        editServiceModal.classList.remove('hidden');
                    } catch (error) {
                        console.error('Lỗi khi tải thông tin dịch vụ để chỉnh sửa:', error);
                        alert('Lỗi khi tải thông tin dịch vụ. Vui lòng kiểm tra console.');
                    }
                } else if (target.classList.contains('action-link-delete')) {
                    console.log(`Delete service with ID: ${serviceId}`);
                    if (confirm('Bạn có chắc chắn muốn xóa dịch vụ này không?')) {
                        try {
                            const token = sessionStorage.getItem('accessToken');
                            const response = await fetch(`/api/services/${serviceId}`, {
                                method: 'DELETE',
                                headers: {
                                    'Authorization': `Bearer ${token}`
                                }
                            });

                            if (!response.ok) {
                                const errorData = await response.json();
                                throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);
                            }

                            alert('Dịch vụ đã được xóa thành công!');
                            fetchServices(); // Refresh the list
                        } catch (error) {
                            console.error('Lỗi khi xóa dịch vụ:', error);
                            alert('Lỗi khi xóa dịch vụ. Vui lòng kiểm tra console.');
                        }
                    }
                } else if (target.classList.contains('action-link-detail')) {
                    console.log(`View details for service with ID: ${serviceId}`);
                    try {
                        const token = sessionStorage.getItem('accessToken');
                        const response = await fetch(`/api/services/${serviceId}`, {
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

                        const service = await response.json();
                        document.getElementById('detail-service-id').textContent = service.id;
                        document.getElementById('detail-service-name').textContent = service.name;
                        document.getElementById('detail-service-description').textContent = service.description || 'N/A';
                        document.getElementById('detail-service-price').textContent = service.price;
                        document.getElementById('detail-service-is-active').textContent = service.is_active ? 'Đang hoạt động' : 'Không hoạt động';

                        serviceDetailModal.classList.remove('hidden');
                    } catch (error) {
                        console.error('Lỗi khi tải chi tiết dịch vụ:', error);
                        alert('Lỗi khi tải chi tiết dịch vụ. Vui lòng kiểm tra console.');
                    }
                }
            }
        });

        // Close Edit Service Modal
        closeEditServiceModalBtn.addEventListener('click', () => {
            editServiceModal.classList.add('hidden');
            editServiceForm.reset();
        });

        cancelEditServiceBtn.addEventListener('click', () => {
            editServiceModal.classList.add('hidden');
            editServiceForm.reset();
        });

        editServiceForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const serviceId = document.getElementById('edit-service-id').value;
            const name = document.getElementById('edit-service-name').value;
            const description = document.getElementById('edit-service-description').value;
            const price = parseFloat(document.getElementById('edit-service-price').value);
            const isActive = document.getElementById('edit-service-is-active').checked;

            if (!name || isNaN(price)) {
                alert('Tên dịch vụ và Giá là bắt buộc!');
                return;
            }

            const updatedService = {
                id: serviceId,
                name: name,
                description: description,
                price: price,
                is_active: isActive
            };

            try {
                const token = sessionStorage.getItem('accessToken');
                const response = await fetch(`/api/services/${serviceId}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedService)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);
                }

                alert('Dịch vụ đã được cập nhật thành công!');
                editServiceModal.classList.add('hidden');
                editServiceForm.reset();
                fetchServices(); // Refresh the list
            } catch (error) {
                console.error('Lỗi khi cập nhật dịch vụ:', error);
                alert('Lỗi khi cập nhật dịch vụ. Vui lòng kiểm tra console.');
            }
        });

        // Close Service Detail Modal
        closeServiceDetailModalBtn.addEventListener('click', () => {
            serviceDetailModal.classList.add('hidden');
        });

        closeServiceDetailBtn.addEventListener('click', () => {
            serviceDetailModal.classList.add('hidden');
        });
    }
}
initDichVuPage();