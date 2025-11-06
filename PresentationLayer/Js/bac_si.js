
    

    if (typeof window.initBacSiPage === 'undefined') {

        window.initBacSiPage = function() {

            const doctorTableBody = document.getElementById('doctor-table-body');

            const searchInput = document.getElementById('search-input');

            const searchButton = document.getElementById('search-button');

            const refreshButton = document.getElementById('refresh-button');

            const createNewButton = document.getElementById('create-new-button');

            const sortDirectionSelect = document.getElementById('sort-direction');

            const sortValueSelect = document.getElementById('sort-value');
            const resultCountSelect = document.getElementById('result-count');
            const sortStatusSelect = document.getElementById('sort-status');
            const sortSpecialitySelect = document.getElementById('sort-speciality');
            const sortRoomSelect = document.getElementById('sort-room');



            // Create Doctor Modal Elements

            const createDoctorModal = document.getElementById('create-doctor-modal');

            const closeCreateDoctorModalBtn = document.getElementById('close-create-doctor-modal');

            const newDoctorForm = document.getElementById('new-doctor-form');

            const cancelNewDoctorBtn = document.getElementById('cancel-new-doctor');



            // Edit Doctor Modal Elements

            const editDoctorModal = document.getElementById('edit-doctor-modal');

            const closeEditDoctorModalBtn = document.getElementById('close-edit-doctor-modal');

            const editDoctorForm = document.getElementById('edit-doctor-form');

            const cancelEditDoctorBtn = document.getElementById('cancel-edit-doctor');



            // Doctor Detail Modal Elements

            const doctorDetailModal = document.getElementById('doctor-detail-modal');

            const closeDoctorDetailModalBtn = document.getElementById('close-doctor-detail-modal');

            const closeDoctorDetailBtn = document.getElementById('close-doctor-detail-btn');



            const fetchDoctors = async (searchQuery = '', sortDir = '', sortBy = '', status = '', specialty = '', room = '', limit = '') => {

                try {

                    const token = sessionStorage.getItem('accessToken');

                    if (!token) {

                        console.error('No access token found. User not authenticated.');

                        // window.location.href = '/login.html'; // Redirect to login

                        return;

                    }



                    let url = '/api/doctors/';

                    const params = new URLSearchParams();



                    if (searchQuery) {

                        params.append('query', searchQuery); // Assuming API supports searching by query

                    }

                    if (sortDir) {

                        params.append('sort_direction', sortDir);

                    }

                    if (sortBy) {

                        params.append('sort_by', sortBy);

                    }



                    if (status) {
                        params.append('is_active', status === 'active' ? 'true' : 'false'); // Assuming API expects 'is_active' boolean
                    }
                    if (specialty) {
                        params.append('specialty_name', specialty); // Assuming API expects 'specialty_name'
                    }
                    if (room) {
                        params.append('room_name', room); // Assuming API expects 'room_name'
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

                        const errorData = await response.json();

                        console.error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}, errorData:`, errorData);

                        throw new Error(`HTTP error! status: ${response.status}`);

                    }



                    const doctors = await response.json();

                    doctorTableBody.innerHTML = ''; // Clear existing rows



                    if (doctors.length === 0) {

                        doctorTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-gray-500">Không tìm thấy bác sĩ nào.</td></tr>`;

                        return;

                    }



                    doctors.forEach(doctor => {

                        const row = doctorTableBody.insertRow();

                        row.className = 'border-b border-gray-200 hover:bg-gray-50';

                        row.dataset.doctorId = doctor.DoctorId; // Store doctor ID on the row



                        row.innerHTML = `

                            <td class="py-4 px-6">

                                <img class="h-10 w-10 rounded-full object-cover" src="https://placehold.co/40x40/EBF8FF/3182CE?text=${doctor.FullName.charAt(0)}" alt="Avatar">

                            </td>

                            <td class="py-4 px-6 font-medium">${doctor.SpecialtyName || 'N/A'}</td>

                            <td class="py-4 px-6 font-medium">${doctor.FullName}</td>

                            <td class="py-4 px-6">${doctor.Phone}</td>

                            <td class="py-4 px-6">${doctor.Qualifications}</td>

                            <td class="py-4 px-6">

                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">

                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />

                                </svg>

                            </td>

                            <td class="py-4 px-6 text-center space-x-3">

                                <button class="btn-action btn-edit action-link-edit" data-id="${doctor.DoctorId}">Sửa</button>

                                <button class="btn-action btn-delete action-link-delete" data-id="${doctor.DoctorId}">Xóa</button>

                                <button class="btn-action btn-detail action-link-detail" data-id="${doctor.DoctorId}">Chi tiết</button>

                            </td>

                        `;

                    });



                } catch (error) {

                    console.error('Error fetching doctors:', error);

                    doctorTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu bác sĩ. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;

                }

            };



            // Initial fetch

            fetchDoctors();



            // Event Listeners

            searchButton.addEventListener('click', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            searchInput.addEventListener('keyup', (event) => {

                if (event.key === 'Enter') {

                    fetchDoctors(

                        searchInput.value.trim(),

                        sortDirectionSelect.value,

                        sortValueSelect.value,

                        sortStatusSelect.value,

                        sortSpecialitySelect.value,

                        sortRoomSelect.value,

                        resultCountSelect.value

                    );

                }

            });



            refreshButton.addEventListener('click', () => {

                searchInput.value = '';

                sortDirectionSelect.value = '';

                sortValueSelect.value = '';

                resultCountSelect.value = '';

                sortStatusSelect.value = '';

                sortSpecialitySelect.value = '';

                sortRoomSelect.value = '';

                fetchDoctors();

            });



            sortDirectionSelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            sortValueSelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            // New event listeners for additional filters

            resultCountSelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            sortStatusSelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            sortSpecialitySelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            sortRoomSelect.addEventListener('change', () => {

                fetchDoctors(

                    searchInput.value.trim(),

                    sortDirectionSelect.value,

                    sortValueSelect.value,

                    sortStatusSelect.value,

                    sortSpecialitySelect.value,

                    sortRoomSelect.value,

                    resultCountSelect.value

                );

            });



            // Create New Doctor

            createNewButton.addEventListener('click', () => {

                createDoctorModal.classList.remove('hidden');

            });



            closeCreateDoctorModalBtn.addEventListener('click', () => {

                createDoctorModal.classList.add('hidden');

                newDoctorForm.reset();

            });



            cancelNewDoctorBtn.addEventListener('click', () => {

                createDoctorModal.classList.add('hidden');

                newDoctorForm.reset();

            });



            newDoctorForm.addEventListener('submit', async (event) => {

                event.preventDefault();



                const fullName = document.getElementById('new-doctor-full-name').value;

                const email = document.getElementById('new-doctor-email').value;

                const phone = document.getElementById('new-doctor-phone').value;

                const specialtyId = parseInt(document.getElementById('new-doctor-specialty-id').value);

                const qualifications = document.getElementById('new-doctor-qualifications').value;

                const password = document.getElementById('new-doctor-password').value;



                if (!fullName || !email || !phone || isNaN(specialtyId) || !qualifications || !password) {

                    alert('Vui lòng điền đầy đủ thông tin bắt buộc.');

                    return;

                }



                const newDoctor = {

                    FullName: fullName,

                    Email: email,

                    Phone: phone,

                    SpecialtyId: specialtyId,

                    Qualifications: qualifications,

                    Password: password

                };



                try {

                    const token = sessionStorage.getItem('accessToken');

                    const response = await fetch('/api/doctors/', {

                        method: 'POST',

                        headers: {

                            'Authorization': `Bearer ${token}`,

                            'Content-Type': 'application/json'

                        },

                        body: JSON.stringify(newDoctor)

                    });



                    if (!response.ok) {

                        const errorData = await response.json();

                        throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);

                    }



                    alert('Bác sĩ đã được tạo thành công!');

                    createDoctorModal.classList.add('hidden');

                    newDoctorForm.reset();

                    fetchDoctors(); // Refresh the list

                } catch (error) {

                    console.error('Lỗi khi tạo bác sĩ:', error);

                    alert('Lỗi khi tạo bác sĩ. Vui lòng kiểm tra console.');

                }

            });



            // Delegated event listeners for action buttons (Edit, Delete, Detail)

            doctorTableBody.addEventListener('click', async (event) => {

                const target = event.target;

                if (target.classList.contains('btn-action')) {

                    event.preventDefault();

                    const doctorId = target.dataset.id;



                    if (target.classList.contains('action-link-edit')) {

                        console.log(`Edit doctor with ID: ${doctorId}`);

                        try {

                            const token = sessionStorage.getItem('accessToken');

                            const response = await fetch(`/api/doctors/${doctorId}`, {

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



                            const doctor = await response.json();

                            document.getElementById('edit-doctor-id').value = doctor.DoctorId;

                            document.getElementById('edit-doctor-full-name').value = doctor.FullName;

                            document.getElementById('edit-doctor-email').value = doctor.Email;

                            document.getElementById('edit-doctor-phone').value = doctor.Phone;

                            document.getElementById('edit-doctor-specialty-id').value = doctor.SpecialtyId;

                            document.getElementById('edit-doctor-qualifications').value = doctor.Qualifications;



                            editDoctorModal.classList.remove('hidden');

                        } catch (error) {

                            console.error('Lỗi khi tải thông tin bác sĩ để chỉnh sửa:', error);

                            alert('Lỗi khi tải thông tin bác sĩ. Vui lòng kiểm tra console.');

                        }

                    } else if (target.classList.contains('action-link-delete')) {

                        console.log(`Delete doctor with ID: ${doctorId}`);

                        if (confirm('Bạn có chắc chắn muốn xóa bác sĩ này không?')) {

                            try {

                                const token = sessionStorage.getItem('accessToken');

                                const response = await fetch(`/api/doctors/${doctorId}`, {

                                    method: 'DELETE',

                                    headers: {

                                        'Authorization': `Bearer ${token}`

                                    }

                                });



                                if (!response.ok) {

                                    const errorData = await response.json();

                                    throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);

                                }



                                alert('Bác sĩ đã được xóa thành công!');

                                fetchDoctors(); // Refresh the list

                            } catch (error) {

                                console.error('Lỗi khi xóa bác sĩ:', error);

                                alert('Lỗi khi xóa bác sĩ. Vui lòng kiểm tra console.');

                            }

                        }

                    } else if (target.classList.contains('action-link-detail')) {

                        console.log(`View details for doctor with ID: ${doctorId}`);

                        try {

                            const token = sessionStorage.getItem('accessToken');

                            const response = await fetch(`/api/doctors/${doctorId}`, {

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



                            const doctor = await response.json();

                            document.getElementById('detail-doctor-id').textContent = doctor.DoctorId;

                            document.getElementById('detail-doctor-full-name').textContent = doctor.FullName;

                            document.getElementById('detail-doctor-email').textContent = doctor.Email;

                            document.getElementById('detail-doctor-phone').textContent = doctor.Phone;

                            document.getElementById('detail-doctor-specialty-name').textContent = doctor.SpecialtyName || 'N/A';

                            document.getElementById('detail-doctor-qualifications').textContent = doctor.Qualifications;



                            doctorDetailModal.classList.remove('hidden');

                        } catch (error) {

                            console.error('Lỗi khi tải chi tiết bác sĩ:', error);

                            alert('Lỗi khi tải chi tiết bác sĩ. Vui lòng kiểm tra console.');

                        }

                    }

                }

            });



            // Close Edit Doctor Modal

            closeEditDoctorModalBtn.addEventListener('click', () => {

                editDoctorModal.classList.add('hidden');

                editDoctorForm.reset();

            });



            cancelEditDoctorBtn.addEventListener('click', () => {

                editDoctorModal.classList.add('hidden');

                editDoctorForm.reset();

            });



            editDoctorForm.addEventListener('submit', async (event) => {

                event.preventDefault();



                const doctorId = document.getElementById('edit-doctor-id').value;

                const fullName = document.getElementById('edit-doctor-full-name').value;

                const email = document.getElementById('edit-doctor-email').value;

                const phone = document.getElementById('edit-doctor-phone').value;

                const specialtyId = parseInt(document.getElementById('edit-doctor-specialty-id').value);

                const qualifications = document.getElementById('edit-doctor-qualifications').value;



                if (!fullName || !email || !phone || isNaN(specialtyId) || !qualifications) {

                    alert('Vui lòng điền đầy đủ thông tin bắt buộc.');

                    return;

                }



                const updatedDoctor = {

                    FullName: fullName,

                    Email: email,

                    Phone: phone,

                    SpecialtyId: specialtyId,

                    Qualifications: qualifications

                };



                try {

                    const token = sessionStorage.getItem('accessToken');

                    const response = await fetch(`/api/doctors/${doctorId}`, {

                        method: 'PUT',

                        headers: {

                            'Authorization': `Bearer ${token}`,

                            'Content-Type': 'application/json'

                        },

                        body: JSON.stringify(updatedDoctor)

                    });



                    if (!response.ok) {

                        const errorData = await response.json();

                        throw new Error(`HTTP error! status: ${response.status}, error: ${JSON.stringify(errorData)}`);

                    }



                    alert('Thông tin bác sĩ đã được cập nhật thành công!');

                    editDoctorModal.classList.add('hidden');

                    editDoctorForm.reset();

                    fetchDoctors(); // Refresh the list

                } catch (error) {

                    console.error('Lỗi khi cập nhật thông tin bác sĩ:', error);

                    alert('Lỗi khi cập nhật thông tin bác sĩ. Vui lòng kiểm tra console.');

                }

            });



            // Close Doctor Detail Modal

            closeDoctorDetailModalBtn.addEventListener('click', () => {

                doctorDetailModal.classList.add('hidden');

            });



            closeDoctorDetailBtn.addEventListener('click', () => {

                doctorDetailModal.classList.add('hidden');

            });

        }

    }

    initBacSiPage();

    
