// doctor_thu_tu_kham.js

if (typeof window.initDoctorThuTuKhamPage === 'undefined') {
    window.initDoctorThuTuKhamPage = function() {
        console.log('doctor_thu_tu_kham.js: initDoctorThuTuKhamPage function started');
        const tableBody = document.getElementById('queue-table-body');

        if (!tableBody) {
            console.error('doctor_thu_tu_kham.js: Critical error - queue-table-body element not found!');
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
            console.log('doctor_thu_tu_kham.js: fetchConfirmedAppointments function called.');
            try {
                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    console.error('doctor_thu_tu_kham.js: No access token found. Aborting fetch.');
                    // Redirect to login if needed
                    // window.location.href = '/GUI/login.html';
                    return;
                }
                console.log('doctor_thu_tu_kham.js: Access token found.');

                const today = getTodayDate();
                // Doctor-specific endpoint for their queue
                const url = `/api/doctor/examination-queue?appointment_statuses=confirmed,pending&appointment_date=${today}`;
                console.log('doctor_thu_tu_kham.js: Fetching URL:', url);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Accept': 'application/json'
                    }
                });

                console.log('doctor_thu_tu_kham.js: Raw response from server:', response);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('doctor_thu_tu_kham.js: Server response text:', errorText);
                    throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
                }

                const appointments = await response.json();
                console.log('doctor_thu_tu_kham.js: Parsed appointments data:', appointments);
                renderTable(appointments);

            } catch (error) {
                console.error('doctor_thu_tu_kham.js: Error fetching appointments:', error);
                tableBody.innerHTML = `<tr><td colspan="5" class="py-4 px-6 text-center text-red-500">Lỗi khi tải dữ liệu: ${error.message}. Vui lòng kiểm tra console để biết chi tiết.</td></tr>`;
            }
        };

        const renderTable = (appointments) => {
            console.log('doctor_thu_tu_kham.js: renderTable function called.');
            tableBody.innerHTML = '';

            if (appointments.length === 0) {
                console.log('doctor_thu_tu_kham.js: No appointments found for today.');
                tableBody.innerHTML = `<tr><td colspan="5" class="py-4 px-6 text-center text-gray-500">Không có lịch hẹn nào được xác nhận cho ngày hôm nay.</td></tr>`;
                return;
            }

            console.log(`doctor_thu_tu_kham.js: Rendering ${appointments.length} appointments.`);
            appointments.sort((a, b) => new Date(a.AppointmentDatetime) - new Date(b.AppointmentDatetime)); // Sort by appointment time

            appointments.forEach((appointment, index) => {
                console.log('Appointment Status:', appointment.Status);
                const row = tableBody.insertRow();
                let rowClass = 'border-b border-gray-200 hover:bg-gray-50';
                let statusClass = 'bg-green-100 text-green-800';
                if (appointment.Status.toLowerCase() === 'pending') {
                    rowClass += ' bg-yellow-50'; // Light yellow background for pending
                    statusClass = 'bg-yellow-100 text-yellow-800';
                }
                row.className = rowClass;

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
                    <td class="py-4 px-6">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
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
    document.addEventListener('DOMContentLoaded', window.initDoctorThuTuKhamPage);
} else {
    window.initDoctorThuTuKhamPage();
}
