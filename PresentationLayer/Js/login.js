// === 1. ANIMATION LOGIC (SLIDING) ===
const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Desktop Animation
signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});

// Mobile Animation (Fallback)
const mobileToRegister = document.getElementById('mobile-to-register');
const mobileToLogin = document.getElementById('mobile-to-login');
const signUpContainer = document.querySelector('.sign-up-container');
const signInContainer = document.querySelector('.sign-in-container');

if(mobileToRegister) {
    mobileToRegister.addEventListener('click', (e) => {
        e.preventDefault();
        signInContainer.style.display = 'none';
        signUpContainer.style.display = 'flex';
    });
}
if(mobileToLogin) {
    mobileToLogin.addEventListener('click', (e) => {
        e.preventDefault();
        signUpContainer.style.display = 'none';
        signInContainer.style.display = 'flex';
    });
}

// === 2. FORGOT PASSWORD TOGGLE ===
const loginView = document.getElementById('login-view');
const forgotView = document.getElementById('forgot-view');
const goToForgot = document.getElementById('go-to-forgot');
const backToLogin = document.getElementById('back-to-login-btn');

goToForgot.addEventListener('click', (e) => {
    e.preventDefault();
    loginView.classList.add('hidden');
    forgotView.classList.remove('hidden');
});

backToLogin.addEventListener('click', (e) => {
    e.preventDefault();
    forgotView.classList.add('hidden');
    loginView.classList.remove('hidden');
});

// === 3. HELPER FUNCTIONS ===
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const icon = type === 'success' ? '<i class="fas fa-check-circle text-green-500 text-xl"></i>' : '<i class="fas fa-exclamation-circle text-red-500 text-xl"></i>';
    const borderClass = type === 'success' ? 'border-green-500' : 'border-red-500';
    
    toast.className = `flex items-center gap-3 bg-white px-4 py-3 rounded-lg shadow-xl border-l-4 ${borderClass} transform transition-all duration-300 translate-x-full`;
    toast.innerHTML = `${icon}<div><h4 class="font-bold text-gray-800 text-sm">${type === 'success' ? 'Thành công' : 'Lỗi'}</h4><p class="text-gray-500 text-xs">${message}</p></div>`;
    
    container.appendChild(toast);
    setTimeout(() => toast.classList.remove('translate-x-full'), 100);
    setTimeout(() => { toast.classList.add('translate-x-full', 'opacity-0'); setTimeout(() => toast.remove(), 300); }, 3000);
}

function setBtnLoading(formId, isLoading) {
    const btn = document.querySelector(`#${formId} .btn-submit`);
    const textSpan = btn.querySelector('.btn-text');
    const loaderSpan = btn.querySelector('.btn-loader');
    if (isLoading) {
        btn.disabled = true; btn.classList.add('opacity-70', 'cursor-not-allowed');
        textSpan.classList.add('hidden'); loaderSpan.classList.remove('hidden');
    } else {
        btn.disabled = false; btn.classList.remove('opacity-70', 'cursor-not-allowed');
        textSpan.classList.remove('hidden'); loaderSpan.classList.add('hidden');
    }
}

// === VALIDATION FUNCTIONS ===
function validateFullName(fullName) {
    if (!fullName || fullName.trim().length === 0) {
        return { valid: false, message: 'Vui lòng nhập họ và tên' };
    }
    if (fullName.trim().length < 3) {
        return { valid: false, message: 'Họ và tên phải có ít nhất 3 ký tự' };
    }
    return { valid: true };
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || email.trim().length === 0) {
        return { valid: false, message: 'Vui lòng nhập email' };
    }
    if (!emailRegex.test(email)) {
        return { valid: false, message: 'Email không đúng định dạng' };
    }
    return { valid: true };
}

function validatePhone(phone) {
    // Loại bỏ khoảng trắng và ký tự đặc biệt
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    
    // Regex cho Việt Nam: 10 chữ số bắt đầu từ 0
    const vietnamRegex = /^0[0-9]{9}$/;
    
    // Regex cho Mỹ: 10 chữ số bắt đầu từ 1 hoặc không bắt đầu từ 0,1
    const usRegex = /^(\+?1)?[2-9]\d{2}[2-9]\d{6}$/;
    
    if (!phone || phone.trim().length === 0) {
        return { valid: false, message: 'Vui lòng nhập số điện thoại' };
    }
    
    // Kiểm tra định dạng Việt Nam
    if (vietnamRegex.test(cleanPhone)) {
        return { valid: true };
    }
    
    // Kiểm tra định dạng Mỹ
    if (usRegex.test(cleanPhone)) {
        return { valid: true };
    }
    
    return { valid: false, message: 'Số điện thoại chưa đúng định dạng' };
}

function validateAddress(address) {
    if (!address || address.trim().length === 0) {
        return { valid: false, message: 'Vui lòng nhập địa chỉ' };
    }
    if (address.trim().length < 5) {
        return { valid: false, message: 'Địa chỉ phải có ít nhất 5 ký tự' };
    }
    return { valid: true };
}

function validatePassword(password) {
    if (!password || password.length === 0) {
        return { valid: false, message: 'Vui lòng nhập mật khẩu' };
    }
    if (password.length < 6) {
        return { valid: false, message: 'Mật khẩu phải có ít nhất 6 ký tự' };
    }
    return { valid: true };
}

function validateBirthDate(birthDate) {
    if (!birthDate) {
        return { valid: false, message: 'Vui lòng nhập ngày sinh' };
    }
    return { valid: true };
}

// === 4. LOGIC FIELD TOGGLE ===
const roleRadios = document.querySelectorAll('input[name="role"]');
const doctorFields = document.getElementById('doctor-fields');
const patientFields = document.getElementById('patient-fields');
const hiddenRole = document.getElementById('hidden-role');

roleRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'doctor') {
            doctorFields.classList.remove('hidden'); patientFields.classList.add('hidden');
        } else {
            doctorFields.classList.add('hidden'); patientFields.classList.remove('hidden');
        }
    });
});

// === 5. API CALLS ===
// LOGIN
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setBtnLoading('login-form', true);
    const usernameInput = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    let loginData = isNaN(usernameInput) ? { Username: usernameInput, Password: password } : { Phone: usernameInput, Password: password };

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(loginData)
        });
        if (response.ok) {
            const data = await response.json();
            sessionStorage.setItem('accessToken', data.access_token);
            sessionStorage.setItem('loggedInUser', JSON.stringify(data.user));
            showToast('Đăng nhập thành công!', 'success');
            setTimeout(() => window.location.href = data.redirect_url, 1000);
        } else {
            showToast('Tài khoản hoặc mật khẩu không đúng.', 'error');
            setBtnLoading('login-form', false);
        }
    } catch (error) {
        showToast('Lỗi kết nối.', 'error');
        setBtnLoading('login-form', false);
    }
});

// REGISTER
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const fullName = document.getElementById('reg-fullname').value;
    const email = document.getElementById('reg-email').value;
    const phone = document.getElementById('reg-phone').value;
    const password = document.getElementById('reg-password').value;
    const birthDate = document.getElementById('reg-birthdate').value;
    const address = document.getElementById('reg-address').value;

    // Validate all fields
    const fullNameValidation = validateFullName(fullName);
    if (!fullNameValidation.valid) {
        showToast(fullNameValidation.message, 'error');
        return;
    }

    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
        showToast(emailValidation.message, 'error');
        return;
    }

    const phoneValidation = validatePhone(phone);
    if (!phoneValidation.valid) {
        showToast(phoneValidation.message, 'error');
        return;
    }

    const addressValidation = validateAddress(address);
    if (!addressValidation.valid) {
        showToast(addressValidation.message, 'error');
        return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
        showToast(passwordValidation.message, 'error');
        return;
    }

    const birthDateValidation = validateBirthDate(birthDate);
    if (!birthDateValidation.valid) {
        showToast(birthDateValidation.message, 'error');
        return;
    }

    setBtnLoading('register-form', true);
    const role = 'patient'; // Luôn là patient
    const payload = { role: role };
    
    payload.patient_data = {
        FullName: fullName,
        Email: email,
        Phone: phone,
        Password: password,
        birth_date: birthDate,
        address: address
    };

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        });
        if (response.ok) {
            showToast('Đăng ký thành công! Vui lòng đăng nhập.', 'success');
            document.getElementById('register-form').reset();
            container.classList.remove("right-panel-active"); // Slide back to login
        } else {
            const res = await response.json();
            showToast(res.detail || 'Đăng ký thất bại.', 'error');
        }
    } catch (error) { showToast('Lỗi kết nối.', 'error'); } 
    finally { setBtnLoading('register-form', false); }
});

// FORGOT PASSWORD
document.getElementById('forgot-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setBtnLoading('forgot-password-form', true);
    try {
        const response = await fetch('/api/auth/request-password-reset', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: document.getElementById('forgot-email').value })
        });
        if(response.ok) {
            showToast('✅ Email khôi phục đã được gửi. Vui lòng kiểm tra hộp thư của bạn.', 'success');
            setTimeout(() => { forgotView.classList.add('hidden'); loginView.classList.remove('hidden'); }, 3000);
        } else { showToast('❌ Email không tồn tại.', 'error'); }
    } catch (err) { showToast('❌ Lỗi hệ thống.', 'error'); }
    finally { setBtnLoading('forgot-password-form', false); }
});

// RESET PASSWORD
const resetView = document.getElementById('reset-view');
const resetForm = document.getElementById('reset-password-form');
const backBtn2 = document.getElementById('back-to-login-btn-2');

// Kiểm tra URL xem có token reset password không
function checkResetToken() {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const hash = window.location.hash;
    
    if (token && hash === '#reset-password') {
        // Lưu token vào sessionStorage
        sessionStorage.setItem('resetToken', token);
        loginView.classList.add('hidden');
        resetView.classList.remove('hidden');
        return true;
    }
    return false;
}

// Handle Reset Password Form
resetForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newPassword = document.getElementById('reset-new-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;
    const token = sessionStorage.getItem('resetToken');
    
    if (!newPassword || !confirmPassword) {
        showToast('❌ Vui lòng nhập mật khẩu.', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showToast('❌ Mật khẩu không khớp.', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showToast('❌ Mật khẩu phải có ít nhất 6 ký tự.', 'error');
        return;
    }
    
    setBtnLoading('reset-password-form', true);
    try {
        const response = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: token, new_password: newPassword })
        });
        
        if (response.ok) {
            showToast('✅ Mật khẩu đã được đặt lại thành công! Đang chuyển hướng...', 'success');
            sessionStorage.removeItem('resetToken');
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 3000);
        } else {
            const error = await response.json();
            showToast('❌ ' + (error.detail || 'Lỗi khi đặt lại mật khẩu.'), 'error');
        }
    } catch (err) {
        showToast('❌ Lỗi hệ thống.', 'error');
    }
    finally {
        setBtnLoading('reset-password-form', false);
    }
});

// Back to login từ reset form
backBtn2.addEventListener('click', (e) => {
    e.preventDefault();
    sessionStorage.removeItem('resetToken');
    resetView.classList.add('hidden');
    loginView.classList.remove('hidden');
});

// Check on page load
checkResetToken();
