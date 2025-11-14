console.log('doctor_lich_lam_viec.js loaded and executing.'); // Added for debugging

if (typeof window.initDoctorLichLamViecPage === 'undefined') {
    window.initDoctorLichLamViecPage = function() {
        console.log('initDoctorLichLamViecPage function called.'); // Added for debugging
        const calendarGrid = document.getElementById('calendar-grid');
        const monthYearDisplay = document.getElementById('month-year');
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');

        let currentDate = new Date();
        let appointments = [];

        async function fetchAppointments() {
            console.log('fetchAppointments function called.'); // Added for debugging
            const token = sessionStorage.getItem('accessToken');
            console.log('Token:', token); // DEBUG
            if (!token) {
                console.error('No access token found. Redirecting to login.');
                window.location.href = '/login.html'; // Redirect to login page
                return;
            }

            try {
                const response = await fetch('/api/doctor/schedule', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                console.log('Fetch response:', response); // DEBUG

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                appointments = await response.json();
                console.log('Appointments data received:', appointments); // DEBUG: Log the raw data
                if (appointments.length === 0) {
                    console.log('No appointments found for this doctor.');
                }
                renderCalendar(currentDate);
            } catch (error) {
                console.error('Error fetching appointments:', error);
            }
        }

        function renderCalendar(date) {
            calendarGrid.innerHTML = ''; // Xóa lịch cũ
            const year = date.getFullYear();
            const month = date.getMonth();

            monthYearDisplay.textContent = `Tháng ${month + 1}, ${year}`;
            monthYearDisplay.style.textAlign = 'center';

            const firstDayOfMonth = new Date(year, month, 1);
            const lastDayOfMonth = new Date(year, month + 1, 0);
            const daysInMonth = lastDayOfMonth.getDate();
            const startDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sunday, 1 = Monday, ...

            // Lấy ngày cuối của tháng trước
            const lastDayOfPrevMonth = new Date(year, month, 0).getDate();

            // Điền các ngày của tháng trước
            for (let i = 0; i < startDayOfWeek; i++) {
                const day = lastDayOfPrevMonth - startDayOfWeek + i + 1;
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day calendar-day-other-month';
                dayCell.innerHTML = `<div class="day-number">${day}</div>`;
                calendarGrid.appendChild(dayCell);
            }

            // Điền các ngày của tháng hiện tại
            for (let day = 1; day <= daysInMonth; day++) {
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day relative';
                dayCell.innerHTML = `<div class="day-number">${day}</div>`;

                const currentDay = new Date(year, month, day);
                const dayAppointments = appointments.filter(app => {
                                        const appDate = new Date(app.start_time);
                                        console.log(`Filtering: app.start_time=${app.start_time}, appDate=${appDate}, currentDay=${currentDay}`); // DEBUG
                                        return appDate.getFullYear() === year &&
                                               appDate.getMonth() === month &&
                                               appDate.getDate() === day;
                                    });
                                    dayAppointments.sort((a, b) => {
                                        if (a.status === 'pending' && b.status !== 'pending') return -1;
                                        if (a.status !== 'pending' && b.status === 'pending') return 1;
                                        return 0;
                                    });

                                    const appointmentsToDisplay = dayAppointments.slice(0, 2);
                                    const hasMoreAppointments = dayAppointments.length > 2;

                                    if (dayAppointments.length > 0) {
                                        console.log(`Day ${day}: Found ${dayAppointments.length} appointments.`); // DEBUG
                                        // Add a blue dot for days with appointments
                                        const dotEl = document.createElement('div');
                                        dotEl.className = 'event-dot absolute bottom-1 right-1 w-2 h-2 bg-blue-500 rounded-full';
                                        dayCell.appendChild(dotEl);

                                        appointmentsToDisplay.forEach(app => {
                                            const eventEl = document.createElement('div');
                                            let statusClass = '';
                                            // Determine the color class based on appointment status
                                            switch (app.status) {
                                                // Pending appointments are yellow
                                                case 'pending':
                                                    statusClass = 'bg-yellow-100 text-yellow-800';
                                                    break;
                                                // Confirmed appointments are green
                                                case 'confirmed':
                                                    statusClass = 'bg-green-100 text-green-800';
                                                    break;
                                                case 'canceled':
                                                    statusClass = 'bg-red-100 text-red-800';
                                                    // Canceled appointments are red
                                                // Completed appointments are blue
                                                case 'completed':
                                                    statusClass = 'bg-blue-100 text-blue-800';
                                                    break;
                                                // Default styling for unknown statuses
                                                default:
                                                    statusClass = 'bg-gray-100 text-gray-800'; // Default styling
                                            }
                                            eventEl.className = `event-item text-xs px-1 py-0.5 rounded mt-1 ${statusClass}`;
                                            const startTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                                            eventEl.textContent = `${startTime} - ${app.patient_name}`;
                                            eventEl.title = `Bệnh nhân: ${app.patient_name}\nTriệu chứng: ${app.symptoms}\nTrạng thái: ${app.status}`;
                                            dayCell.appendChild(eventEl);
                                        });

                                        if (hasMoreAppointments) {
                                            const moreEl = document.createElement('div');
                                            moreEl.className = 'text-xs text-gray-500 mt-1';
                                            moreEl.textContent = '...';
                                            dayCell.appendChild(moreEl);
                                        }
                                    } else {
                                        const emptyText = document.createElement('div');
                                        emptyText.className = 'text-gray-400 text-sm mt-2';
                                        emptyText.textContent = 'Trống';
                                        dayCell.appendChild(emptyText);
                                    }

                dayCell.addEventListener('click', () => {
                    if (dayAppointments.length > 0) {
                        showAppointmentModal(currentDay, dayAppointments);
                    }
                });

                calendarGrid.appendChild(dayCell);
            }

            // Điền các ngày của tháng sau
            const totalCells = startDayOfWeek + daysInMonth;
            const remainingCells = (7 - (totalCells % 7)) % 7;
            for (let i = 1; i <= remainingCells; i++) {
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day calendar-day-other-month';
                dayCell.innerHTML = `<div class="day-number">${i}</div>`;
                calendarGrid.appendChild(dayCell);
            }
        }

        prevMonthBtn.addEventListener('click', async () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            await fetchAppointments(); // Re-fetch appointments for the new month
        });

        nextMonthBtn.addEventListener('click', async () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            await fetchAppointments(); // Re-fetch appointments for the new month
        });

        // Modal elements
        const appointmentModal = document.getElementById('appointment-modal');
        const closeModalBtn = document.getElementById('close-modal');
        const modalDateSpan = document.getElementById('modal-date');
        const modalAppointmentsList = document.getElementById('modal-appointments-list');

        function showAppointmentModal(date, dayAppointments) {
            modalDateSpan.textContent = date.toLocaleDateString('vi-VN');
            modalAppointmentsList.innerHTML = ''; // Clear previous appointments

            if (dayAppointments.length === 0) {
                modalAppointmentsList.innerHTML = '<p class="text-gray-600">Không có lịch hẹn nào.</p>';
            } else {
                dayAppointments.forEach(app => {
                    const appTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                    const appItem = document.createElement('div');
                    let statusClass = '';
                    // Determine the color class based on appointment status for the modal
                    switch (app.status) {
                        // Pending appointments are yellow
                        case 'pending':
                            statusClass = 'bg-yellow-100 border-yellow-400 text-yellow-800';
                            break;
                        // Confirmed appointments are green
                        case 'confirmed':
                            statusClass = 'bg-green-100 border-green-400 text-green-800';
                            break;
                        // Canceled appointments are gray
                        case 'canceled':
                            statusClass = 'bg-red-100 border-red-400 text-red-800';
                            break;
                        // Completed appointments are blue
                        case 'completed':
                            statusClass = 'bg-blue-100 border-blue-400 text-blue-800';
                            break;
                        // Default styling for unknown statuses
                        default:
                            statusClass = 'bg-gray-100 border-gray-200 text-gray-800'; // Default styling
                    }
                    appItem.className = `mb-2 p-3 border rounded-md ${statusClass}`;
                    appItem.innerHTML = `
                        <p class="font-semibold text-gray-800">Thời gian: ${appTime}</p>
                        <p class="text-gray-700">Bệnh nhân: ${app.patient_name}</p>
                        <p class="text-gray-700">Triệu chứng: ${app.symptoms || 'Không có'}</p>
                    `;
                    modalAppointmentsList.appendChild(appItem);
                });
            }
            appointmentModal.classList.remove('hidden');
        }

        closeModalBtn.addEventListener('click', () => {
            appointmentModal.classList.add('hidden');
        });

        // Close modal when clicking outside of it
        window.addEventListener('click', (event) => {
            if (event.target === appointmentModal) {
                appointmentModal.classList.add('hidden');
            }
        });

        fetchAppointments();
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorLichLamViecPage);
} else {
    window.initDoctorLichLamViecPage();
}
