// reminders.js - Timeline Reminders with Pagination

if (typeof window.initRemindersPage === 'undefined') {
    window.initRemindersPage = function() {
        const remindersContainer = document.getElementById('reminders-container');
        const loadingDiv = document.getElementById('loading');
        const noRemindersDiv = document.getElementById('no-reminders');
        const paginationControls = document.getElementById('pagination-controls');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const currentPageSpan = document.getElementById('current-page');
        const totalPagesSpan = document.getElementById('total-pages');

        if (!remindersContainer) {
            console.error('Required element (reminders-container) not found.');
            return;
        }

        // Pagination state
        let allAppointments = [];
        let currentPage = 1;
        const itemsPerPage = 5;
        let totalPages = 1;

        // ============= UTILITY FUNCTIONS =============

        // Format relative date
        function formatReminderDate(appointmentDatetime) {
            const appointmentDate = new Date(appointmentDatetime);
            const today = new Date();
            const diffTime = appointmentDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            const time = appointmentDate.toLocaleString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            if (diffDays <= 7 && diffDays > 0) {
                if (diffDays === 1) {
                    return `ngày mai, lúc ${time}`;
                } else {
                    return `${diffDays} ngày nữa, lúc ${time}`;
                }
            } else {
                const date = appointmentDate.toLocaleString('vi-VN', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });
                return `ngày ${date} lúc ${time}`;
            }
        }

        // Get date key for grouping
        function getDateKey(appointmentDatetime) {
            const date = new Date(appointmentDatetime);
            return date.toISOString().split('T')[0];
        }

        // Format date header
        function formatDateHeader(dateKey) {
            const date = new Date(dateKey);
            const today = new Date();
            const isToday = date.toDateString() === today.toDateString();
            
            const [year, month, day] = dateKey.split('-');
            
            if (isToday) return `Hôm nay, ${day}/${month}`;
            return `Ngày ${day}/${month}/${year}`;
        }

        // Get status display info
        function getStatusInfo(status) {
            const statusMap = {
                'confirmed': {
                    icon: 'fa-check',
                    message: 'Đã xác nhận',
                    bgClass: 'bg-blue-100 text-blue-600',
                    badgeClass: 'bg-blue-50 text-blue-700 border-blue-200',
                    borderLeft: 'border-l-4 border-blue-500'
                },
                'completed': {
                    icon: 'fa-check-double',
                    message: 'Đã hoàn thành',
                    bgClass: 'bg-green-100 text-green-600',
                    badgeClass: 'bg-green-50 text-green-700 border-green-200',
                    borderLeft: 'border-l-4 border-green-500'
                },
                'cancelled': {
                    icon: 'fa-times',
                    message: 'Đã hủy',
                    bgClass: 'bg-red-100 text-red-600',
                    badgeClass: 'bg-red-50 text-red-700 border-red-200',
                    borderLeft: 'border-l-4 border-red-500'
                },
                'pending': {
                    icon: 'fa-hourglass-half',
                    message: 'Chờ xác nhận',
                    bgClass: 'bg-yellow-100 text-yellow-600',
                    badgeClass: 'bg-yellow-50 text-yellow-700 border-yellow-200',
                    borderLeft: 'border-l-4 border-yellow-400'
                }
            };
            return statusMap[status] || statusMap['pending'];
        }

        // Generate reminder text
        function generateReminderText(apt, status) {
            const baseText = `Khám chuyên khoa <b>${apt.SpecialtyName}</b>`;
            const docText = `Bác sĩ: <b>${apt.DoctorName}</b>`;
            
            if (status === 'confirmed') {
                return `Bạn có lịch hẹn ${baseText} với ${docText}. Vui lòng đến sớm 15 phút để làm thủ tục.`;
            } else if (status === 'completed') {
                return `Lịch khám ${baseText} đã hoàn tất. Bạn có thể xem lại kết quả trong hồ sơ bệnh án.`;
            } else if (status === 'cancelled') {
                return `Lịch khám ${baseText} này đã bị hủy bỏ.`;
            } else if (status === 'pending') {
                return `Yêu cầu đặt lịch ${baseText} đang chờ phòng khám xác nhận.`;
            }
        }

        // Get time string
        function getTimeString(appointmentDatetime) {
            const date = new Date(appointmentDatetime);
            return date.toLocaleString('vi-VN', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // ============= RENDER FUNCTIONS =============

        // Render current page
        function renderPage(page) {
            const startIdx = (page - 1) * itemsPerPage;
            const endIdx = startIdx + itemsPerPage;
            const pageAppointments = allAppointments.slice(startIdx, endIdx);
            
            remindersContainer.innerHTML = '<div class="absolute top-4 bottom-0 left-[23px] w-0.5 bg-gray-200 z-0"></div>';
            
            let currentDate = null;
            
            pageAppointments.forEach(apt => {
                const dateKey = getDateKey(apt.AppointmentDatetime);
                
                // Add date header if date changed
                if (dateKey !== currentDate) {
                    currentDate = dateKey;
                    const dateHeaderDiv = document.createElement('div');
                    dateHeaderDiv.className = 'relative z-10 mb-4 mt-6 first:mt-0';
                    dateHeaderDiv.innerHTML = `
                        <div class="flex items-center">
                            <div class="w-12 flex justify-center flex-shrink-0">
                                <div class="w-3 h-3 bg-gray-400 rounded-full border-2 border-white ring-2 ring-gray-100"></div>
                            </div>
                            <span class="text-xs font-bold text-gray-500 uppercase tracking-wider bg-white px-2 py-1 rounded border border-gray-100 shadow-sm">
                                ${formatDateHeader(dateKey)}
                            </span>
                        </div>
                    `;
                    remindersContainer.appendChild(dateHeaderDiv);
                }
                
                // Create appointment card
                const status = apt.Status?.toLowerCase() || 'pending';
                const statusInfo = getStatusInfo(status);
                const timeString = getTimeString(apt.AppointmentDatetime);
                const reminderText = generateReminderText(apt, status);
                const relativeTime = formatReminderDate(apt.AppointmentDatetime);
                
                const reminderDiv = document.createElement('div');
                reminderDiv.className = 'relative z-10 mb-6 group';
                
                reminderDiv.innerHTML = `
                    <div class="flex items-start">
                        <div class="w-12 flex justify-center flex-shrink-0 pt-4">
                            <div class="w-8 h-8 rounded-full ${statusInfo.bgClass} flex items-center justify-center border-4 border-white shadow-sm group-hover:scale-110 transition-transform duration-200">
                                <i class="fas ${statusInfo.icon} text-xs"></i>
                            </div>
                        </div>
                        
                        <div class="flex-1 bg-white border border-gray-100 rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-200 ml-2 ${statusInfo.borderLeft}">
                            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 mb-2">
                                <div>
                                    <div class="flex items-center gap-2 mb-1">
                                        <i class="far fa-clock text-gray-400 text-xs"></i>
                                        <span class="text-sm font-bold text-gray-800">${timeString}</span>
                                        <span class="text-xs text-gray-400">• ${relativeTime}</span>
                                    </div>
                                    <h4 class="font-bold text-gray-900 text-md">${apt.SpecialtyName}</h4>
                                </div>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusInfo.badgeClass}">
                                    ${statusInfo.message}
                                </span>
                            </div>
                            
                            <div class="text-sm text-gray-600 mt-2 bg-gray-50 p-3 rounded-lg border border-gray-100">
                                <i class="fas fa-info-circle text-gray-400 mr-1"></i> ${reminderText}
                            </div>
                            
                            <div class="mt-3 flex gap-3 justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                <button class="text-xs text-blue-600 hover:text-blue-800 font-medium">Chi tiết</button>
                                ${status === 'confirmed' ? '<button class="text-xs text-red-600 hover:text-red-800 font-medium">Hủy lịch</button>' : ''}
                            </div>
                        </div>
                    </div>
                `;
                
                remindersContainer.appendChild(reminderDiv);
            });
            
            // Update pagination controls
            currentPage = page;
            currentPageSpan.textContent = page;
            totalPagesSpan.textContent = totalPages;
            prevBtn.disabled = page === 1;
            nextBtn.disabled = page === totalPages;
        }

        // ============= PAGINATION HANDLERS =============

        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                renderPage(currentPage - 1);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                renderPage(currentPage + 1);
            }
        });

        // ============= LOAD DATA =============

        async function loadReminders() {
            try {
                loadingDiv.style.display = 'flex';
                remindersContainer.style.display = 'none';
                noRemindersDiv.style.display = 'none';

                const token = sessionStorage.getItem('accessToken');
                if (!token) {
                    throw new Error('Vui lòng đăng nhập để xem lịch hẹn.');
                }

                const response = await fetch('/api/patients/me/appointments/history', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Không thể tải lịch hẹn.');
                }

                const appointments = await response.json();

                if (!appointments || appointments.length === 0) {
                    loadingDiv.style.display = 'none';
                    noRemindersDiv.style.display = 'flex';
                    return;
                }

                // Sort appointments by date
                allAppointments = appointments.sort((a, b) => {
                    return new Date(a.AppointmentDatetime) - new Date(b.AppointmentDatetime);
                });

                // Calculate pagination
                totalPages = Math.ceil(allAppointments.length / itemsPerPage);
                
                // Show UI
                loadingDiv.style.display = 'none';
                remindersContainer.style.display = 'block';
                paginationControls.style.display = totalPages > 1 ? 'flex' : 'none';

                // Render first page
                renderPage(1);

            } catch (error) {
                console.error('Error loading reminders:', error);
                loadingDiv.style.display = 'none';
                noRemindersDiv.style.display = 'flex';
                noRemindersDiv.innerHTML = `
                    <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center text-gray-300 mb-4">
                        <i class="fas fa-exclamation-circle text-2xl"></i>
                    </div>
                    <h3 class="text-gray-900 font-medium mb-1">Lỗi tải dữ liệu</h3>
                    <p class="text-gray-500 text-sm">${error.message}</p>
                    <button class="mt-4 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition shadow-sm" onclick="location.reload()">
                        Thử lại
                    </button>
                `;
            }
        }

        // ============= INITIALIZE =============

        // Auto-mark active nav
        function setActiveNav() {
            const currentPage = window.location.pathname.split('/').pop() || 'reminders.html';
            const navLinks = document.querySelectorAll('#sidebar-nav .nav-link');
            
            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === 'reminders.html') {
                    link.classList.add('bg-blue-50', 'text-blue-700', 'border', 'border-blue-100');
                }
            });
        }

        setActiveNav();
        loadReminders();
    };
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initRemindersPage);
} else {
    window.initRemindersPage();
}
