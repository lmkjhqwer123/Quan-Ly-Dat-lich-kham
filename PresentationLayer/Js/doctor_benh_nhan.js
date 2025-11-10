// doctor_benh_nhan.js

if (typeof window.initDoctorBenhNhanPage === 'undefined') {
    window.initDoctorBenhNhanPage = function() {
        const patientTableBody = document.getElementById('patient-table-body');
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const refreshPatientsBtn = document.getElementById('refresh-patients-btn');
        const sortDirectionDropdown = document.getElementById('sort-direction');
        const sortValueDropdown = document.getElementById('sort-value');

        const patientDetailModal = document.getElementById('patient-detail-modal');
        const closePatientDetailModalBtn = document.getElementById('close-patient-detail-modal');
        const closePatientDetailBtn = document.getElementById('close-patient-detail-btn');

        const fetchPatients = async (searchQuery = '', sortDirection = '', sortValue = '') => {
            console.log('Attempting to call fetchPatients() with query:', searchQuery);
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('No access token found. User not authenticated.');
                    // Optionally redirect to login page
                    // window.location.href = '/login.html';
                    return;
                }

                let url = '/api/doctor/patients/me'; // Doctor-specific endpoint
                const params = new URLSearchParams();

                if (searchQuery) {
                    params.append('query', searchQuery);
                }
                if (sortDirection) {
                    params.append('sort_direction', sortDirection);
                }
                if (sortValue) {
                    params.append('sort_by', sortValue);
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

                const patients = await response.json();
                console.log('Fetched patients:', patients);

                // Clear existing table rows before adding new ones
                patientTableBody.innerHTML = '';

                if (patients.length === 0) {
                    patientTableBody.innerHTML = `<tr><td colspan="7" class="py-3 px-6 text-center text-gray-500">Không tìm thấy bệnh nhân nào.</td></tr>`;
                    return;
                }

                patients.forEach(patient => {
                    const row = patientTableBody.insertRow();
                    row.className = 'border-b border-gray-200 hover:bg-gray-50';

                    row.innerHTML = `
                        <td class="py-3 px-6">${patient.PatientId}</td>
                        <td class="py-3 px-6">
                            <img src="https://via.placeholder.com/40" alt="Avatar" class="h-10 w-10 rounded-full object-cover">
                        </td>
                        <td class="py-3 px-6 font-medium">${patient.FullName}</td>
                        <td class="py-3 px-6">${patient.Email}</td>
                        <td class="py-3 px-6">${patient.Phone}</td>
                        <td class="py-3 px-6">${patient.address || 'N/A'}</td>
                        <td class="py-3 px-6">
                            <button class="btn-action btn-detail view-patient-detail-btn" data-patient-id="${patient.PatientId}">Chi tiết</button>
                        </td>
                    `;
                });

            } catch (error) {
                console.error('Error fetching patients:', error);
                patientTableBody.innerHTML = `<tr><td colspan="7" class="py-3 px-6 text-center text-red-500">Lỗi khi tải dữ liệu bệnh nhân.</td></tr>`;
            }
        };

        // Initial load of patients
        fetchPatients(searchInput.value.trim(), sortDirectionDropdown.value, sortValueDropdown.value);

        // Event listener for search button
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                const query = searchInput.value.trim();
                fetchPatients(query, sortDirectionDropdown.value, sortValueDropdown.value);
            });
        }

        // Event listener for search input (Enter key)
        if (searchInput) {
            searchInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    const query = searchInput.value.trim();
                    fetchPatients(query, sortDirectionDropdown.value, sortValueDropdown.value);
                }
            });
        }

        // Event listener for refresh button
        if (refreshPatientsBtn) {
            refreshPatientsBtn.addEventListener('click', () => {
                searchInput.value = ''; // Clear search input
                sortDirectionDropdown.value = ''; // Clear sort direction
                sortValueDropdown.value = ''; // Clear sort value
                fetchPatients(); // Fetch all patients with default sorting
            });
        }

        // Event listeners for sort dropdowns
        if (sortDirectionDropdown) {
            sortDirectionDropdown.addEventListener('change', () => {
                fetchPatients(searchInput.value.trim(), sortDirectionDropdown.value, sortValueDropdown.value);
            });
        }

        if (sortValueDropdown) {
            sortValueDropdown.addEventListener('change', () => {
                fetchPatients(searchInput.value.trim(), sortDirectionDropdown.value, sortValueDropdown.value);
            });
        }

        // Event listener for view patient detail buttons
        patientTableBody.addEventListener('click', async (event) => {
            if (event.target.classList.contains('view-patient-detail-btn')) {
                const patientId = event.target.dataset.patientId;
                if (patientId) {
                    try {
                        const token = sessionStorage.getItem('accessToken');
                        if (!token) {
                            console.error('No access token found. User not authenticated.');
                            return;
                        }
                        const response = await fetch(`/api/doctor/patients/${patientId}`, { // Doctor-specific endpoint
                            method: 'GET',
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Accept': 'application/json'
                            }
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }

                        const patient = await response.json();
                        
                        document.getElementById('detail-patient-id').textContent = patient.PatientId;
                        document.getElementById('detail-full-name').textContent = patient.FullName;
                        document.getElementById('detail-email').textContent = patient.Email;
                        document.getElementById('detail-phone').textContent = patient.Phone;
                        document.getElementById('detail-birth-date').textContent = patient.birth_date || 'N/A';
                        document.getElementById('detail-address').textContent = patient.address || 'N/A';

                        patientDetailModal.classList.remove('hidden');

                    } catch (error) {
                        console.error('Error fetching patient details:', error);
                        alert('Error fetching patient details.');
                    }
                }
            }
        });

        // Close patient detail modal
        if (closePatientDetailModalBtn) {
            closePatientDetailModalBtn.addEventListener('click', () => {
                patientDetailModal.classList.add('hidden');
            });
        }

        if (closePatientDetailBtn) {
            closePatientDetailBtn.addEventListener('click', () => {
                patientDetailModal.classList.add('hidden');
            });
        }
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorBenhNhanPage);
} else {
    window.initDoctorBenhNhanPage();
}
