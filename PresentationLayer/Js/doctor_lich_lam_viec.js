console.log('doctor_lich_lam_viec.js loaded and executing.');

if (typeof window.initDoctorLichLamViecPage === 'undefined') {
    window.initDoctorLichLamViecPage = function() {
        console.log('initDoctorLichLamViecPage function called.');
        const calendarGrid = document.getElementById('calendar-grid');
        const monthYearDisplay = document.getElementById('month-year');
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');

        let mainCalendarDate = new Date();
        let appointments = [];

        async function fetchAppointments() {
            console.log('fetchAppointments function called.');
            const token = sessionStorage.getItem('accessToken');
            if (!token) {
                console.error('No access token found. Redirecting to login.');
                window.location.href = '/login.html';
                return;
            }

            try {
                const response = await fetch('/api/doctor/schedule', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                appointments = await response.json();
                renderMainCalendar(mainCalendarDate);
            } catch (error) {
                console.error('Error fetching appointments:', error);
            }
        }

        function renderMainCalendar(date) {
            calendarGrid.innerHTML = '';
            const year = date.getFullYear();
            const month = date.getMonth();
            monthYearDisplay.textContent = `Tháng ${month + 1}, ${year}`;
            monthYearDisplay.style.textAlign = 'center';

            const firstDayOfMonth = new Date(year, month, 1);
            const lastDayOfMonth = new Date(year, month + 1, 0);
            const daysInMonth = lastDayOfMonth.getDate();
            const startDayOfWeek = firstDayOfMonth.getDay();

            const lastDayOfPrevMonth = new Date(year, month, 0).getDate();
            for (let i = 0; i < startDayOfWeek; i++) {
                const day = lastDayOfPrevMonth - startDayOfWeek + i + 1;
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day calendar-day-other-month';
                dayCell.innerHTML = `<div class="day-number">${day}</div>`;
                calendarGrid.appendChild(dayCell);
            }

            for (let day = 1; day <= daysInMonth; day++) {
                const dayCell = document.createElement('div');
                dayCell.className = 'calendar-day relative';
                dayCell.innerHTML = `<div class="day-number">${day}</div>`;
                const currentDay = new Date(year, month, day);
                const dayAppointments = appointments.filter(app => {
                    const appDate = new Date(app.start_time);
                    return appDate.getFullYear() === year && appDate.getMonth() === month && appDate.getDate() === day;
                });

                if (dayAppointments.length > 0) {
                    const dotEl = document.createElement('div');
                    dotEl.className = 'event-dot absolute bottom-1 right-1 w-2 h-2 bg-blue-500 rounded-full';
                    dayCell.appendChild(dotEl);
                } else {
                    const emptyText = document.createElement('div');
                    emptyText.className = 'text-gray-400 text-sm mt-2';
                    emptyText.textContent = 'Trống';
                    dayCell.appendChild(emptyText);
                }

                dayCell.addEventListener('click', () => {
                    if (dayAppointments.length > 0) showAppointmentModal(currentDay, dayAppointments);
                });
                calendarGrid.appendChild(dayCell);
            }

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
            mainCalendarDate.setMonth(mainCalendarDate.getMonth() - 1);
            await fetchAppointments();
        });

        nextMonthBtn.addEventListener('click', async () => {
            mainCalendarDate.setMonth(mainCalendarDate.getMonth() + 1);
            await fetchAppointments();
        });

        // Main Appointment Modal Logic (existing)
        const appointmentModal = document.getElementById('appointment-modal');
        const closeModalBtn = document.getElementById('close-modal');
        const modalDateSpan = document.getElementById('modal-date');
        const modalAppointmentsList = document.getElementById('modal-appointments-list');

        function showAppointmentModal(date, dayAppointments) {
            modalDateSpan.textContent = date.toLocaleDateString('vi-VN');
            modalAppointmentsList.innerHTML = '';
            if (dayAppointments.length === 0) {
                modalAppointmentsList.innerHTML = '<p class="text-gray-600">Không có lịch hẹn nào.</p>';
            } else {
                dayAppointments.forEach(app => {
                    const appTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                    const appItem = document.createElement('div');
                    appItem.className = `mb-2 p-3 border rounded-md`;
                    appItem.innerHTML = `
                        <p class="font-semibold text-gray-800">Thời gian: ${appTime}</p>
                        <p class="text-gray-700">Bệnh nhân: ${app.patient_name}</p>
                    `;
                    modalAppointmentsList.appendChild(appItem);
                });
            }
            appointmentModal.classList.remove('hidden');
        }
        closeModalBtn.addEventListener('click', () => appointmentModal.classList.add('hidden'));
        window.addEventListener('click', (event) => {
            if (event.target === appointmentModal) appointmentModal.classList.add('hidden');
        });

        // --- NEW LEAVE REGISTRATION MODAL LOGIC ---

        const leaveModal = document.getElementById('leaveModal');
        const openLeaveModalBtn = document.getElementById('register-leave-btn');
        const closeLeaveModalBtn = document.getElementById('closeLeaveModal');
        const cancelLeaveSubmissionBtn = document.getElementById('cancel-leave-submission');
        const submitLeaveRequestBtn = document.getElementById('submit-leave-request');

        const miniCalMonthYear = document.getElementById('mini-cal-month-year');
        const miniCalBody = document.getElementById('mini-calendar-body');
        const miniCalPrevBtn = document.getElementById('mini-cal-prev-month');
        const miniCalNextBtn = document.getElementById('mini-cal-next-month');
        const selectedDaysList = document.getElementById('selected-days-list');

        let miniCalDate = new Date();
        let selectedDates = new Set();

        function renderMiniCalendar() {
            miniCalBody.innerHTML = '';
            const year = miniCalDate.getFullYear();
            const month = miniCalDate.getMonth();
            miniCalMonthYear.textContent = `Tháng ${month + 1}, ${year}`;

            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const daysInMonth = lastDay.getDate();
            // Adjust to make Monday the first day (0 = Mon, 6 = Sun)
            const startDayOfWeek = (firstDay.getDay() + 6) % 7;

            // Add empty cells for days before the 1st of the month
            for (let i = 0; i < startDayOfWeek; i++) {
                miniCalBody.insertAdjacentHTML('beforeend', '<div></div>');
            }

            // Add day cells
            for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(year, month, day);
                const dateString = date.toISOString().split('T')[0]; // YYYY-MM-DD format
                const dayCell = document.createElement('div');
                dayCell.textContent = day;
                dayCell.className = 'p-1.5 rounded-full cursor-pointer hover:bg-gray-200';
                dayCell.dataset.date = dateString;

                if (selectedDates.has(dateString)) {
                    dayCell.classList.add('bg-blue-500', 'text-white');
                }

                dayCell.addEventListener('click', () => toggleDateSelection(dateString));
                miniCalBody.appendChild(dayCell);
            }
        }

        function toggleDateSelection(dateString) {
            const cell = miniCalBody.querySelector(`[data-date="${dateString}"]`);
            if (selectedDates.has(dateString)) {
                selectedDates.delete(dateString);
                cell.classList.remove('bg-blue-500', 'text-white');
            } else {
                selectedDates.add(dateString);
                cell.classList.add('bg-blue-500', 'text-white');
            }
            updateSelectedDaysList();
        }

        function updateSelectedDaysList() {
            selectedDaysList.innerHTML = '';
            if (selectedDates.size === 0) {
                selectedDaysList.innerHTML = '<p class="text-gray-500">Vui lòng chọn một ngày từ lịch bên trái...</p>';
                return;
            }

            const sortedDates = Array.from(selectedDates).sort();
            sortedDates.forEach(dateString => {
                const date = new Date(dateString);
                const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
                const dayElement = document.createElement('div');
                dayElement.className = 'flex items-center justify-between bg-gray-50 p-2 rounded-md';
                dayElement.dataset.date = dateString;
                dayElement.innerHTML = `
                    <span class="font-medium text-gray-800">${formattedDate}</span>
                    <div class="flex items-center gap-2">
                        <input type="time" class="start-time border-gray-300 rounded-md shadow-sm text-sm" style="width: 100px;">
                        <span>-</span>
                        <input type="time" class="end-time border-gray-300 rounded-md shadow-sm text-sm" style="width: 100px;">
                    </div>
                `;
                selectedDaysList.appendChild(dayElement);
            });
        }

        miniCalPrevBtn.addEventListener('click', () => {
            miniCalDate.setMonth(miniCalDate.getMonth() - 1);
            renderMiniCalendar();
        });

        miniCalNextBtn.addEventListener('click', () => {
            miniCalDate.setMonth(miniCalDate.getMonth() + 1);
            renderMiniCalendar();
        });

        openLeaveModalBtn.addEventListener('click', () => {
            miniCalDate = new Date(); // Reset to current month
            selectedDates.clear();
            renderMiniCalendar();
            updateSelectedDaysList();
            leaveModal.classList.remove('hidden');
            leaveModal.classList.add('flex');
        });

        const closeAndResetModal = () => {
            leaveModal.classList.add('hidden');
            leaveModal.classList.remove('flex');
        };

        closeLeaveModalBtn.addEventListener('click', closeAndResetModal);
        cancelLeaveSubmissionBtn.addEventListener('click', closeAndResetModal);

        submitLeaveRequestBtn.addEventListener('click', async () => {
            const token = sessionStorage.getItem('accessToken');
            if (!token) {
                alert('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
                return;
            }

            const reason = document.getElementById('reason').value;
            const description = document.getElementById('leave-description').value; // Get description value
            const schedules = [];

            let hasInvalidTime = false;
            selectedDaysList.querySelectorAll('.flex.items-center.justify-between').forEach(dayElement => {
                const date = dayElement.dataset.date;
                const startTime = dayElement.querySelector('.start-time').value;
                const endTime = dayElement.querySelector('.end-time').value;

                if (startTime && endTime && startTime >= endTime) {
                    hasInvalidTime = true;
                }

                schedules.push({
                    date: date,
                    start_time: startTime || null,
                    end_time: endTime || null
                });
            });

            if (hasInvalidTime) {
                alert('Thời gian kết thúc phải sau thời gian bắt đầu.');
                return;
            }

            if (schedules.length === 0) {
                alert('Vui lòng chọn ít nhất một ngày.');
                return;
            }

            try {
                const response = await fetch('/api/doctor/register-schedule', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ reason, description, schedules }) // Add description to payload
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Có lỗi xảy ra');
                }

                alert('Đăng ký lịch thành công!');
                closeAndResetModal();
                await fetchAppointments(); // Refresh the main calendar

            } catch (error) {
                console.error('Error submitting leave request:', error);
                alert(`Lỗi: ${error.message}`);
            }
        });

        // Initial fetch for the main calendar
        fetchAppointments();
    };
}

// Initialize the page logic
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initDoctorLichLamViecPage);
} else {
    window.initDoctorLichLamViecPage();
}