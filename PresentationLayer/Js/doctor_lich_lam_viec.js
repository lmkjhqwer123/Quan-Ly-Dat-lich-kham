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
                    // Sort appointments: pending first, then by start_time
                    dayAppointments.sort((a, b) => {
                        if (a.status === 'pending' && b.status !== 'pending') return -1;
                        if (a.status !== 'pending' && b.status === 'pending') return 1;
                        return new Date(a.start_time) - new Date(b.start_time);
                    });

                    const appointmentsContainer = document.createElement('div');
                    appointmentsContainer.className = 'appointments-container mt-1 text-xs space-y-0.5';
                    dayCell.appendChild(appointmentsContainer);

                    const statusColors = {
                        'pending': 'bg-yellow-500',
                        'confirmed': 'bg-blue-500',
                        'completed': 'bg-green-500',
                        'canceled': 'bg-red-500'
                    };

                    const displayLimit = 2;
                    const appointmentsToDisplay = dayAppointments.slice(0, displayLimit);

                    appointmentsToDisplay.forEach(app => {
                        const appTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                        const appInfo = document.createElement('div');
                        const statusColorClass = statusColors[app.status] || 'bg-gray-400'; // Default color if status is unknown
                        appInfo.className = `flex items-center space-x-1 p-1 rounded-md ${statusColorClass} text-white text-xs font-medium mb-0.5 transform transition-transform duration-200 hover:scale-105`;
                        appInfo.innerHTML = `
                            <span class="w-2 h-2 rounded-full bg-white"></span>
                            <span>${appTime} - ${app.patient_name}</span>
                        `;
                        appointmentsContainer.appendChild(appInfo);
                    });

                    if (dayAppointments.length > displayLimit) {
                        const moreIndicator = document.createElement('div');
                        moreIndicator.className = 'text-center text-gray-500 font-bold text-xs mt-1';
                        moreIndicator.textContent = '...';
                        appointmentsContainer.appendChild(moreIndicator);
                    }
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
                const statusColors = {
                    'pending': 'bg-yellow-500',
                    'confirmed': 'bg-blue-500',
                    'completed': 'bg-green-500',
                    'canceled': 'bg-red-500'
                };
                const statusBgColors = {
                    'pending': 'bg-yellow-100',
                    'confirmed': 'bg-blue-100',
                    'completed': 'bg-green-100',
                    'canceled': 'bg-red-100'
                };

                dayAppointments.forEach(app => {
                    const appTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                    const statusColorClass = statusColors[app.status] || 'bg-gray-400'; // Default color if status is unknown
                    const statusBgColorClass = statusBgColors[app.status] || 'bg-gray-100'; // Lighter background color
                    const appItem = document.createElement('div');
                    appItem.className = `mb-2 py-2 px-3 border rounded-md flex items-center space-x-2 ${statusBgColorClass} cursor-pointer transform transition-transform duration-200 hover:scale-105`;
                    appItem.innerHTML = `
                        <span class="w-3 h-3 rounded-full ${statusColorClass}"></span>
                        <div>
                            <p class="font-semibold text-gray-800">Thời gian: ${appTime}</p>
                            <p class="text-gray-700">Bệnh nhân: ${app.patient_name}</p>
                            <p class="text-gray-600 text-sm">Trạng thái: <span class="font-medium">${app.status}</span></p>
                        </div>
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
        // Use a Map to store the state of each selected date
        let selectedDates = new Map();

        function renderMiniCalendar() {
            miniCalBody.innerHTML = '';
            const year = miniCalDate.getFullYear();
            const month = miniCalDate.getMonth();
            miniCalMonthYear.textContent = `Tháng ${month + 1}, ${year}`;

            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const daysInMonth = lastDay.getDate();
            const startDayOfWeek = (firstDay.getDay() + 6) % 7;

            for (let i = 0; i < startDayOfWeek; i++) {
                miniCalBody.insertAdjacentHTML('beforeend', '<div></div>');
            }

            for (let day = 1; day <= daysInMonth; day++) {
                const date = new Date(year, month, day);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                const isPastDay = date < today;

                const dateString = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
                const dayCell = document.createElement('div');
                dayCell.textContent = day;
                dayCell.className = 'p-1.5 rounded-full';

                if (isPastDay) {
                    dayCell.classList.add('text-gray-400', 'cursor-not-allowed');
                } else {
                    dayCell.classList.add('cursor-pointer', 'hover:bg-gray-200');
                    dayCell.dataset.date = dateString;
                    dayCell.addEventListener('click', () => toggleDateSelection(dateString));
                }

                if (selectedDates.has(dateString) && !isPastDay) {
                    dayCell.classList.add('bg-blue-500', 'text-white');
                }
                miniCalBody.appendChild(dayCell);
            }
        }

        function toggleDateSelection(dateString) {
            const cell = miniCalBody.querySelector(`[data-date="${dateString}"]`);
            if (selectedDates.has(dateString)) {
                selectedDates.delete(dateString);
                if (cell) cell.classList.remove('bg-blue-500', 'text-white');
            } else {
                // Add new date with a default state
                selectedDates.set(dateString, {
                    leaveType: 'all-day',
                    sessions: []
                });
                if (cell) cell.classList.add('bg-blue-500', 'text-white');
            }
            updateSelectedDaysList();
        }

        function updateSelectedDaysList() {
            selectedDaysList.innerHTML = '';
            if (selectedDates.size === 0) {
                selectedDaysList.innerHTML = '<p class="text-gray-500">Vui lòng chọn một ngày từ lịch bên trái...</p>';
                return;
            }

            const sortedDates = Array.from(selectedDates.entries()).sort((a, b) => a[0].localeCompare(b[0]));

            sortedDates.forEach(([dateString, dateState]) => {
                const [year, month, day] = dateString.split('-').map(Number);
                const date = new Date(year, month - 1, day);
                const formattedDate = `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
                const dayElement = document.createElement('div');
                dayElement.className = 'bg-gray-50 p-3 rounded-lg border border-gray-200';
                dayElement.dataset.date = dateString;

                const isAllDay = dateState.leaveType === 'all-day';
                const isBySession = dateState.leaveType === 'by-session';

                dayElement.innerHTML = `
                    <div class="text-center">
                        <span class="font-semibold text-gray-800">${formattedDate}</span>
                    </div>
                    <hr class="border-gray-200 my-2">
                    <div class="flex justify-center items-center gap-6 mb-3">
                        <label class="flex items-center cursor-pointer">
                            <input type="radio" name="leave-type-${dateString}" value="all-day" class="form-radio h-4 w-4 text-blue-600" ${isAllDay ? 'checked' : ''}>
                            <span class="ml-2 text-sm text-gray-700">Nghỉ Cả Ngày</span>
                        </label>
                        <label class="flex items-center cursor-pointer">
                            <input type="radio" name="leave-type-${dateString}" value="by-session" class="form-radio h-4 w-4 text-blue-600" ${isBySession ? 'checked' : ''}>
                            <span class="ml-2 text-sm text-gray-700">Nghỉ Theo Ca</span>
                        </label>
                    </div>
                    <div class="session-checkboxes grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2 ${isBySession ? '' : 'hidden'} pl-4">
                        <label class="flex items-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
                            <input type="checkbox" value="07:00-09:00" class="form-checkbox h-4 w-4 text-blue-600 rounded" ${dateState.sessions.includes('07:00-09:00') ? 'checked' : ''}>
                            <span class="ml-2 text-sm font-medium text-gray-800">7h-9h</span>
                        </label>
                        <label class="flex items-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
                            <input type="checkbox" value="09:00-11:00" class="form-checkbox h-4 w-4 text-blue-600 rounded" ${dateState.sessions.includes('09:00-11:00') ? 'checked' : ''}>
                            <span class="ml-2 text-sm font-medium text-gray-800">9h-11h</span>
                        </label>
                        <label class="flex items-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
                            <input type="checkbox" value="13:00-15:00" class="form-checkbox h-4 w-4 text-blue-600 rounded" ${dateState.sessions.includes('13:00-15:00') ? 'checked' : ''}>
                            <span class="ml-2 text-sm font-medium text-gray-800">13h-15h</span>
                        </label>
                        <label class="flex items-center p-2 rounded-md bg-gray-100 hover:bg-gray-200 cursor-pointer">
                            <input type="checkbox" value="15:00-17:00" class="form-checkbox h-4 w-4 text-blue-600 rounded" ${dateState.sessions.includes('15:00-17:00') ? 'checked' : ''}>
                            <span class="ml-2 text-sm font-medium text-gray-800">15h-17h</span>
                        </label>
                    </div>
                `;
                selectedDaysList.appendChild(dayElement);

                // Add event listeners to update the state in the map
                const radios = dayElement.querySelectorAll(`input[name="leave-type-${dateString}"]`);
                const checkboxesContainer = dayElement.querySelector('.session-checkboxes');
                const checkboxes = dayElement.querySelectorAll('.session-checkboxes input[type="checkbox"]');

                radios.forEach(radio => {
                    radio.addEventListener('change', (e) => {
                        const currentState = selectedDates.get(dateString);
                        currentState.leaveType = e.target.value;
                        if (e.target.value === 'by-session') {
                            checkboxesContainer.classList.remove('hidden');
                        } else {
                            checkboxesContainer.classList.add('hidden');
                            currentState.sessions = []; // Clear sessions when switching to all-day
                            checkboxes.forEach(cb => cb.checked = false); // Uncheck UI
                        }
                    });
                });

                checkboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', (e) => {
                        const currentState = selectedDates.get(dateString);
                        const sessionValue = e.target.value;
                        if (e.target.checked) {
                            if (!currentState.sessions.includes(sessionValue)) {
                                currentState.sessions.push(sessionValue);
                            }
                        } else {
                            const index = currentState.sessions.indexOf(sessionValue);
                            if (index > -1) {
                                currentState.sessions.splice(index, 1);
                            }
                        }
                    });
                });
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

        // Helper function to check for appointment overlap
        function checkAppointmentOverlap(leaveSchedules, existingAppointments) {
            let overlapFound = false;
            const overlappingAppointments = [];

            leaveSchedules.forEach(leave => {
                const leaveStart = new Date(`${leave.date}T${leave.start_time || '00:00'}`);
                const leaveEnd = new Date(`${leave.date}T${leave.end_time || '23:59'}`);

                existingAppointments.forEach(app => {
                    const appStart = new Date(app.start_time);
                    const appEnd = new Date(app.end_time || app.start_time); // Assuming end_time if not present

                    // Check for overlap
                    if (
                        (leaveStart < appEnd && leaveEnd > appStart)
                    ) {
                        overlapFound = true;
                        overlappingAppointments.push(app);
                    }
                });
            });
            return { overlapFound, overlappingAppointments };
        }

        submitLeaveRequestBtn.addEventListener('click', async () => {
            const token = sessionStorage.getItem('accessToken');
            if (!token) {
                alert('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
                return;
            }

            const leaveType = document.getElementById('leave-type').value;
            const description = document.getElementById('leave-description').value;
            const schedules = [];

            let hasError = false;
            selectedDaysList.querySelectorAll('[data-date]').forEach(dayElement => {
                if (hasError) return;

                const date = dayElement.dataset.date;
                const leaveType = dayElement.querySelector('input[type="radio"]:checked').value;

                if (leaveType === 'all-day') {
                    schedules.push({
                        date: date,
                        start_time: null, // Represents the whole day
                        end_time: null
                    });
                } else { // by-session
                    const checkedSessions = Array.from(dayElement.querySelectorAll('.session-checkboxes input:checked'));
                    if (checkedSessions.length === 0) {
                        alert(`Vui lòng chọn ít nhất một ca nghỉ cho ngày ${date}.`);
                        hasError = true;
                        return;
                    }
                    
                    // Logic to merge consecutive time slots
                    const timeSlots = checkedSessions.map(cb => cb.value.split('-'));
                    timeSlots.sort((a, b) => a[0].localeCompare(b[0])); // Sort by start time

                    if (timeSlots.length > 0) {
                        let currentSchedule = { date: date, start_time: timeSlots[0][0], end_time: timeSlots[0][1] };

                        for (let i = 1; i < timeSlots.length; i++) {
                            const prevEndTime = currentSchedule.end_time;
                            const currentStartTime = timeSlots[i][0];
                            
                            if (prevEndTime === currentStartTime) {
                                // Merge consecutive slots
                                currentSchedule.end_time = timeSlots[i][1];
                            } else {
                                // It's not consecutive, push the previous schedule and start a new one
                                schedules.push(currentSchedule);
                                currentSchedule = { date: date, start_time: timeSlots[i][0], end_time: timeSlots[i][1] };
                            }
                        }
                        schedules.push(currentSchedule); // Push the last schedule
                    }
                }
            });

            if (hasError) {
                return; // Stop submission if there was an error
            }

            if (schedules.length === 0) {
                alert('Vui lòng chọn ít nhất một ngày và cấu hình nghỉ.');
                return;
            }
            
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            for (const schedule of schedules) {
                const leaveDate = new Date(schedule.date);
                if (leaveDate < today) {
                    alert('Không thể gửi yêu cầu nghỉ phép cho ngày trong quá khứ.');
                    return;
                }
            }

            const { overlapFound, overlappingAppointments } = checkAppointmentOverlap(schedules, appointments);

            if (overlapFound) {
                let warningMessage = 'Cảnh báo: Có lịch hẹn trùng với thời gian bạn muốn nghỉ:\n';
                overlappingAppointments.forEach(app => {
                    const appDate = new Date(app.start_time).toLocaleDateString('vi-VN');
                    const appTime = new Date(app.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                    warningMessage += `- Lịch hẹn với bệnh nhân ${app.patient_name} vào lúc ${appTime} ngày ${appDate}\n`;
                });
                warningMessage += '\nBạn có chắc chắn muốn gửi yêu cầu nghỉ phép này không?';

                if (!confirm(warningMessage)) {
                    return;
                }
            }

            try {
                const response = await fetch('/api/doctor/leave-request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ leave_type: leaveType, description, schedules })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    // The backend sends the error message in the 'detail' field
                    throw new Error(errorData.detail || 'Có lỗi xảy ra khi gửi yêu cầu.');
                }

                const result = await response.json();
                alert('Đăng ký nghỉ phép thành công!');
                closeAndResetModal();
                await fetchAppointments();

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