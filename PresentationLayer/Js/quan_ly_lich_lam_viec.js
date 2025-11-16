document.addEventListener('DOMContentLoaded', () => {
    const leaveRequestsTableBody = document.querySelector('#leave-requests-table-body');
    const searchInput = document.getElementById('search');
    const statusFilter = document.getElementById('status');
    const dateRangeFilter = document.getElementById('date-range');

    let allLeaveRequests = [];

    const fetchLeaveRequests = async () => {
        try {
            let url = '/api/admin/leave-requests';
            const params = new URLSearchParams();

            if (statusFilter.value !== 'all') {
                params.append('status', statusFilter.value);
            }
            if (dateRangeFilter.value) {
                params.append('leave_date', dateRangeFilter.value);
            }

            if (params.toString()) {
                url += `?${params.toString()}`;
            }

            const accessToken = sessionStorage.getItem('accessToken');
            console.log('Access Token:', accessToken);
            console.log('Fetching leave requests from URL:', url);

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            console.log('Response Status:', response.status);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response Error Text:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            const data = await response.json();
            console.log('Fetched Leave Requests Data:', data);
            allLeaveRequests = data;
            renderLeaveRequests(allLeaveRequests);
        } catch (error) {
            console.error('Error fetching leave requests:', error);
            if (leaveRequestsTableBody) {
                leaveRequestsTableBody.innerHTML = '<tr><td colspan="5" class="py-4 px-6 text-center text-red-500">Không thể tải dữ liệu yêu cầu nghỉ phép.</td></tr>';
            }
        }
    };

    const renderLeaveRequests = (leaveRequests) => {
        if (!leaveRequestsTableBody) return;

        leaveRequestsTableBody.innerHTML = ''; // Clear existing rows

        if (leaveRequests.length === 0) {
            leaveRequestsTableBody.innerHTML = '<tr><td colspan="5" class="py-4 px-6 text-center text-gray-500">Không có yêu cầu nghỉ phép nào.</td></tr>';
            return;
        }

        leaveRequests.forEach(request => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-200 hover:bg-gray-50';

            const startDate = new Date(request.start_datetime);
            const endDate = new Date(request.end_datetime);
            const formattedDate = startDate.toLocaleDateString('vi-VN') + 
                                  (startDate.toDateString() !== endDate.toDateString() ? ' - ' + endDate.toLocaleDateString('vi-VN') : '');
            
            row.innerHTML = `
                <td class="py-4 px-6">
                    <span class="font-medium">${request.doctor_name}</span>
                </td>
                <td class="py-4 px-6">${request.specialty_name}</td>
                <td class="py-4 px-6">${formattedDate}</td>
                <td class="py-4 px-6 text-sm">${request.reason}</td>
                <td class="py-4 px-6 text-center">
                    <button class="btn-action btn-view" onclick="openLeaveDetailModal(${request.leave_id})">Xem chi tiết</button>
                </td>
            `;
            leaveRequestsTableBody.appendChild(row);
        });
    };

    const filterAndSearchLeaveRequests = () => {
        let filteredRequests = [...allLeaveRequests];

        // Filter by status
        const selectedStatus = statusFilter.value;
        if (selectedStatus !== 'all') {
            filteredRequests = filteredRequests.filter(request => request.status === selectedStatus);
        }

        // Filter by date (exact match for now, can be extended to range)
        const selectedDate = dateRangeFilter.value;
        if (selectedDate) {
            filteredRequests = filteredRequests.filter(request => {
                const requestStartDate = new Date(request.start_datetime).toISOString().split('T')[0];
                return requestStartDate === selectedDate;
            });
        }

        // Search by doctor name or specialty
        const searchTerm = searchInput.value.toLowerCase();
        if (searchTerm) {
            filteredRequests = filteredRequests.filter(request =>
                request.doctor_name.toLowerCase().includes(searchTerm) ||
                request.specialty_name.toLowerCase().includes(searchTerm)
            );
        }

        renderLeaveRequests(filteredRequests);
    };

    // Event Listeners for filters and search
    searchInput.addEventListener('input', filterAndSearchLeaveRequests);
    statusFilter.addEventListener('change', filterAndSearchLeaveRequests);
    dateRangeFilter.addEventListener('change', filterAndSearchLeaveRequests);

    // Initial fetch
    fetchLeaveRequests();

    // Global function to open modal (for buttons generated dynamically)
    window.openLeaveDetailModal = (leaveId) => {
        const request = allLeaveRequests.find(req => req.leave_id === leaveId);
        if (!request) {
            console.error('Leave request not found:', leaveId);
            return;
        }
        
        // Populate modal with request data
        document.getElementById('modal-leave-id').textContent = request.leave_id;
        document.getElementById('modal-doctor-name').textContent = request.doctor_name;
        document.getElementById('modal-specialty-name').textContent = request.specialty_name;
        document.getElementById('modal-leave-type').textContent = request.leave_type;
        document.getElementById('modal-start-datetime').textContent = new Date(request.start_datetime).toLocaleString('vi-VN');
        document.getElementById('modal-end-datetime').textContent = new Date(request.end_datetime).toLocaleString('vi-VN');
        document.getElementById('modal-reason').textContent = request.reason;
        document.getElementById('modal-status').textContent = request.status;

        // Show the modal
        document.getElementById('leave-detail-modal').classList.add('active');
    };

    window.closeModal = (modalId) => {
        document.getElementById(modalId).classList.remove('active');
    };

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('leave-detail-modal');
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
});
