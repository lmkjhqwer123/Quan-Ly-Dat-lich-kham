// thu_tu_kham.js

if (typeof window.initThuTuKhamPage === 'undefined') {
    window.initThuTuKhamPage = function() {
        console.log('thu_tu_kham.js: initThuTuKhamPage function started');
        const tableBody = document.getElementById('queue-table-body');

        if (!tableBody) {
            console.error('thu_tu_kham.js: Critical error - queue-table-body element not found!');
            return;
        }

        const getTodayDate = () => {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        const fetchConfirmedAppointments = async () => {
            console.log('thu_tu_kham.js: fetchConfirmedAppointments function called.');
            try {
                const token = sessionStorage.getItem('accessToken');
                const userRole = sessionStorage.getItem('userRole');
                console.log('thu_tu_kham.js: User role:', userRole);

                if (!token) {
                    console.error('thu_tu_kham.js: No access token found. Aborting fetch.');
                    // Redirect to login if needed
                    // window.location.href = '/GUI/login.html';
                    return;
                }
                console.log('thu_tu_kham.js: Access token found.');

                const today = getTodayDate();
                const url = `/api/admin/appointments?status=confirmed&appointment_date=${today}`;
                console.log('thu_tu_kham.js: Fetching URL:', url);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                console.log('thu_tu_kham.js: Raw response from server:', response);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('thu_tu_kham.js: Server response text:', errorText);
                    throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
                }

                const appointments = await response.json();
                console.log('thu_tu_kham.js: Parsed appointments data:', appointments);
                renderTable(appointments);

            } catch (error) {
                console.error('thu_tu_kham.js: Error fetching appointments:', error);
                tableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu: ${error.message}. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;
            }
        };

        const renderTable = (appointments) => {
            console.log('thu_tu_kham.js: renderTable function called.');
            tableBody.innerHTML = '';

            if (appointments.length === 0) {
                console.log('thu_tu_kham.js: No appointments found for today.');
                tableBody.innerHTML = `<tr><td colspan="6" class="py-4 px-6 text-center text-gray-500">Không có lịch hẹn nào được xác nhận cho ngày hôm nay.</td></tr>`;
                return;
            }

            console.log(`thu_tu_kham.js: Rendering ${appointments.length} appointments.`);
            appointments.sort((a, b) => new Date(a.AppointmentDatetime) - new Date(b.AppointmentDatetime)); // Sắp xếp theo giờ hẹn

            appointments.forEach((appointment, index) => {
                const row = tableBody.insertRow();
                row.className = 'border-b border-gray-200 hover:bg-gray-50';

                const appointmentTime = new Date(appointment.AppointmentDatetime).toLocaleTimeString('vi-VN', {
                    hour: '2-digit',
                    minute: '2-digit'
                });

                row.innerHTML = `
                    <td class="py-4 px-6 font-medium">${index + 1}</td>
                    <td class="py-4 px-6">
                        <span class="font-medium">${appointment.PatientName || 'N/A'}</span>
                    </td>
                    <td class="py-4 px-6">${appointmentTime}</td>
                    <td class="py-4 px-6">${appointment.SpecialtyName || 'N/A'}</td>
                    <td class="py-4 px-6">${appointment.DoctorName || 'N/A'}</td>
                    <td class="py-4 px-6">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            ${appointment.Status}
                        </span>
                    </td>
                `;
            });
        };

        // Initial fetch
        fetchConfirmedAppointments();
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initThuTuKhamPage);
} else {
    window.initThuTuKhamPage();
}