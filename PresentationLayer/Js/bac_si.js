
    

    if (typeof window.initBacSiPage === 'undefined') {

        window.initBacSiPage = function() {

            const doctorTableBody = document.getElementById('doctor-table-body');

    

            const fetchDoctors = async () => {

                try {

                    const token = sessionStorage.getItem('accessToken');

                    if (!token) {

                        console.error('No access token found. User not authenticated.');

                        // window.location.href = '/login.html'; // Redirect to login

                        return;

                    }

    

                    const response = await fetch('/api/doctors/', {

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

    

                        row.innerHTML = `

                            <td class="py-4 px-6">

                                <img class="h-10 w-10 rounded-full object-cover" src="https://placehold.co/40x40/EBF8FF/3182CE?text=${doctor.FullName.charAt(0)}" alt="Avatar">

                            </td>

                            <td class="py-4 px-6 font-medium">${doctor.SpecialtyName}</td>

                            <td class="py-4 px-6 font-medium">${doctor.FullName}</td>

                            <td class="py-4 px-6">${doctor.Phone}</td>

                            <td class="py-4 px-6">${doctor.Qualifications}</td>

                            <td class="py-4 px-6">

                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">

                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />

                                </svg>

                            </td>

                            <td class="py-4 px-6 text-center space-x-3">

                                <a href="#" class="action-link action-link-edit">Sửa</a>

                                <a href="#" class="action-link action-link-delete">Xóa</a>

                                <a href="#" class="action-link action-link-detail">Chi tiết</a>

                            </td>

                        `;

                    });

    

                } catch (error) {

                    console.error('Error fetching doctors:', error);

                    doctorTableBody.innerHTML = `<tr><td colspan="7" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu bác sĩ. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;

                }

            };

    

            fetchDoctors();

        }

    }

    initBacSiPage();

    
