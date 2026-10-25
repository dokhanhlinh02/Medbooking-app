// frontend/static/js/Auth.js

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. XỬ LÝ ĐĂNG KÝ (dk.html) ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Chặn load lại trang

            const fullname = document.getElementById('hoten').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            // Ràng buộc mật khẩu: Ít nhất 6 ký tự, 1 chữ hoa, 1 số
            const passwordRegex = /^(?=.*[A-Z])(?=.*\d).{6,}$/;

            if (!passwordRegex.test(password)) {
                showNotification('Mật khẩu phải có ít nhất 6 ký tự, bao gồm 1 chữ hoa và 1 số!', 'error');
                return;
            }

            // Lấy danh sách user từ localStorage (giả lập DB)
            let users = JSON.parse(localStorage.getItem('medbooking_users')) || [];

            // Kiểm tra email tồn tại
            const existingUser = users.find(u => u.email === email);
            if (existingUser) {
                showNotification('Email này đã được đăng ký!', 'error');
                return;
            }

            // Lưu user mới
            users.push({ fullname, email, password });
            localStorage.setItem('medbooking_users', JSON.stringify(users));

            showNotification('Đăng ký thành công! Đang chuyển hướng...', 'success');

            setTimeout(() => {
                window.location.href = 'dn.html';
            }, 2000);
        });
    }

    // --- 2. XỬ LÝ ĐĂNG NHẬP (dn.html) ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value.trim();
            const emailLower = email.toLowerCase();
            const password = document.getElementById('password').value;

            // Phân quyền dựa theo định dạng email khớp với backend FastAPI
            let redirectUrl = 'home.html';
            let role = 'guest';

            if (emailLower.startsWith('ad')) {
                role = 'admin';
                redirectUrl = '/admin/home_a.html';
            } else if (emailLower.startsWith('bs.')) {
                role = 'bac_si';
                redirectUrl = '/bac_si/home_bs.html';
            } else if (emailLower.startsWith('lt.')) {
                role = 'le_tan';
                redirectUrl = '/le_tan/dashboard.html';
            } else if (emailLower.endswith('@gmail.com')) {
                role = 'benh_nhan';
                redirectUrl = '/benh_nhan/home_bn.html';
            } else {
                showNotification('Email không thuộc quyền hạn nào trong hệ thống!', 'error');
                return;
            }

            // Lấy danh sách user
            let users = JSON.parse(localStorage.getItem('medbooking_users')) || [];

            // Tìm user khớp email và password
            const user = users.find(u => u.email === email && u.password === password);

            // Cho phép đăng nhập nếu tìm thấy user hoặc tài khoản phân quyền đặc biệt
            if (user || role !== 'benh_nhan') {
                showNotification(`Đăng nhập thành công! Đang chuyển hướng...`, 'success');

                // Lưu trạng thái đăng nhập và phân quyền vào localStorage
                localStorage.setItem('medbooking_role', role);
                localStorage.setItem('medbooking_email', email);
                if (user) {
                    localStorage.setItem('medbooking_current_user', JSON.stringify(user));
                }

                setTimeout(() => {
                    window.location.href = redirectUrl; // Chuyển hướng chính xác sang trang bệnh nhân / bác sĩ / admin
                }, 1500);
            } else {
                // Kiểm tra xem email có tồn tại không để báo lỗi cụ thể
                const emailExists = users.some(u => u.email === email);
                if (emailExists) {
                    showNotification('Mật khẩu không chính xác!', 'error');
                } else {
                    showNotification('Tài khoản chưa tồn tại. Vui lòng đăng ký!', 'error');
                }
            }
        });
    }
});

// Hàm hiển thị thông báo (Toast Message)
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    toast.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
        <span>${message}</span>
    `;

    Object.assign(toast.style, {
        position: 'fixed', top: '20px', right: '20px',
        background: type === 'success' ? '#4caf50' : '#f44336',
        color: 'white', padding: '15px 25px', borderRadius: '10px',
        boxShadow: '0 5px 15px rgba(0,0,0,0.2)', zIndex: '10000',
        display: 'flex', alignItems: 'center', gap: '10px',
        fontSize: '14px', fontWeight: '500', animation: 'slideInRight 0.3s ease-out'
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.5s ease-out forwards';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Thêm keyframes animation
const styleSheet = document.createElement("style");
styleSheet.textContent = `
    @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes fadeOut { from { opacity: 1; } to { opacity: 0; } }
`;
document.head.appendChild(styleSheet);