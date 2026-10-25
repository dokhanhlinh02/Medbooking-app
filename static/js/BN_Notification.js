/* ============================================================
   MEDBOOKING - BN_Notification.js
   QUẢN LÝ THÔNG BÁO CHO BỆNH NHÂN
   ============================================================ */

const BN_Notification = (function() {

    const KEY = 'medbooking_bn_notifications';
    const READ_KEY = 'medbooking_bn_notifications_read';

    // =========================================
    // READ/WRITE
    // =========================================
    function getAll() {
        try {
            return JSON.parse(localStorage.getItem(KEY) || '[]');
        } catch (e) {
            console.warn('BN_Notification.getAll error:', e);
            return [];
        }
    }

    function saveAll(list) {
        localStorage.setItem(KEY, JSON.stringify(list));
    }

    // =========================================
    // API
    // =========================================

    // Lấy thông báo chưa đọc
    function getUnread() {
        const readIds = JSON.parse(localStorage.getItem(READ_KEY) || '[]');
        return getAll().filter(n => !readIds.includes(n.id));
    }

    // Đếm số chưa đọc
    function countUnread() {
        return getUnread().length;
    }

    // Đánh dấu đã đọc
    function markAsRead(id) {
        const readIds = JSON.parse(localStorage.getItem(READ_KEY) || '[]');
        if (!readIds.includes(id)) {
            readIds.push(id);
            localStorage.setItem(READ_KEY, JSON.stringify(readIds));
        }
    }

    // Đánh dấu tất cả đã đọc
    function markAllAsRead() {
        const allIds = getAll().map(n => n.id);
        localStorage.setItem(READ_KEY, JSON.stringify(allIds));
    }

    // Xóa thông báo
    function remove(id) {
        const list = getAll().filter(n => n.id !== id);
        saveAll(list);
    }

    // Xóa tất cả
    function clearAll() {
        saveAll([]);
        localStorage.setItem(READ_KEY, '[]');
    }

    // Tạo thông báo mới (dùng cho test/demo)
    function create(data) {
        const list = getAll();
        const noti = {
            id: 'NOTI' + Date.now() + Math.random().toString(36).slice(2, 6),
            type: data.type || 'info', // recheck | info | success | warning
            title: data.title || 'Thông báo',
            message: data.message || '',
            icon: data.icon || 'fa-bell',
            link: data.link || null,
            meta: data.meta || {},
            createdAt: new Date().toISOString(),
            read: false
        };
        list.unshift(noti);
        // Giữ tối đa 50 thông báo
        if (list.length > 50) list.length = 50;
        saveAll(list);
        return noti;
    }

    // =========================================
    // RENDER DROPDOWN TRÊN HEADER
    // =========================================
    function renderDropdown(containerId, badgeId) {
        const container = document.getElementById(containerId);
        const badge = document.getElementById(badgeId);
        if (!container) return;

        const unread = getUnread();
        const all = getAll();

        // Cập nhật badge
        if (badge) {
            if (unread.length > 0) {
                badge.style.display = 'flex';
                badge.textContent = unread.length > 9 ? '9+' : unread.length;
            } else {
                badge.style.display = 'none';
            }
        }

        if (all.length === 0) {
            container.innerHTML = `
                <div class="noti-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>Chưa có thông báo nào</p>
                </div>`;
            return;
        }

        const iconMap = {
            recheck: { icon: 'fa-calendar-plus', color: '#FF6B9D', bg: '#FFE4EC' },
            info:    { icon: 'fa-circle-info',  color: '#3B82F6', bg: '#DBEAFE' },
            success: { icon: 'fa-check-circle', color: '#22C55E', bg: '#DCFCE7' },
            warning: { icon: 'fa-triangle-exclamation', color: '#F59E0B', bg: '#FEF3C7' }
        };

        container.innerHTML = `
            <div class="noti-header">
                <span>Thông báo (${all.length})</span>
                ${unread.length > 0 ? `<button class="noti-mark-all" onclick="BN_Notification.markAllAsRead(); BN_Notification.renderDropdown('${containerId}', '${badgeId}');">Đánh dấu đã đọc</button>` : ''}
            </div>
            <div class="noti-list">
                ${all.slice(0, 8).map(n => {
                    const style = iconMap[n.type] || iconMap.info;
                    const isUnread = unread.find(u => u.id === n.id);
                    const timeAgo = formatTimeAgo(n.createdAt);
                    return `
                        <div class="noti-item ${isUnread ? 'unread' : ''}" onclick="BN_Notification.handleClick('${n.id}', '${containerId}', '${badgeId}')">
                            <div class="noti-icon" style="background: ${style.bg}; color: ${style.color};">
                                <i class="fas ${n.icon || style.icon}"></i>
                            </div>
                            <div class="noti-body">
                                <div class="noti-title">${n.title}</div>
                                <div class="noti-message">${n.message}</div>
                                <div class="noti-time"><i class="far fa-clock"></i> ${timeAgo}</div>
                            </div>
                            ${isUnread ? '<span class="noti-dot"></span>' : ''}
                        </div>
                    `;
                }).join('')}
            </div>
            ${all.length > 8 ? `<div class="noti-footer" onclick="window.location.href='danh_sach_thong_bao.html'">Xem tất cả thông báo <i class="fas fa-arrow-right"></i></div>` : ''}
        `;
    }

    function handleClick(id, containerId, badgeId) {
        const n = getAll().find(x => x.id === id);
        if (!n) return;

        markAsRead(id);

        // Nếu có link -> chuyển trang
        if (n.link) {
            window.location.href = n.link;
            return;
        }

        // Render lại dropdown
        renderDropdown(containerId, badgeId);

        // Hiện toast/modal nếu là recheck
        if (n.type === 'recheck') {
            showRecheckModal(n);
        }
    }

    function showRecheckModal(n) {
        const meta = n.meta || {};
        const dateStr = meta.suggestedDate ? formatDateDisplay(meta.suggestedDate) : '—';
        const sessionMap = { morning: 'Ca sáng (08:00 - 12:00)', afternoon: 'Ca chiều (13:30 - 17:30)', any: 'Bất kỳ ca nào' };
        const sessionStr = sessionMap[meta.suggestedSession] || '—';

        const modalHTML = `
            <div class="modal-overlay active" id="recheck-modal">
                <div class="modal-box">
                    <div class="modal-icon info"><i class="fas fa-calendar-plus"></i></div>
                    <h3>Yêu cầu tái khám</h3>
                    <p>Bác sĩ <strong>${meta.doctorName || 'Bác sĩ'}</strong> đã gửi yêu cầu tái khám cho bạn.</p>
                    <div class="modal-details" style="display: block;">
                        <div class="detail-row"><span class="label">Chẩn đoán</span><span class="value">${meta.diagnosis || '—'}</span></div>
                        <div class="detail-row"><span class="label">Ngày đề xuất</span><span class="value">${dateStr}</span></div>
                        <div class="detail-row"><span class="label">Ca khám</span><span class="value">${sessionStr}</span></div>
                        ${meta.note ? `<div class="detail-row"><span class="label">Ghi chú</span><span class="value">${meta.note}</span></div>` : ''}
                    </div>
                    <div class="modal-actions">
                        <button class="modal-btn modal-btn-secondary" onclick="document.getElementById('recheck-modal').remove()">
                            <i class="fas fa-times"></i> Để sau
                        </button>
                        <button class="modal-btn modal-btn-primary" onclick="BN_Notification.goToRecheck('${id}')">
                            <i class="fas fa-calendar-check"></i> Đặt lịch ngay
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    function goToRecheck(notiId) {
        const n = getAll().find(x => x.id === notiId);
        if (!n) return;
        const meta = n.meta || {};
        // Chuyển tới dat_lich.html với prefill từ yêu cầu tái khám
        const params = new URLSearchParams({
            recheck_from: notiId,
            doctor_id: meta.doctorId || '',
            suggested_date: meta.suggestedDate || '',
            suggested_session: meta.suggestedSession || 'any'
        });
        window.location.href = 'dat_lich.html?' + params.toString();
    }

    // =========================================
    // HELPERS
    // =========================================
    function formatTimeAgo(iso) {
        const diff = Date.now() - new Date(iso).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Vừa xong';
        if (mins < 60) return `${mins} phút trước`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours} giờ trước`;
        const days = Math.floor(hours / 24);
        if (days < 7) return `${days} ngày trước`;
        const d = new Date(iso);
        return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
    }

    function formatDateDisplay(dateStr) {
        if (!dateStr) return '—';
        const d = new Date(dateStr);
        return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
    }

    // =========================================
    // PUBLIC API
    // =========================================
    return {
        getAll,
        getUnread,
        countUnread,
        markAsRead,
        markAllAsRead,
        remove,
        clearAll,
        create,
        renderDropdown,
        handleClick,
        goToRecheck
    };
})();