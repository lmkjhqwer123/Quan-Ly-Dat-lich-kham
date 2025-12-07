document.addEventListener('DOMContentLoaded', () => {
    const headerPlaceholder = document.getElementById('header-placeholder');
    const footerPlaceholder = document.getElementById('footer-placeholder');
    console.log('DOMContentLoaded fired.');
    console.log('headerPlaceholder:', headerPlaceholder);
    console.log('footerPlaceholder:', footerPlaceholder);

    // --- LOAD HEADER & FOOTER ---
    const getSharePath = () => {
        return '/GUI/Share/';
    };

    const sharePath = getSharePath();
    console.log('sharePath:', sharePath);

    const loadComponents = async () => {
        // Load Header
        if (headerPlaceholder) {
            try {
                const headerResponse = await fetch(sharePath + '_header.html');
                console.log('Header fetch response:', headerResponse);
                if (!headerResponse.ok) {
                    throw new Error(`HTTP error! status: ${headerResponse.status}`);
                }
                const headerHtml = await headerResponse.text();
                console.log('Header HTML:', headerHtml.substring(0, 200) + '...'); // Log first 200 chars
                headerPlaceholder.innerHTML = headerHtml;
            } catch (error) {
                console.error('Error loading header:', error);
                headerPlaceholder.innerHTML = '<p class="text-red-500 text-center">Lỗi tải header</p>';
            }
        }

        // Load Footer
        if (footerPlaceholder) {
            try {
                const footerResponse = await fetch(sharePath + '_footer.html');
                console.log('Footer fetch response:', footerResponse);
                if (!footerResponse.ok) {
                    throw new Error(`HTTP error! status: ${footerResponse.status}`);
                }
                const footerHtml = await footerResponse.text();
                console.log('Footer HTML:', footerHtml.substring(0, 200) + '...'); // Log first 200 chars
                footerPlaceholder.innerHTML = footerHtml;
            } catch (error) {
                console.error('Error loading footer:', error);
                footerPlaceholder.innerHTML = '<p class="text-red-500 text-center">Lỗi tải footer</p>';
            }
        }

        // Sau khi tải xong header, chạy các script liên quan đến header
        initializeHeaderScripts();
        highlightActiveNav();
        
    };

    const initializeHeaderScripts = () => {
        const logoutButton = document.getElementById('logout-button');
        const welcomeUser = document.getElementById('welcome-user');

        // --- AUTHENTICATION ---
        const accessToken = sessionStorage.getItem('accessToken');
        if (!accessToken && !window.location.pathname.endsWith('login.html')) {
            window.location.href = '/GUI/login.html';
            return;
        }

        const loggedInUser = sessionStorage.getItem('loggedInUser');
        if (welcomeUser && loggedInUser) { // Check if loggedInUser is not null
            try {
                const user = JSON.parse(loggedInUser);
                // Use the 'name' property from the parsed user object
                const userName = user.name || user.FullName || user.Username || 'Người dùng';
                welcomeUser.textContent = `Chào, ${userName}!`;
            } catch (error) {
                console.error("Failed to parse user data:", error);
                // Fallback for safety
                welcomeUser.textContent = `Chào!`;
            }
        }

        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                sessionStorage.removeItem('loggedInUser');
                sessionStorage.removeItem('userRole');
                window.location.href = '/login.html';
            });
        }

        // --- DATE & TIME ---
        function updateDateTime() {
            const dateEl = document.getElementById('current-date');
            const timeEl = document.getElementById('current-time');
            if (!dateEl || !timeEl) return;
            const now = new Date();
            dateEl.textContent = now.toLocaleDateString('vi-VN', { weekday: 'long', day: 'numeric', month: 'numeric', year: 'numeric' });
            timeEl.textContent = now.toLocaleTimeString('vi-VN');
        }
        updateDateTime();
        setInterval(updateDateTime, 1000);

        // --- WEATHER API ---
        function fetchWeather() {
            const tempEl = document.getElementById('weather-temp');
            const iconEl = document.getElementById('weather-icon');
            if (!tempEl || !iconEl) return;
            
            // Dữ liệu thời tiết giả lập để tránh lỗi API và chạy nhanh hơn
            tempEl.textContent = '28°C';
            iconEl.textContent = '⛅️';
            console.log('Mock weather loaded.');
        }
        fetchWeather();
    };

    const highlightActiveNav = () => {
        const currentPage = window.location.pathname.split('/').pop();
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const linkPage = link.getAttribute('href');
            if (linkPage === currentPage || (currentPage === '' && linkPage === 'home.html')) {
                link.classList.add('text-blue-600', 'font-bold');
                link.classList.remove('text-gray-700');
            }
        });
    };

    

    // Bắt đầu quá trình
    loadComponents();
});