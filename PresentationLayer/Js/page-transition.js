class PageTransition {
    constructor(options = {}) {
        this.transitionDuration = options.transitionDuration || 300;
        this.contentId = options.contentId || 'main-content';
        // Các link loại trừ không áp dụng hiệu ứng
        this.excludeLinks = options.excludeLinks || ['#', '[data-no-transition]', '[target="_blank"]'];
        
        // Cache để lưu HTML các trang đã tải (tăng tốc độ khi back lại)
        this.cache = new Map();
        
        this.init();
    }

    init() {
        // Inject CSS styles cho hiệu ứng
        this.injectStyles();
        
        // Bắt sự kiện click
        this.attachLinkListeners();
        
        // Xử lý sự kiện Back/Forward của trình duyệt
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.url) {
                // Khi back lại, dùng hướng 'back'
                this.loadPage(e.state.url, false, 'back');
            } else {
                // Trường hợp fallback hoặc trang đầu tiên
                this.loadPage(window.location.href, false, 'back');
            }
        });

        // Lưu state ban đầu
        window.history.replaceState({ url: window.location.href }, '', window.location.href);
    }

    injectStyles() {
        if (document.getElementById('page-transition-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'page-transition-styles';
        styles.textContent = `
            /* Container giữ nội dung để tránh nhảy layout khi animation */
            #${this.contentId} {
                transition: transform ${this.transitionDuration}ms cubic-bezier(0.4, 0.0, 0.2, 1), 
                            opacity ${this.transitionDuration}ms cubic-bezier(0.4, 0.0, 0.2, 1);
                transform-origin: center top;
            }

            /* 1. Animation đi tới (Next Page) */
            /* Trang cũ trượt sang trái và mờ đi */
            .slide-out-left {
                opacity: 0 !important;
                transform: translateX(-30px) !important;
            }
            /* Trang mới chuẩn bị trượt từ phải vào */
            .slide-enter-right {
                opacity: 0 !important;
                transform: translateX(30px) !important;
            }

            /* 2. Animation quay lại (Back Page) */
            /* Trang cũ trượt sang phải và mờ đi */
            .slide-out-right {
                opacity: 0 !important;
                transform: translateX(30px) !important;
            }
            /* Trang mới chuẩn bị trượt từ trái vào */
            .slide-enter-left {
                opacity: 0 !important;
                transform: translateX(-30px) !important;
            }

            /* Trạng thái bình thường */
            .slide-active {
                opacity: 1 !important;
                transform: translateX(0) !important;
            }

            /* Loading Bar trên cùng */
            #page-loading-bar {
                position: fixed;
                top: 0;
                left: 0;
                height: 3px;
                background: #2563eb; /* Blue-600 */
                z-index: 9999;
                width: 0%;
                transition: width 0.2s ease;
                box-shadow: 0 1px 2px rgba(37, 99, 235, 0.3);
            }
        `;
        document.head.appendChild(styles);

        // Thêm Loading Bar
        const loader = document.createElement('div');
        loader.id = 'page-loading-bar';
        document.body.appendChild(loader);
    }

    attachLinkListeners() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;

            // Bỏ qua nếu link có target="_blank" hoặc là link download
            if (link.target === '_blank' || link.hasAttribute('download')) return;

            // Kiểm tra internal link
            if (!this.isInternalLink(link)) return;

            // Kiểm tra exclude
            const href = link.getAttribute('href');
            if (this.excludeLinks.some(selector => {
                return href.startsWith('#') || (selector.startsWith('.') ? link.classList.contains(selector.substring(1)) : link.matches(selector));
            })) {
                return;
            }

            // Chặn hành vi mặc định và tải trang
            e.preventDefault();
            this.loadPage(href, true, 'next');
        });
    }

    isInternalLink(link) {
        const href = link.getAttribute('href');
        if (!href) return false;
        if (href.startsWith('javascript:')) return false;
        if (href.startsWith('mailto:') || href.startsWith('tel:')) return false;
        
        // So sánh hostname
        if (link.hostname !== window.location.hostname) return false;
        
        // Bỏ qua nếu chỉ là anchor trên cùng trang (#section)
        const url = new URL(link.href);
        if (url.pathname === window.location.pathname && url.hash) return false;

        return true;
    }

    updateLoadingBar(percent) {
        const bar = document.getElementById('page-loading-bar');
        if (bar) {
            bar.style.width = `${percent}%`;
            if (percent >= 100) {
                setTimeout(() => { bar.style.width = '0%'; }, 300);
            }
        }
    }

    async loadPage(url, pushState = true, direction = 'next') {
        const contentElement = document.getElementById(this.contentId);
        if (!contentElement) {
            window.location.href = url;
            return;
        }

        this.updateLoadingBar(30);

        // 1. Animation Out (Biến mất)
        const outClass = direction === 'next' ? 'slide-out-left' : 'slide-out-right';
        contentElement.classList.add(outClass);

        try {
            // Chờ fetch dữ liệu và animation out cùng lúc
            const [htmlText] = await Promise.all([
                this.fetchContent(url),
                this.wait(this.transitionDuration) // Chờ ít nhất bằng thời gian animation
            ]);

            this.updateLoadingBar(70);

            // 2. Xử lý HTML mới
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(htmlText, 'text/html');
            
            // Lấy nội dung main mới
            const newContent = newDoc.getElementById(this.contentId);
            if (!newContent) throw new Error('No content found in new page');

            // Cập nhật Title
            document.title = newDoc.title;

            // Cập nhật Body Classes (nếu trang mới có style riêng)
            document.body.className = newDoc.body.className;

            // Cập nhật DOM
            contentElement.innerHTML = newContent.innerHTML;
            
            // Cuộn lên đầu trang
            window.scrollTo(0, 0);

            // 3. Chuẩn bị Animation In (Xuất hiện)
            // Xóa class out, thêm class enter (vị trí bắt đầu của trang mới)
            contentElement.classList.remove(outClass);
            const enterClass = direction === 'next' ? 'slide-enter-right' : 'slide-enter-left';
            contentElement.classList.add(enterClass);

            // Force reflow để trình duyệt nhận diện vị trí mới trước khi transition
            void contentElement.offsetWidth; 

            // Kích hoạt transition về vị trí gốc (0)
            contentElement.classList.remove(enterClass);
            contentElement.classList.add('slide-active');

            // Xóa class active sau khi hoàn tất để sạch sẽ
            setTimeout(() => {
                contentElement.classList.remove('slide-active');
            }, this.transitionDuration);

            // 4. Cập nhật History & Menu
            if (pushState) {
                window.history.pushState({ url }, newDoc.title, url);
            }
            this.updateActiveLinks(url);
            
            // 5. Chạy lại Scripts
            this.reexecuteScripts(contentElement);
            this.updateLoadingBar(100);

        } catch (error) {
            console.error('Page transition failed:', error);
            window.location.href = url; // Fallback: tải lại trang thường
        }
    }

    async fetchContent(url) {
        // Kiểm tra cache
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const text = await response.text();
        
        // Lưu cache (giới hạn 10 trang gần nhất để tiết kiệm bộ nhớ)
        if (this.cache.size > 10) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(url, text);
        
        return text;
    }

    updateActiveLinks(url) {
        // Lấy path tương đối để so sánh (ví dụ: /GUI/Page/profile.html)
        const currentPath = new URL(url, window.location.origin).pathname;
        
        document.querySelectorAll('nav a, .sidebar a').forEach(link => {
            const linkPath = new URL(link.href, window.location.origin).pathname;
            
            // Logic so sánh đơn giản
            if (linkPath === currentPath) {
                link.classList.add('active', 'text-blue-600', 'bg-blue-50'); // Các class active của Tailwind
                link.classList.remove('text-gray-700');
            } else {
                link.classList.remove('active', 'text-blue-600', 'bg-blue-50');
                link.classList.add('text-gray-700');
            }
        });
    }

    reexecuteScripts(container) {
        // Tìm tất cả thẻ script trong nội dung mới
        const scripts = container.querySelectorAll('script');
        
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            
            // Sao chép attributes (src, type, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });

            // Sao chép nội dung (inline script)
            if (!oldScript.src) {
                newScript.textContent = oldScript.textContent;
            }

            // Thay thế script cũ bằng script mới để trình duyệt thực thi nó
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }

    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static init(options) {
        return new PageTransition(options);
    }
}

// Khởi tạo khi DOM sẵn sàng
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        PageTransition.init({ contentId: 'main-content' });
    });
} else {
    PageTransition.init({ contentId: 'main-content' });
}
// ```

// ### Cách sử dụng

// 1.  Lưu mã trên vào file `js/page_transition.js`.
// 2.  Chắc chắn rằng tất cả các trang HTML của bạn đều có một container chính bao bọc nội dung thay đổi với ID là `main-content` (hoặc ID bạn cấu hình).
//     Ví dụ:
//     ```html
//     <!-- Header/Sidebar giữ nguyên -->
//     <main id="main-content" class="flex-grow p-4 ...">
//         <!-- Nội dung thay đổi ở đây -->
//     </main>
//     <!-- Footer giữ nguyên -->
//     ```
// 3.  Nhúng script vào cuối trang (tốt nhất là ở Footer hoặc cuối `<body>` của tất cả các trang):
//     ```html
//     <script src="/Js/page_transition.js"></script>