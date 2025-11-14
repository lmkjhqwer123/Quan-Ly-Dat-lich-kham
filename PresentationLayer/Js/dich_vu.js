if (typeof window.initDichVuPage === 'undefined') {
    window.initDichVuPage = function() {
        const userRole = sessionStorage.getItem('userRole');

        const serviceTableBody = document.getElementById('service-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshButton = document.getElementById('refresh-button');
        const createNewButton = document.getElementById('create-new-button');
        const sortDirectionSelect = document.getElementById('sort-direction');
        const sortValueSelect = document.getElementById('sort-value');

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

        if (userRole !== 'Admin') {
            if (createNewButton) createNewButton.style.display = 'none';
        }

        const fetchServices = async (searchQuery = '', sortDir = '', sortBy = '') => {
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    return;
                }

                let url = '/api/services';
                const params = new URLSearchParams();
                if (searchQuery) params.append('query', searchQuery);
                if (sortDir) params.append('sort_direction', sortDir);
                if (sortBy) params.append('sort_by', sortBy);

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
                    console.error(`HTTP error! status: ${response.status}, errorData:`, errorData);
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const services = await response.json();
                serviceTableBody.innerHTML = '';

                if (services.length === 0) {
                    serviceTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không tìm thấy dịch vụ nào.</td></tr>`;
                    return;
                }

                services.forEach(service => {
                    const row = serviceTableBody.insertRow();
                    row.className = 'border-b border-gray-200 hover:bg-gray-50';
                    row.dataset.serviceId = service.id;

                    const statusText = service.is_active ? 'Đang hoạt động' : 'Không hoạt động';
                    const statusColor = service.is_active ? 'text-green-500' : 'text-red-500';
                    const statusIcon = service.is_active ? `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ${statusColor} inline-block mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>` : `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ${statusColor} inline-block mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>`;

                    let actionButtonsHTML = '';
                    if (userRole === 'Admin') {
                        actionButtonsHTML += `
                            <button class="btn-action btn-edit action-link-edit" data-id="${service.id}">Sửa</button>
                            <button class="btn-action btn-delete action-link-delete" data-id="${service.id}">Xóa</button>
                        `;
                    }
                    actionButtonsHTML += `<button class="btn-action btn-doctors action-link-detail" data-id="${service.id}">Chi tiết</button>`;

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
                            ${actionButtonsHTML}
                        </td>
                    `;
                });

            } catch (error) {
                console.error('Error fetching services:', error);
                serviceTableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu dịch vụ.</td></tr>`;
            }
        };

        fetchServices();

        searchButton.addEventListener('click', () => fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value));
        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value);
        });
        refreshButton.addEventListener('click', () => {
            searchInput.value = '';
            sortDirectionSelect.value = '';
            sortValueSelect.value = '';
            fetchServices();
        });
        sortDirectionSelect.addEventListener('change', () => fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value));
        sortValueSelect.addEventListener('change', () => fetchServices(searchInput.value.trim(), sortDirectionSelect.value, sortValueSelect.value));

        if (userRole === 'Admin') {
            createNewButton.addEventListener('click', () => createServiceModal.classList.remove('hidden'));
            closeCreateServiceModalBtn.addEventListener('click', () => createServiceModal.classList.add('hidden'));
            cancelNewServiceBtn.addEventListener('click', () => createServiceModal.classList.add('hidden'));

            newServiceForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const newService = {
                    id: 0,
                    name: document.getElementById('new-service-name').value,
                    description: document.getElementById('new-service-description').value,
                    price: parseFloat(document.getElementById('new-service-price').value),
                    is_active: document.getElementById('new-service-is-active').checked
                };
                try {
                    const token = sessionStorage.getItem('accessToken');
                    const response = await fetch('/api/services', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify(newService)
                    });
                    if (!response.ok) throw new Error(await response.text());
                    alert('Dịch vụ đã được tạo thành công!');
                    createServiceModal.classList.add('hidden');
                    newServiceForm.reset();
                    fetchServices();
                } catch (error) {
                    console.error('Lỗi khi tạo dịch vụ:', error);
                    alert('Lỗi khi tạo dịch vụ.');
                }
            });

            closeEditServiceModalBtn.addEventListener('click', () => editServiceModal.classList.add('hidden'));
            cancelEditServiceBtn.addEventListener('click', () => editServiceModal.classList.add('hidden'));

            editServiceForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const serviceId = document.getElementById('edit-service-id').value;
                const updatedService = {
                    id: serviceId,
                    name: document.getElementById('edit-service-name').value,
                    description: document.getElementById('edit-service-description').value,
                    price: parseFloat(document.getElementById('edit-service-price').value),
                    is_active: document.getElementById('edit-service-is-active').checked
                };
                try {
                    const token = sessionStorage.getItem('accessToken');
                    const response = await fetch(`/api/services/${serviceId}`, {
                        method: 'PUT',
                        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                        body: JSON.stringify(updatedService)
                    });
                    if (!response.ok) throw new Error(await response.text());
                    alert('Dịch vụ đã được cập nhật thành công!');
                    editServiceModal.classList.add('hidden');
                    editServiceForm.reset();
                    fetchServices();
                } catch (error) {
                    console.error('Lỗi khi cập nhật dịch vụ:', error);
                    alert('Lỗi khi cập nhật dịch vụ.');
                }
            });
        }

        serviceTableBody.addEventListener('click', async (event) => {
            const target = event.target;
            const serviceId = target.dataset.id;

            if (target.classList.contains('action-link-edit') && userRole === 'Admin') {
                try {
                    const token = sessionStorage.getItem('accessToken');
                    const response = await fetch(`/api/services/${serviceId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                    if (!response.ok) throw new Error(await response.text());
                    const service = await response.json();
                    document.getElementById('edit-service-id').value = service.id;
                    document.getElementById('edit-service-name').value = service.name;
                    document.getElementById('edit-service-description').value = service.description || '';
                    document.getElementById('edit-service-price').value = service.price;
                    document.getElementById('edit-service-is-active').checked = service.is_active;
                    editServiceModal.classList.remove('hidden');
                } catch (error) {
                    console.error('Lỗi khi tải thông tin dịch vụ:', error);
                    alert('Lỗi khi tải thông tin dịch vụ.');
                }
            } else if (target.classList.contains('action-link-delete') && userRole === 'Admin') {
                if (confirm('Bạn có chắc chắn muốn xóa dịch vụ này không?')) {
                    try {
                        const token = sessionStorage.getItem('accessToken');
                        const response = await fetch(`/api/services/${serviceId}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
                        if (!response.ok) throw new Error(await response.text());
                        alert('Dịch vụ đã được xóa thành công!');
                        fetchServices();
                    } catch (error) {
                        console.error('Lỗi khi xóa dịch vụ:', error);
                        alert('Lỗi khi xóa dịch vụ.');
                    }
                }
            } else if (target.classList.contains('action-link-detail')) {
                try {
                    const token = sessionStorage.getItem('accessToken');
                    const response = await fetch(`/api/services/${serviceId}`, { headers: { 'Authorization': `Bearer ${token}` } });
                    if (!response.ok) {
                        if(response.status === 403) {
                             alert("Bạn không có quyền xem chi tiết dịch vụ.");
                             return;
                        }
                        throw new Error(await response.text());
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
                    alert('Lỗi khi tải chi tiết dịch vụ.');
                }
            }
        });

        closeServiceDetailModalBtn.addEventListener('click', () => serviceDetailModal.classList.add('hidden'));
        closeServiceDetailBtn.addEventListener('click', () => serviceDetailModal.classList.add('hidden'));
    }
}
initDichVuPage();