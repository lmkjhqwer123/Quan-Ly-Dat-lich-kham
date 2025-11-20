document.addEventListener('DOMContentLoaded', function () {
    const specialtySelect = document.getElementById('specialty');
    const doctorSelect = document.getElementById('doctor');
    const appointmentTimeInput = document.getElementById('appointment-time');
    const timeSlotButtons = document.querySelectorAll('.time-slot-button');

    // Calendar elements
    const calendarGrid = document.getElementById('calendar-grid');
    const monthYearDisplay = document.getElementById('month-year');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const hiddenAppointmentDateInput = document.getElementById('appointment-date');

    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
    let selectedDate = null; // To store the currently selected date object
    let selectedDoctorId = null; // To store the currently selected doctor ID

    let isDoctorSelected = false; // New: Track if a doctor has been selected
    let isDateSelected = false;   // New: Track if a date has been selected

    // Define the fixed time slots
    const FIXED_TIME_SLOTS = [
        "07:00-09:00",
        "09:00-11:00",
        "13:00-15:00",
        "15:00-17:00"
    ];

    let monthlyAvailabilityData = {}; // To store availability data for the current month

    // Initially disable doctor select, calendar navigation, and time slots
    doctorSelect.disabled = true;
    doctorSelect.innerHTML = '<option value="" disabled selected>Vui lòng chọn chuyên khoa trước</option>';
    prevMonthBtn.disabled = true;
    nextMonthBtn.disabled = true;
    timeSlotButtons.forEach(button => {
        button.disabled = true;
        button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
        button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
    });

    // Function to fetch monthly availability
    async function fetchMonthlyAvailability(doctorId, year, month) {
        if (!doctorId) {
            monthlyAvailabilityData = {};
            return;
        }
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/doctor/${doctorId}/availability/monthly/${year}/${month + 1}`); // month + 1 because JS month is 0-indexed
            if (!response.ok) {
                throw new Error('Failed to fetch monthly availability');
            }
            monthlyAvailabilityData = await response.json();
        } catch (error) {
            console.error('Error fetching monthly availability:', error);
            monthlyAvailabilityData = {};
        }
    }

    // Function to fetch daily availability
    async function fetchDailyAvailability(doctorId, year, month, day) {
        if (!doctorId) {
            return {};
        }
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/doctor/${doctorId}/availability/daily/${year}/${month + 1}/${day}`); // month + 1 because JS month is 0-indexed
            if (!response.ok) {
                throw new Error('Failed to fetch daily availability');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching daily availability:', error);
            return {};
        }
    }

    // Function to render the calendar
    async function renderCalendar() {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        today.setHours(0, 0, 0, 0); // Normalize today to start of day

        const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
        const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0);
        const daysInMonth = lastDayOfMonth.getDate();

        // Clear previous days
        calendarGrid.innerHTML = '';

        // Fetch monthly availability data if a doctor is selected
        if (selectedDoctorId) {
            await fetchMonthlyAvailability(selectedDoctorId, currentYear, currentMonth);
        } else {
            monthlyAvailabilityData = {}; // Clear data if no doctor is selected
        }

        // Adjust start day to be Sunday (0)
        let startDay = firstDayOfMonth.getDay(); // 0 for Sunday, 1 for Monday, etc.

        // Calculate days from previous month to show
        const prevMonthLastDay = new Date(currentYear, currentMonth, 0).getDate();
        for (let i = startDay; i > 0; i--) {
            const day = document.createElement('div');
            day.classList.add('calendar-day', 'calendar-day-other-month');
            day.innerHTML = `<span class="day-number">${prevMonthLastDay - i + 1}</span>`;
            calendarGrid.appendChild(day);
        }

        // Render current month's days
        for (let i = 1; i <= daysInMonth; i++) {
            const day = document.createElement('div');
            day.classList.add('calendar-day');
            day.innerHTML = `<span class="day-number">${i}</span>`;

            const date = new Date(currentYear, currentMonth, i);
            date.setHours(0, 0, 0, 0); // Normalize for comparison

            const yyyy = date.getFullYear();
            const mm = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
            const dd = String(date.getDate()).padStart(2, '0');
            const fullDateString = `${yyyy}-${mm}-${dd}`;
            day.dataset.date = fullDateString; // Store date in YYYY-MM-DD format

            let isDayDisabled = false;

            if (!isDoctorSelected) {
                isDayDisabled = true;
                day.classList.add('calendar-day-other-month');
                day.style.cursor = 'not-allowed';
                day.addEventListener('click', function() {
                    alert('Vui lòng chọn bác sĩ trước khi chọn ngày.');
                });
            } else if (date < today) {
                isDayDisabled = true;
                day.classList.add('calendar-day-other-month'); // Use this class for disabled styling
                day.style.cursor = 'not-allowed';
            } else {
                // Check if all time slots are booked for this day
                const unavailableSlots = monthlyAvailabilityData[i] || [];
                if (unavailableSlots.length === FIXED_TIME_SLOTS.length) {
                    isDayDisabled = true;
                    day.classList.add('fully-booked-day'); // Add class for fully booked days
                    day.style.cursor = 'not-allowed';
                    day.addEventListener('click', function() {
                        alert('Ngày này đã kín lịch. Vui lòng chọn ngày khác.');
                    });
                } else {
                    day.addEventListener('click', function() {
                        if (this.classList.contains('calendar-day-other-month') || this.classList.contains('fully-booked-day')) return; // Do nothing if disabled

                        // Remove selected class from previously selected day
                        const previouslySelected = calendarGrid.querySelector('.calendar-day.selected');
                        if (previouslySelected) {
                            previouslySelected.classList.remove('selected');
                        }

                        // Add selected class to current day
                        this.classList.add('selected');
                        const [year, month, dayOfMonth] = this.dataset.date.split('-').map(Number);
                        selectedDate = new Date(year, month - 1, dayOfMonth); // Month is 0-indexed
                        hiddenAppointmentDateInput.value = this.dataset.date; // Update hidden input
                        isDateSelected = true; // Set date selected flag
                        updateTimeSlotAvailability(); // Re-evaluate time slots
                    });
                }

                // Highlight selected date if it matches
                if (selectedDate && date.getTime() === selectedDate.getTime()) {
                    day.classList.add('selected');
                }
            }
            calendarGrid.appendChild(day);
        }

        // Calculate days from next month to show (to fill 6 rows)
        const totalDaysDisplayed = startDay + daysInMonth;
        const remainingCells = 42 - totalDaysDisplayed; // 6 rows * 7 days/row = 42 cells

        for (let i = 1; i <= remainingCells; i++) {
            const day = document.createElement('div');
            day.classList.add('calendar-day', 'calendar-day-other-month');
            day.innerHTML = `<span class="day-number">${i}</span>`;
            calendarGrid.appendChild(day);
        }

        updateMonthYearDisplay();
    }

    // Function to update month and year display
    function updateMonthYearDisplay() {
        const date = new Date(currentYear, currentMonth);
        monthYearDisplay.textContent = date.toLocaleString('vi-VN', { month: 'long', year: 'numeric' });
    }

    // Event listeners for month navigation
    prevMonthBtn.addEventListener('click', function() {
        if (!isDoctorSelected) {
            alert('Vui lòng chọn bác sĩ trước khi chọn ngày.');
            return;
        }
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    });

    nextMonthBtn.addEventListener('click', function() {
        if (!isDoctorSelected) {
            alert('Vui lòng chọn bác sĩ trước khi chọn ngày.');
            return;
        }
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    });

    // Function to fetch specialties and populate the dropdown
    function loadSpecialties() {
        fetch('http://127.0.0.1:8000/api/specialties/')
            .then(response => response.json())
            .then(data => {
                data.forEach(specialty => {
                    const option = document.createElement('option');
                    option.value = specialty.SpecialtyId;
                    option.textContent = specialty.Name;
                    specialtySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading specialties:', error));
    }

    // Function to fetch doctors based on specialty
    function loadDoctors(specialtyId) {
        // Clear existing doctor options
        doctorSelect.innerHTML = '<option value="" disabled selected>Đang tải...</option>';
        doctorSelect.disabled = true;

        fetch(`http://127.0.0.1:8000/api/doctors/?sort_speciality=${specialtyId}`)
            .then(response => response.json())
            .then(data => {
                doctorSelect.innerHTML = '<option value="" disabled selected>Chọn bác sĩ</option>';
                data.forEach(doctor => {
                    const option = document.createElement('option');
                    option.value = doctor.DoctorId;
                    option.textContent = doctor.FullName;
                    doctorSelect.appendChild(option);
                });
                doctorSelect.disabled = false;
                isDoctorSelected = false; // Ensure this is false until a doctor is explicitly selected
            })
            .catch(error => {
                console.error('Error loading doctors:', error);
                doctorSelect.innerHTML = '<option value="" disabled selected>Lỗi khi tải bác sĩ</option>';
                doctorSelect.disabled = true;
                isDoctorSelected = false;
            });
    }

    // Event listener for doctor change
    doctorSelect.addEventListener('change', function() {
        selectedDoctorId = this.value;
        if (selectedDoctorId) {
            isDoctorSelected = true; // A doctor has been selected
            prevMonthBtn.disabled = false; // Enable calendar navigation
            nextMonthBtn.disabled = false;
            isDateSelected = false; // Reset date selection state
            selectedDate = null;
            hiddenAppointmentDateInput.value = '';
            timeSlotButtons.forEach(button => { // Disable time slots
                button.disabled = true;
                button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            });
            renderCalendar(); // Re-render calendar to enable dates
        } else {
            isDoctorSelected = false;
            prevMonthBtn.disabled = true;
            nextMonthBtn.disabled = true;
            isDateSelected = false;
            selectedDate = null;
            hiddenAppointmentDateInput.value = '';
            timeSlotButtons.forEach(button => {
                button.disabled = true;
                button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            });
            renderCalendar();
        }
    });

    // Event listener for specialty change
    specialtySelect.addEventListener('change', function () {
        const selectedSpecialtyId = this.value;
        if (selectedSpecialtyId) {
            loadDoctors(selectedSpecialtyId);
            isDoctorSelected = false; // Reset doctor selection state
            isDateSelected = false;   // Reset date selection state
            selectedDate = null;
            hiddenAppointmentDateInput.value = '';
            prevMonthBtn.disabled = true; // Disable calendar navigation
            nextMonthBtn.disabled = true;
            timeSlotButtons.forEach(button => { // Disable time slots
                button.disabled = true;
                button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            });
            renderCalendar(); // Re-render calendar to disable dates
        } else {
            // Disable and reset doctor select if no specialty is chosen
            doctorSelect.innerHTML = '<option value="" disabled selected>Vui lòng chọn chuyên khoa trước</option>';
            doctorSelect.disabled = true;
            isDoctorSelected = false;
            isDateSelected = false;
            selectedDate = null;
            hiddenAppointmentDateInput.value = '';
            prevMonthBtn.disabled = true;
            nextMonthBtn.disabled = true;
            timeSlotButtons.forEach(button => {
                button.disabled = true;
                button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            });
            renderCalendar();
        }
    });

    // Add click listener to doctorSelect for disabled state
    doctorSelect.addEventListener('click', function(event) {
        if (this.disabled) {
            event.preventDefault();
            alert('Vui lòng chọn chuyên khoa trước khi chọn bác sĩ.');
        }
    });

    // Initial load of specialties
    loadSpecialties();

    // Function to load patient info
    function loadPatientInfo() {
        const accessToken = sessionStorage.getItem('accessToken');
        if (!accessToken) {
            console.error('Access token not found.');
            // Redirect to login or show an error
            return;
        }

        fetch('/api/patients/me', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch patient information');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('full-name').value = data.FullName;
            document.getElementById('phone').value = data.Phone;
            document.getElementById('email').value = data.Email;
        })
        .catch(error => {
            console.error('Error loading patient info:', error);
        });
    }

    // Load patient info on page load
    loadPatientInfo();

    // Handle time slot button clicks
    timeSlotButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!isDateSelected) {
                event.preventDefault();
                alert('Vui lòng chọn ngày trước khi chọn giờ hẹn.');
                return;
            }
            if (button.disabled) { // Prevent clicking disabled buttons
                event.preventDefault();
                return;
            }
            // Remove 'selected' class from all buttons
            timeSlotButtons.forEach(btn => {
                if (!btn.disabled) { // Only deselect if not disabled
                    btn.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600');
                    btn.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-100');
                }
            });


            // Add 'selected' class to the clicked button
            this.classList.add('bg-teal-500', 'text-white', 'hover:bg-teal-600');
            this.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-100');


            // Set the hidden input's value
            appointmentTimeInput.value = this.dataset.time.split('-')[0] + ':00';
        });
    });

    async function updateTimeSlotAvailability() {
        // Reset all time slot buttons to default state
        timeSlotButtons.forEach(button => {
            button.disabled = false;
            button.classList.remove('bg-red-500', 'text-white', 'cursor-not-allowed', 'bg-teal-500', 'hover:bg-teal-600', 'bg-gray-300', 'text-gray-500');
            button.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-100');
            button.title = ''; // Clear tooltip
        });

        // Ensure a doctor and date are selected before checking availability
        if (!selectedDoctorId || !selectedDate || !isDateSelected) {
            timeSlotButtons.forEach(button => {
                button.disabled = true;
                button.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-100');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
            });
            return;
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0); // Normalize today to start of day
        const selectedDateNormalized = new Date(selectedDate);
        selectedDateNormalized.setHours(0, 0, 0, 0); // Normalize selectedDate to start of day

        const currentHour = new Date().getHours();
        const isToday = selectedDateNormalized.getTime() === today.getTime();

        // Fetch daily availability from the backend
        const dailyAvailability = await fetchDailyAvailability(selectedDoctorId, selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate());

        timeSlotButtons.forEach(button => {
            const timeSlotName = button.dataset.time;
            const [startTimeStr] = timeSlotName.split('-');
            const [startHour] = startTimeStr.split(':').map(Number);

            // Disable past time slots for today
            if (isToday && currentHour >= startHour) {
                button.disabled = true;
                button.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-100', 'bg-teal-500', 'text-white');
                button.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
                button.title = 'Khung giờ này đã qua.';
            } else if (dailyAvailability[timeSlotName] === false) { // Check backend availability for booked slots or leave
                button.disabled = true;
                // Clear existing styles
                button.classList.remove('bg-teal-500', 'text-white', 'hover:bg-teal-600', 'bg-white', 'text-gray-700', 'hover:bg-gray-100');
                // Add styles for unavailable slot (red color)
                button.classList.add('bg-red-500', 'text-white', 'cursor-not-allowed');
                button.title = 'Khung giờ này đã được đặt hoặc bác sĩ không có mặt.'; // Tooltip for user
            } else {
                button.disabled = false;
                // Re-apply default styling if not disabled
                if (!button.classList.contains('bg-teal-500')) {
                    button.classList.remove('bg-gray-300', 'text-gray-500', 'cursor-not-allowed', 'bg-red-500');
                    button.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-100');
                }
            }
        });
    }

    // Initial render of the calendar
    renderCalendar();
    updateTimeSlotAvailability(); // Call initially to disable time slots if no date is selected

    // Handle form submission
    const bookingForm = document.getElementById('booking-form');
    bookingForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent actual form submission

        // Collect data from the form
        const specialtyId = document.getElementById('specialty').value;
        const doctorId = document.getElementById('doctor').value;
        const appointmentDate = document.getElementById('appointment-date').value;
        const appointmentTime = document.getElementById('appointment-time').value;
        const reason = document.getElementById('reason').value;
        const termsAccepted = document.getElementById('terms').checked;

        // Basic validation
        if (!specialtyId || !doctorId || !appointmentDate || !appointmentTime) {
            alert('Vui lòng điền đầy đủ thông tin bắt buộc: chuyên khoa, bác sĩ, ngày và giờ hẹn.');
            return;
        }

        if (!termsAccepted) {
            alert('Bạn phải đồng ý với các điều khoản để tiếp tục.');
            return;
        }

        // Combine date and time
        const appointmentDatetime = `${appointmentDate}T${appointmentTime}`;

        // Prepare the data object
        const formData = {
            SpecialtyId: parseInt(specialtyId, 10),
            DoctorId: parseInt(doctorId, 10),
            AppointmentDatetime: appointmentDatetime,
            Symptoms: reason,
            // PatientId will be taken from the token on the backend
        };

        // Submit the booking data to the backend
        submitBooking(formData);
    });

    function submitBooking(formData) {
        const accessToken = sessionStorage.getItem('accessToken');
        if (!accessToken) {
            alert('Bạn chưa đăng nhập. Vui lòng đăng nhập để đặt lịch.');
            // Optionally redirect to login page
            window.location.href = 'login.html';
            return;
        }

        fetch('/api/patients/me/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            // If the response is not OK, we need to handle the error
            if (!response.ok) {
                // Try to parse the error response from the backend
                return response.json().then(errorData => {
                    // Throw an error with the specific message from the backend
                    throw new Error(errorData.detail || `Lỗi ${response.status}: Đã có lỗi xảy ra.`);
                });
            }
            // If response is OK, parse the success JSON
            return response.json();
        })
        .then(data => {
            alert('Đặt lịch hẹn thành công! Vui lòng kiểm tra lịch sử đặt hẹn.');
            // Redirect to the history page on success
            window.location.href = '/PresentationLayer/GUI/Page/history.html';
        })
        .catch(error => {
            // Catch any error thrown (from network or from the !response.ok block)
            console.error('Error booking appointment:', error);
            alert(`Lỗi khi đặt lịch: ${error.message}`);
        });
    }
});
