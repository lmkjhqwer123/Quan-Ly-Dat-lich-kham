// active_nav.js - Tự động đánh dấu link active dựa trên URL hiện tại

document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop() || 'profile.html';
    
    // Tìm tất cả nav links trong sidebar
    const navLinks = document.querySelectorAll('aside nav a, .sidebar nav a, .menu nav a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Xóa active styles
        link.classList.remove('text-blue-600', 'bg-gray-100', 'text-white', 'bg-blue-600');
        link.classList.add('text-gray-700');
        link.classList.remove('hover:bg-gray-100');
        
        // Kiểm tra xem link có phải trang hiện tại không
        const isCurrentPage = href === currentPage || (currentPage === '' && href === 'profile.html');
        
        if (isCurrentPage) {
            // Thêm active style
            link.classList.remove('text-gray-700');
            link.classList.add('text-blue-600', 'bg-gray-100');
        }
    });
});
