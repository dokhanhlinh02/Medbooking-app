/* ============================================================
   MEDBOOKING ADMIN — UI Controller (v4)
   Thêm: Notification realtime
   ============================================================ */
(function () {
    'use strict';

    console.log('[admin.js] Bắt đầu load...');

    function waitForAPI(cb) {
        if (window.MedBookingAPI) {
            return cb(window.MedBookingAPI);
        }
        let tries = 0;
        const t = setInterval(() => {
            tries++;
            if (window.MedBookingAPI) {
                clearInterval(t);
                console.log('[admin.js] API sẵn sàng sau', tries * 100, 'ms');
                cb(window.MedBookingAPI);
            } else if (tries > 50) {
                clearInterval(t);
                console.error('[admin.js] ❌ MedBookingAPI không load!');
            }
        }, 100);
    }

    const $ = (s, r = document) => r.querySelector(s);
    const $$ = (s, r = document) => [...r.querySelectorAll(s)];

    function toast(msg, type = 'info') {
        const colors = {
            success: 'linear-gradient(135deg,#10B981,#059669)',
            error:   'linear-gradient(135deg,#EF4444,#DC2626)',
            warning: 'linear-gradient(135deg,#F59E0B,#D97706)',
            info:    'linear-gradient(135deg,#8B5CF6,#7C3AED)'
        };
        const el = document.createElement('div');
        el.style.cssText = `position:fixed;top:20px;right:20px;z-index:99999;padding:14px 22px;border-radius:14px;color:#fff;font-family:Inter,sans-serif;font-size:13.5px;font-weight:600;background:${colors[type]};box-shadow:0 12px 28px rgba(0,0,0,0.15);transform:translateX(120%);transition:transform .4s cubic-bezier(.16,1,.3,1);display:flex;align-items:center;gap:8px;max-width:340px;`;
        const icons = { success:'check-circle', error:'exclamation-circle', warning:'exclamation-triangle', info:'info-circle' };
        el.innerHTML = `<i class="fas fa-${icons[type]}"></i> <span>${msg}</span>`;
        document.body.appendChild(el);
        requestAnimationFrame(() => el.style.transform = 'translateX(0)');
        setTimeout(() => {
            el.style.transform = 'translateX(120%)';
            setTimeout(() => el.remove(), 400);
        }, 2800);
    }

    function openModal(id) {
        const m = document.getElementById(id);
        if (m) { m.style.display = 'block'; document.body.classList.add('modal-open'); }
    }
    function closeModal(id) {
        const m = document.getElementById(id);
        if (m) { m.style.display = 'none'; document.body.classList.remove('modal-open'); }
    }

    const roleText = { admin: 'Quản trị viên', doctor: 'Bác sĩ', receptionist: 'Lễ tân', patient: 'Bệnh nhân' };

    /* ============================================================
       NOTIFICATION - Hiển thị thông báo realtime
       ============================================================ */
    function initNotifications(API) {
        const header = document.querySelector('header');
        if (!header) return;
        if (document.getElementById('notif-wrapper')) return;

        const wrapper = document.createElement('div');
        wrapper.id = 'notif-wrapper';
        wrapper.className = 'notif-wrapper';
        wrapper.innerHTML = `
            <button class="notif-bell" id="notif-bell" aria-label="Thông báo">
                <i class="fas fa-bell"></i>
                <span class="notif-badge" id="notif-badge" style="display:none;">0</span>
            </button>
            <div class="notif-panel" id="notif-panel">
                <div class="notif-header">
                    <h4><i class="fas fa-bell"></i> Thông báo</h4>
                    <button class="mark-all" id="mark-all-read">Đánh dấu đã đọc</button>
                </div>
                <div class="notif-list" id="notif-list">
                    <div class="notif-empty">
                        <i class="fas fa-inbox"></i>
                        Đang tải thông báo...
                    </div>
                </div>
            </div>
        `;

        const themeBtn = header.querySelector('.theme-toggle');
        const headerRight = header.querySelector('div');
        if (themeBtn && themeBtn.parentNode) {
            themeBtn.parentNode.insertBefore(wrapper, themeBtn);
        } else if (headerRight) {
            headerRight.insertBefore(wrapper, headerRight.firstChild);
        }

        const bell = document.getElementById('notif-bell');
        const panel = document.getElementById('notif-panel');
        const list = document.getElementById('notif-list');
        const badge = document.getElementById('notif-badge');

        bell.addEventListener('click', (e) => {
            e.stopPropagation();
            panel.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                panel.classList.remove('open');
            }
        });

        function render(notifications) {
            const unread = notifications.filter(n => !n.read).length;

            if (unread > 0) {
                badge.textContent = unread > 9 ? '9+' : unread;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }

            if (!notifications.length) {
                list.innerHTML = `
                    <div class="notif-empty">
                        <i class="fas fa-inbox"></i>
                        Không có thông báo nào
                    </div>
                `;
                return;
            }

            const iconMap = {
                'Lịch hẹn mới': { icon: 'fa-calendar-plus', cls: '' },
                'Thanh toán thành công': { icon: 'fa-check-circle', cls: 'success' },
                'Cảnh báo hệ thống': { icon: 'fa-exclamation-triangle', cls: 'warning' },
                'Đánh giá mới': { icon: 'fa-star', cls: '' }
            };

            list.innerHTML = notifications.map(n => {
                const meta = iconMap[n.title] || { icon: 'fa-bell', cls: '' };
                return `
                    <div class="notif-item ${n.read ? '' : 'unread'}" data-id="${n.id}">
                        <div class="notif-icon ${meta.cls}">
                            <i class="fas ${meta.icon}"></i>
                        </div>
                        <div class="notif-body">
                            <div class="notif-title">
                                <span>${n.title}</span>
                                <span class="notif-time">${n.time}</span>
                            </div>
                            <div class="notif-message">${n.message}</div>
                        </div>
                    </div>
                `;
            }).join('');

            list.querySelectorAll('.notif-item').forEach(item => {
                item.addEventListener('click', () => {
                    item.classList.remove('unread');
                    const id = item.dataset.id;
                    const found = notifications.find(x => x.id === id);
                    if (found) found.read = true;
                    const stillUnread = notifications.filter(x => !x.read).length;
                    if (stillUnread > 0) {
                        badge.textContent = stillUnread > 9 ? '9+' : stillUnread;
                        badge.style.display = 'flex';
                    } else {
                        badge.style.display = 'none';
                    }
                });
            });
        }

        async function load() {
            if (!API || typeof API.getNotifications !== 'function') {
                render([
                    { id: 'N001', title: 'Lịch hẹn mới', message: 'Bệnh nhân Nguyễn Văn A vừa đặt lịch khám Tim mạch', time: '5 phút trước', read: false },
                    { id: 'N002', title: 'Thanh toán thành công', message: 'Giao dịch GD002 đã hoàn tất 1.200.000₫', time: '1 giờ trước', read: false },
                    { id: 'N003', title: 'Cảnh báo hệ thống', message: 'Có 3 bản ghi trong thùng rác cần xử lý', time: '2 giờ trước', read: false },
                    { id: 'N004', title: 'Đánh giá mới', message: 'BS. Phạm Thị D vừa nhận đánh giá 5 sao', time: '1 ngày trước', read: true }
                ]);
                return;
            }
            try {
                const res = await API.getNotifications();
                render(res.data || []);
            } catch (err) {
                console.error('[notif] Lỗi load:', err);
            }
        }

        const markAllBtn = document.getElementById('mark-all-read');
        markAllBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (API && typeof API.markAllRead === 'function') {
                await API.markAllRead();
            }
            badge.style.display = 'none';
            list.querySelectorAll('.notif-item').forEach(it => it.classList.remove('unread'));
            toast('Đã đánh dấu tất cả đã đọc', 'success');
        });

        load();
        setInterval(load, 30000);
    }

    /* ===== DASHBOARD ===== */
    function initDashboard(API) {
        const canvas = document.getElementById('revenueChart');
        if (!canvas) return;
        const yearSel = document.getElementById('filter-year');
        const quarterSel = document.getElementById('filter-quarter');

        async function refresh() {
            const year = yearSel ? yearSel.value : '2026';
            const quarter = quarterSel ? quarterSel.value : 'all';
            const res = await API.getDashboardStats(year, quarter);
            const s = res.data;
            const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
            set('total-appointments', s.totalAppointments);
            set('total-revenue', window.MedBookingUtils.formatMoney(s.totalRevenue));
            set('total-profit', window.MedBookingUtils.formatMoney(s.totalProfit));
            set('cancellation-rate', s.cancelRate + '%');
            renderRevenueChart(s.revenueByMonth);
        }
        if (yearSel) yearSel.addEventListener('change', refresh);
        if (quarterSel) quarterSel.addEventListener('change', refresh);
        refresh();
    }

    let chartInstance = null;
    function renderRevenueChart(data) {
        const ctx = document.getElementById('revenueChart');
        if (!ctx || typeof Chart === 'undefined') return;
        if (chartInstance) chartInstance.destroy();
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(167,139,250,0.1)' : 'rgba(139,92,246,0.08)';
        const textColor = isDark ? '#B8AECB' : '#8B7FA8';
        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.label),
                datasets: [
                    { label: 'Doanh thu', data: data.map(d => d.value), borderColor: '#8B5CF6',
                      backgroundColor: (context) => { const g = context.chart.ctx.createLinearGradient(0, 0, 0, 260); g.addColorStop(0, 'rgba(167,139,250,0.4)'); g.addColorStop(1, 'rgba(167,139,250,0)'); return g; },
                      borderWidth: 3, tension: 0.45, fill: true, pointBackgroundColor: '#fff', pointBorderColor: '#8B5CF6', pointBorderWidth: 2, pointRadius: 4 },
                    { label: 'Kỳ trước', data: data.map(d => d.prev), borderColor: '#F0ABFC', backgroundColor: 'transparent', borderWidth: 2, borderDash: [5,4], tension: 0.45, pointRadius: 0, fill: false }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(26,20,40,0.95)', padding: 12, titleColor: '#fff', bodyColor: '#E0D8FF', cornerRadius: 10, displayColors: false } },
                scales: { x: { grid: { display: false }, ticks: { color: textColor, font: { size: 11, weight: '600' } } },
                          y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 } } } }
            }
        });
    }

    /* ===== TÀI KHOẢN ===== */
    function initAccountPage(API) {
        const tbody = document.getElementById('account-table-body');
        if (!tbody) return;
        console.log('[admin.js] initAccountPage chạy');

        const searchEl = document.getElementById('search-account');
        const roleEl = document.getElementById('filter-role');
        const statusEl = document.getElementById('filter-status');
        const btnAdd = document.getElementById('btn-add-account');
        const form = document.getElementById('form-account-info');
        const modalId = 'account-form-modal';
        const lockModalId = 'lock-modal';
        let editingId = null;

        async function refresh() {
            const res = await API.getAccounts({
                search: searchEl?.value || '',
                role: roleEl?.value || 'all',
                status: statusEl?.value || 'all'
            });
            console.log('[admin.js] getAccounts →', res.data.length, 'dòng');
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:#8B7FA8;">Không có tài khoản nào.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(a => {
                const isActive = a.status === 'active';
                return `<tr>
                    <td><strong>${a.id}</strong></td>
                    <td>${a.name}</td>
                    <td>${a.email}</td>
                    <td>${a.phone}</td>
                    <td>${roleText[a.role] || a.role}</td>
                    <td><span class="badge ${isActive ? 'success' : 'danger'}">${isActive ? 'Đang hoạt động' : 'Đã khóa'}</span></td>
                    <td>
                        <button type="button" class="btn-edit-account" data-id="${a.id}">Sửa</button>
                        <button type="button" class="btn-toggle-lock" data-id="${a.id}" data-action="${isActive ? 'lock' : 'unlock'}">${isActive ? 'Khóa' : 'Mở khóa'}</button>
                        <button type="button" class="btn-delete-account" data-id="${a.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa</button>
                    </td>
                </tr>`;
            }).join('');

            $$('.btn-edit-account', tbody).forEach(btn => {
                btn.onclick = async () => {
                    const res = await API.getAccounts();
                    const acc = res.data.find(x => x.id === btn.dataset.id);
                    if (!acc) return;
                    editingId = acc.id;
                    $('#form-account-title').textContent = 'Chỉnh sửa tài khoản';
                    $('#acc-name').value = acc.name;
                    $('#acc-email').value = acc.email;
                    $('#acc-phone').value = acc.phone;
                    $('#acc-role').value = acc.role;
                    $('#acc-password').value = '';
                    openModal(modalId);
                };
            });
            $$('.btn-toggle-lock', tbody).forEach(btn => {
                btn.onclick = () => {
                    const id = btn.dataset.id;
                    if (btn.dataset.action === 'lock') {
                        $('#lock-target-id').value = id;
                        $('#lock-reason-text').value = '';
                        $('#lock-modal-title').textContent = 'Lý do khóa tài khoản';
                        openModal(lockModalId);
                    } else {
                        API.toggleAccountStatus(id).then(() => { toast('Đã mở khóa', 'success'); refresh(); });
                    }
                };
            });
            $$('.btn-delete-account', tbody).forEach(btn => {
                btn.onclick = async () => {
                    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này vào thùng rác?')) return;
                    await API.deleteAccount(btn.dataset.id);
                    toast('Đã chuyển vào thùng rác', 'success');
                    refresh();
                };
            });
        }

        if (searchEl) searchEl.addEventListener('input', refresh);
        if (roleEl) roleEl.addEventListener('change', refresh);
        if (statusEl) statusEl.addEventListener('change', refresh);

        if (btnAdd) btnAdd.onclick = () => {
            editingId = null;
            $('#form-account-title').textContent = 'Thêm Tài khoản Mới';
            form.reset();
            openModal(modalId);
        };

        if (form) form.onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                name: $('#acc-name').value.trim(),
                email: $('#acc-email').value.trim(),
                phone: $('#acc-phone').value.trim(),
                role: $('#acc-role').value
            };
            const pwd = $('#acc-password').value;
            if (!data.name || !data.email || !data.phone) { toast('Nhập đầy đủ thông tin', 'error'); return; }
            if (!editingId && !pwd) { toast('Nhập mật khẩu ban đầu', 'error'); return; }
            try {
                if (editingId) { await API.updateAccount(editingId, data); toast('Đã cập nhật', 'success'); }
                else { await API.createAccount(data); toast('Đã thêm tài khoản', 'success'); }
                closeModal(modalId); refresh();
            } catch (err) { toast(err.message || 'Lỗi', 'error'); }
        };

        const btnCancel = $('#btn-cancel-account');
        if (btnCancel) btnCancel.onclick = () => closeModal(modalId);

        const lockForm = $('#form-lock-reason');
        if (lockForm) lockForm.onsubmit = async (e) => {
            e.preventDefault();
            const id = $('#lock-target-id').value;
            const reason = $('#lock-reason-text').value.trim();
            if (!reason) { toast('Nhập lý do khóa', 'error'); return; }
            await API.toggleAccountStatus(id, reason);
            toast('Đã khóa tài khoản', 'success');
            closeModal(lockModalId); refresh();
        };
        const btnCancelLock = $('#btn-cancel-lock');
        if (btnCancelLock) btnCancelLock.onclick = () => closeModal(lockModalId);

        refresh();
    }

    /* ===== BÁC SĨ ===== */
    function initDoctorPage(API) {
        const tbody = document.getElementById('doctor-table-body');
        if (!tbody) return;
        console.log('[admin.js] initDoctorPage chạy');
        const searchEl = $('#search-doctor');
        const filterSpec = $('#filter-specialty');
        const btnAdd = $('#btn-add-doctor');
        const form = $('#form-doctor-info');
        const modalId = 'doctor-form-modal';
        const docSpecSel = $('#doc-specialty');
        let editingId = null;

        API.getSpecialties().then(specRes => {
            if (filterSpec) filterSpec.innerHTML = '<option value="all">Tất cả chuyên khoa</option>' + specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            if (docSpecSel) docSpecSel.innerHTML = specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        });

        async function refresh() {
            const res = await API.getDoctors({ search: searchEl?.value || '', specialtyId: filterSpec?.value || 'all' });
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:#8B7FA8;">Không có bác sĩ nào.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(d => {
                const stars = '★'.repeat(Math.round(d.rating)) + '☆'.repeat(5 - Math.round(d.rating));
                return `<tr>
                    <td><strong>${d.id}</strong></td>
                    <td>${d.name}</td>
                    <td>${d.specialtyName}</td>
                    <td>${d.email}<br><small style="color:#8B7FA8;">${d.phone}</small></td>
                    <td><span class="badge ${d.status === 'available' ? 'success' : 'danger'}">${d.status === 'available' ? 'Đang trực' : 'Nghỉ'}</span></td>
                    <td><span style="color:#F59E0B;">${stars}</span> ${d.rating.toFixed(1)}</td>
                    <td>
                        <button type="button" class="btn-edit-doctor" data-id="${d.id}">Sửa</button>
                        <button type="button" class="btn-delete-doctor" data-id="${d.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa</button>
                    </td>
                </tr>`;
            }).join('');

            $$('.btn-edit-doctor', tbody).forEach(btn => btn.onclick = async () => {
                const res = await API.getDoctors();
                const d = res.data.find(x => x.id === btn.dataset.id);
                if (!d) return;
                editingId = d.id;
                $('#form-title').textContent = 'Chỉnh sửa Bác sĩ';
                $('#doc-name').value = d.name;
                $('#doc-specialty').value = d.specialtyId;
                $('#doc-email').value = d.email;
                $('#doc-phone').value = d.phone;
                openModal(modalId);
            });
            $$('.btn-delete-doctor', tbody).forEach(btn => btn.onclick = async () => {
                if (!confirm('Chuyển bác sĩ này vào thùng rác?')) return;
                await API.deleteDoctor(btn.dataset.id);
                toast('Đã chuyển vào thùng rác', 'success');
                refresh();
            });
        }

        if (searchEl) searchEl.addEventListener('input', refresh);
        if (filterSpec) filterSpec.addEventListener('change', refresh);
        if (btnAdd) btnAdd.onclick = () => {
            editingId = null;
            $('#form-title').textContent = 'Thêm Bác sĩ Mới';
            form.reset();
            openModal(modalId);
        };
        if (form) form.onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                name: $('#doc-name').value.trim(),
                specialtyId: $('#doc-specialty').value,
                email: $('#doc-email').value.trim(),
                phone: $('#doc-phone').value.trim()
            };
            if (!data.name || !data.specialtyId || !data.email || !data.phone) { toast('Nhập đầy đủ', 'error'); return; }
            try {
                if (editingId) { await API.updateDoctor(editingId, data); toast('Đã cập nhật', 'success'); }
                else { await API.createDoctor(data); toast('Đã thêm', 'success'); }
                closeModal(modalId); refresh();
            } catch (err) { toast(err.message, 'error'); }
        };
        const btnCancel = $('#btn-cancel-doctor');
        if (btnCancel) btnCancel.onclick = () => closeModal(modalId);
        refresh();
    }

    /* ===== CHUYÊN KHOA ===== */
    function initSpecialtyPage(API) {
        const tbody = document.getElementById('specialty-table-body');
        if (!tbody) return;
        console.log('[admin.js] initSpecialtyPage chạy');
        const searchEl = $('#search-specialty');
        const btnAdd = $('#btn-add-specialty');
        const form = $('#form-specialty-info');
        const modalId = 'specialty-form-modal';
        let editingId = null;

        async function refresh() {
            const res = await API.getSpecialties({ search: searchEl?.value || '' });
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:#8B7FA8;">Không có chuyên khoa nào.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(s => `<tr>
                <td><strong>${s.id}</strong></td>
                <td>${s.name}</td>
                <td style="max-width:320px;">${s.desc || ''}</td>
                <td>${s.doctorCount || 0} bác sĩ</td>
                <td>
                    <button type="button" class="btn-edit-spec" data-id="${s.id}">Sửa</button>
                    <button type="button" class="btn-delete-spec" data-id="${s.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa</button>
                </td>
            </tr>`).join('');

            $$('.btn-edit-spec', tbody).forEach(btn => btn.onclick = async () => {
                const res = await API.getSpecialties();
                const s = res.data.find(x => x.id === btn.dataset.id);
                if (!s) return;
                editingId = s.id;
                $('#form-specialty-title').textContent = 'Chỉnh sửa Chuyên khoa';
                $('#spec-name').value = s.name;
                $('#spec-desc').value = s.desc || '';
                openModal(modalId);
            });
            $$('.btn-delete-spec', tbody).forEach(btn => btn.onclick = async () => {
                if (!confirm('Chuyển chuyên khoa này vào thùng rác?')) return;
                await API.deleteSpecialty(btn.dataset.id);
                toast('Đã chuyển vào thùng rác', 'success');
                refresh();
            });
        }
        if (searchEl) searchEl.addEventListener('input', refresh);
        if (btnAdd) btnAdd.onclick = () => {
            editingId = null;
            $('#form-specialty-title').textContent = 'Thêm Chuyên khoa Mới';
            form.reset();
            openModal(modalId);
        };
        if (form) form.onsubmit = async (e) => {
            e.preventDefault();
            const data = { name: $('#spec-name').value.trim(), desc: $('#spec-desc').value.trim() };
            if (!data.name) { toast('Nhập tên', 'error'); return; }
            if (editingId) { await API.updateSpecialty(editingId, data); toast('Đã cập nhật', 'success'); }
            else { await API.createSpecialty(data); toast('Đã thêm', 'success'); }
            closeModal(modalId); refresh();
        };
        const btnCancel = $('#btn-cancel-specialty');
        if (btnCancel) btnCancel.onclick = () => closeModal(modalId);
        refresh();
    }

    /* ===== DỊCH VỤ ===== */
    function initServicePage(API) {
        const tbody = document.getElementById('service-table-body');
        if (!tbody) return;
        console.log('[admin.js] initServicePage chạy');
        const searchEl = $('#search-service');
        const filterSpec = $('#filter-service-specialty');
        const btnAdd = $('#btn-add-service');
        const form = $('#form-service-info');
        const modalId = 'service-form-modal';
        const servSpecSel = $('#serv-specialty');
        let editingId = null;

        API.getSpecialties().then(specRes => {
            if (filterSpec) filterSpec.innerHTML = '<option value="all">Tất cả chuyên khoa</option>' + specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            if (servSpecSel) servSpecSel.innerHTML = specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
        });

        async function refresh() {
            const res = await API.getServices({ search: searchEl?.value || '', specialtyId: filterSpec?.value || 'all' });
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:#8B7FA8;">Không có dịch vụ nào.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(s => `<tr>
                <td><strong>${s.id}</strong></td>
                <td>${s.name}</td>
                <td>${s.specialtyName}</td>
                <td style="font-weight:700;color:#10B981;">${window.MedBookingUtils.formatMoney(s.price)}</td>
                <td style="max-width:280px;">${s.desc || ''}</td>
                <td>
                    <button type="button" class="btn-edit-serv" data-id="${s.id}">Sửa</button>
                    <button type="button" class="btn-delete-serv" data-id="${s.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa</button>
                </td>
            </tr>`).join('');

            $$('.btn-edit-serv', tbody).forEach(btn => btn.onclick = async () => {
                const res = await API.getServices();
                const s = res.data.find(x => x.id === btn.dataset.id);
                if (!s) return;
                editingId = s.id;
                $('#form-service-title').textContent = 'Chỉnh sửa Dịch vụ';
                $('#serv-name').value = s.name;
                $('#serv-specialty').value = s.specialtyId;
                $('#serv-price').value = s.price;
                $('#serv-desc').value = s.desc || '';
                openModal(modalId);
            });
            $$('.btn-delete-serv', tbody).forEach(btn => btn.onclick = async () => {
                if (!confirm('Chuyển dịch vụ này vào thùng rác?')) return;
                await API.deleteService(btn.dataset.id);
                toast('Đã chuyển vào thùng rác', 'success');
                refresh();
            });
        }
        if (searchEl) searchEl.addEventListener('input', refresh);
        if (filterSpec) filterSpec.addEventListener('change', refresh);
        if (btnAdd) btnAdd.onclick = () => {
            editingId = null;
            $('#form-service-title').textContent = 'Thêm Dịch vụ Mới';
            form.reset();
            openModal(modalId);
        };
        if (form) form.onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                name: $('#serv-name').value.trim(),
                specialtyId: $('#serv-specialty').value,
                price: parseInt($('#serv-price').value, 10) || 0,
                desc: $('#serv-desc').value.trim()
            };
            if (!data.name || !data.specialtyId) { toast('Nhập đầy đủ', 'error'); return; }
            if (editingId) { await API.updateService(editingId, data); toast('Đã cập nhật', 'success'); }
            else { await API.createService(data); toast('Đã thêm', 'success'); }
            closeModal(modalId); refresh();
        };
        const btnCancel = $('#btn-cancel-service');
        if (btnCancel) btnCancel.onclick = () => closeModal(modalId);
        refresh();
    }

    /* ===== MAPPING ===== */
    function initMappingPage(API) {
        const tbody = document.getElementById('mapping-table-body');
        if (!tbody) return;
        console.log('[admin.js] initMappingPage chạy');
        const searchEl = $('#search-mapping');
        const filterSpec = $('#filter-mapping-specialty');
        const btnAdd = $('#btn-add-mapping');
        const form = $('#form-mapping-info');
        const modalId = 'mapping-form-modal';
        const mapSpecSel = $('#map-specialty');
        const mapDocSel = $('#map-doctor');
        let editingId = null;

        Promise.all([API.getSpecialties(), API.getDoctors()]).then(([specRes, docRes]) => {
            if (filterSpec) filterSpec.innerHTML = '<option value="all">Tất cả chuyên khoa đích</option>' + specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            if (mapSpecSel) mapSpecSel.innerHTML = specRes.data.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
            if (mapDocSel) mapDocSel.innerHTML = '<option value="">-- Không chỉ định cụ thể --</option>' + docRes.data.map(d => `<option value="${d.id}">${d.name} (${d.specialtyName})</option>`).join('');
        });

        async function refresh() {
            const res = await API.getMappings({ search: searchEl?.value || '', specialtyId: filterSpec?.value || 'all' });
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:#8B7FA8;">Không có mapping nào.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(m => `<tr>
                <td><strong>${m.id}</strong></td>
                <td>${m.keywords}</td>
                <td>${m.specialtyName}</td>
                <td>${m.doctorName || '<em style="color:#8B7FA8;">Không chỉ định</em>'}</td>
                <td><span class="badge info">${m.priority}</span></td>
                <td>
                    <button type="button" class="btn-edit-map" data-id="${m.id}">Sửa</button>
                    <button type="button" class="btn-delete-map" data-id="${m.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa</button>
                </td>
            </tr>`).join('');

            $$('.btn-edit-map', tbody).forEach(btn => btn.onclick = async () => {
                const res = await API.getMappings();
                const m = res.data.find(x => x.id === btn.dataset.id);
                if (!m) return;
                editingId = m.id;
                $('#form-mapping-title').textContent = 'Chỉnh sửa Mapping';
                $('#map-keywords').value = m.keywords;
                $('#map-specialty').value = m.specialtyId;
                $('#map-doctor').value = m.doctorId || '';
                $('#map-priority').value = m.priority;
                openModal(modalId);
            });
            $$('.btn-delete-map', tbody).forEach(btn => btn.onclick = async () => {
                if (!confirm('Xóa mapping này?')) return;
                await API.deleteMapping(btn.dataset.id);
                toast('Đã xóa mapping', 'success');
                refresh();
            });
        }
        if (searchEl) searchEl.addEventListener('input', refresh);
        if (filterSpec) filterSpec.addEventListener('change', refresh);
        if (btnAdd) btnAdd.onclick = () => {
            editingId = null;
            $('#form-mapping-title').textContent = 'Thêm Quy tắc Mapping Mới';
            form.reset();
            $('#map-priority').value = 1;
            openModal(modalId);
        };
        if (form) form.onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                keywords: $('#map-keywords').value.trim(),
                specialtyId: $('#map-specialty').value,
                doctorId: $('#map-doctor').value,
                priority: parseInt($('#map-priority').value, 10) || 1
            };
            if (!data.keywords || !data.specialtyId) { toast('Nhập đầy đủ', 'error'); return; }
            if (editingId) { await API.updateMapping(editingId, data); toast('Đã cập nhật', 'success'); }
            else { await API.createMapping(data); toast('Đã thêm', 'success'); }
            closeModal(modalId); refresh();
        };
        const btnCancel = $('#btn-cancel-mapping');
        if (btnCancel) btnCancel.onclick = () => closeModal(modalId);
        refresh();
    }

    /* ===== NHẬT KÝ ===== */
    function initAuditLogPage(API) {
        const tbody = document.getElementById('audit-log-table-body');
        if (!tbody) return;
        console.log('[admin.js] initAuditLogPage chạy');
        const yearSel = $('#filter-year');
        const monthSel = $('#filter-month');
        const statusSel = $('#filter-status');
        const btnSearch = $('#btn-search-log');
        const btnExport = $('#btn-export-log');

        async function refresh() {
            const res = await API.getTransactions({
                year: yearSel?.value || '2026',
                month: monthSel?.value || 'all',
                status: statusSel?.value || 'all'
            });
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:40px;color:#8B7FA8;">Không có dữ liệu.</td></tr>`;
                return;
            }
            const fmt = window.MedBookingUtils.formatMoney;
            tbody.innerHTML = res.data.map(t => `<tr>
                <td><strong>${t.id}</strong></td>
                <td>${t.date.split('-').reverse().join('/')}</td>
                <td>${t.patient}</td>
                <td style="color:#10B981;font-weight:700;">${fmt(t.revenue)}</td>
                <td style="color:#3B82F6;font-weight:700;">${fmt(t.profit)}</td>
                <td>${t.doctorConfirm || '—'}</td>
                <td>${t.receptionConfirm || '—'}</td>
                <td>${t.updatedAt}</td>
                <td><span class="badge ${t.status === 'completed' ? 'success' : 'danger'}">${t.status === 'completed' ? 'Hoàn thành' : 'Đã hủy'}</span></td>
            </tr>`).join('');
        }
        if (yearSel) yearSel.addEventListener('change', refresh);
        if (monthSel) monthSel.addEventListener('change', refresh);
        if (statusSel) statusSel.addEventListener('change', refresh);
        if (btnSearch) btnSearch.onclick = refresh;
        if (btnExport) btnExport.onclick = () => toast('Đã xuất Excel (demo)', 'success');
        refresh();
    }

    /* ===== THÙNG RÁC ===== */
    function initRecycleBinPage(API) {
        const tbody = document.getElementById('recycle-bin-body');
        if (!tbody) return;
        console.log('[admin.js] initRecycleBinPage chạy');

        async function refresh() {
            const res = await API.getRecycleBin();
            if (!res.data.length) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:#8B7FA8;"><i class="fas fa-trash" style="font-size:32px;opacity:0.3;display:block;margin-bottom:8px;"></i>Thùng rác đang trống.</td></tr>`;
                return;
            }
            tbody.innerHTML = res.data.map(item => `<tr>
                <td><strong>${item.id}</strong></td>
                <td>${item.type}</td>
                <td>${item.name}</td>
                <td>${item.deletedAt}</td>
                <td>
                    <button type="button" class="btn-restore" data-id="${item.id}" style="background:linear-gradient(135deg,#10B981,#059669);color:#fff;border:none;">Khôi phục</button>
                    <button type="button" class="btn-delete-forever" data-id="${item.id}" style="background:#FEF2F2;color:#DC2626;border-color:#FECACA;">Xóa vĩnh viễn</button>
                </td>
            </tr>`).join('');

            $$('.btn-restore', tbody).forEach(btn => btn.onclick = async () => {
                await API.restoreItem(btn.dataset.id);
                toast('Đã khôi phục', 'success');
                refresh();
            });
            $$('.btn-delete-forever', tbody).forEach(btn => btn.onclick = async () => {
                if (!confirm('Xóa vĩnh viễn không thể hoàn tác. Tiếp tục?')) return;
                await API.deleteItemForever(btn.dataset.id);
                toast('Đã xóa vĩnh viễn', 'success');
                refresh();
            });
        }
        refresh();
    }

    /* ===== HỒ SƠ ===== */
    function initProfilePage(API) {
        const formInfo = $('#form-profile');
        if (!formInfo) return;
        API.getCurrentUser().then(res => {
            const u = res.data;
            if ($('#profile-name')) $('#profile-name').value = u.name;
            if ($('#profile-email')) $('#profile-email').value = u.email;
        });
        formInfo.onsubmit = async (e) => {
            e.preventDefault();
            const name = $('#profile-name').value.trim();
            const email = $('#profile-email').value.trim();
            if (!name || !email) return;
            await API.updateCurrentUser({ name, email });
            toast('Đã cập nhật hồ sơ', 'success');
        };
        const formPwd = $('#form-password');
        if (formPwd) formPwd.onsubmit = (e) => {
            e.preventDefault();
            toast('Đổi mật khẩu thành công (demo)', 'success');
            formPwd.reset();
        };
    }

    document.addEventListener('DOMContentLoaded', () => {
        console.log('[admin.js] DOMContentLoaded');
        waitForAPI((API) => {
            console.log('[admin.js] Bắt đầu init...');
            initDashboard(API);
            initAccountPage(API);
            initDoctorPage(API);
            initSpecialtyPage(API);
            initServicePage(API);
            initMappingPage(API);
            initAuditLogPage(API);
            initRecycleBinPage(API);
            initProfilePage(API);
            initNotifications(API);
            console.log('[admin.js] ✅ Init xong');
        });
    });

    window.MedBookingToast = toast;
})();