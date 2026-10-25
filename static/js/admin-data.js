/* ============================================================
   MEDBOOKING — Mock Data Layer (v4)
   Thêm: pushNotification()
   ============================================================ */
(function (global) {
    'use strict';

    console.log('[admin-data.js] Bắt đầu load...');

    const STORAGE_KEY = 'medbooking_admin_db';

    const seedData = {
        accounts: [
            { id: 'TK001', name: 'Nguyễn Văn A', email: 'admin@medbooking.com', phone: '0901234567', role: 'admin', status: 'active', createdAt: '2026-01-15' },
            { id: 'TK002', name: 'Trần Thị B', email: 'bacsi.b@medbooking.com', phone: '0912345678', role: 'doctor', status: 'active', createdAt: '2026-02-20' },
            { id: 'TK003', name: 'Lê Văn C', email: 'letan.c@medbooking.com', phone: '0923456789', role: 'receptionist', status: 'active', createdAt: '2026-03-10' },
            { id: 'TK004', name: 'Phạm Thị D', email: 'benhnhan.d@gmail.com', phone: '0934567890', role: 'patient', status: 'active', createdAt: '2026-04-05' },
            { id: 'TK005', name: 'Hoàng Văn E', email: 'bacsi.e@medbooking.com', phone: '0945678901', role: 'doctor', status: 'locked', createdAt: '2026-04-12' },
            { id: 'TK006', name: 'Vũ Thị F', email: 'benhnhan.f@gmail.com', phone: '0956789012', role: 'patient', status: 'active', createdAt: '2026-05-18' },
            { id: 'TK007', name: 'Đặng Văn G', email: 'letan.g@medbooking.com', phone: '0967890123', role: 'receptionist', status: 'active', createdAt: '2026-06-22' },
            { id: 'TK008', name: 'Bùi Thị H', email: 'bacsi.h@medbooking.com', phone: '0978901234', role: 'doctor', status: 'active', createdAt: '2026-07-01' }
        ],
        specialties: [
            { id: 'CK001', name: 'Tim mạch', desc: 'Khám và điều trị các bệnh về tim mạch, huyết áp', doctorCount: 3 },
            { id: 'CK002', name: 'Nha khoa', desc: 'Khám, điều trị răng miệng, nhổ răng, trồng răng implant', doctorCount: 2 },
            { id: 'CK003', name: 'Mắt', desc: 'Khám và điều trị các bệnh về mắt, đo thị lực', doctorCount: 2 },
            { id: 'CK004', name: 'Nội tổng quát', desc: 'Khám tổng quát, tầm soát sức khỏe định kỳ', doctorCount: 4 },
            { id: 'CK005', name: 'Da liễu', desc: 'Khám và điều trị các bệnh về da, thẩm mỹ da', doctorCount: 2 },
            { id: 'CK006', name: 'Tai Mũi Họng', desc: 'Khám và điều trị các bệnh về tai mũi họng', doctorCount: 3 }
        ],
        doctors: [
            { id: 'BS001', name: 'BS. Nguyễn Văn A', specialtyId: 'CK001', specialtyName: 'Tim mạch', email: 'bacsi.a@medbooking.com', phone: '0901111111', status: 'available', rating: 4.9 },
            { id: 'BS002', name: 'BS. Trần Thị B', specialtyId: 'CK002', specialtyName: 'Nha khoa', email: 'bacsi.b@medbooking.com', phone: '0902222222', status: 'available', rating: 4.8 },
            { id: 'BS003', name: 'BS. Lê Văn C', specialtyId: 'CK001', specialtyName: 'Tim mạch', email: 'bacsi.c@medbooking.com', phone: '0903333333', status: 'available', rating: 4.7 },
            { id: 'BS004', name: 'BS. Phạm Thị D', specialtyId: 'CK003', specialtyName: 'Mắt', email: 'bacsi.d@medbooking.com', phone: '0904444444', status: 'available', rating: 4.9 },
            { id: 'BS005', name: 'BS. Hoàng Văn E', specialtyId: 'CK004', specialtyName: 'Nội tổng quát', email: 'bacsi.e@medbooking.com', phone: '0905555555', status: 'off', rating: 4.6 },
            { id: 'BS006', name: 'BS. Vũ Thị F', specialtyId: 'CK005', specialtyName: 'Da liễu', email: 'bacsi.f@medbooking.com', phone: '0906666666', status: 'available', rating: 4.8 },
            { id: 'BS007', name: 'BS. Đặng Văn G', specialtyId: 'CK006', specialtyName: 'Tai Mũi Họng', email: 'bacsi.g@medbooking.com', phone: '0907777777', status: 'available', rating: 4.5 },
            { id: 'BS008', name: 'BS. Bùi Thị H', specialtyId: 'CK004', specialtyName: 'Nội tổng quát', email: 'bacsi.h@medbooking.com', phone: '0908888888', status: 'available', rating: 4.9 }
        ],
        services: [
            { id: 'DV001', name: 'Khám tim mạch tổng quát', specialtyId: 'CK001', specialtyName: 'Tim mạch', price: 500000, desc: 'Khám, đo huyết áp, điện tim' },
            { id: 'DV002', name: 'Siêu âm tim', specialtyId: 'CK001', specialtyName: 'Tim mạch', price: 650000, desc: 'Siêu âm tim Doppler màu' },
            { id: 'DV003', name: 'Nhổ răng khôn', specialtyId: 'CK002', specialtyName: 'Nha khoa', price: 1200000, desc: 'Nhổ răng khôn có gây tê' },
            { id: 'DV004', name: 'Trám răng', specialtyId: 'CK002', specialtyName: 'Nha khoa', price: 300000, desc: 'Trám răng sâu composite' },
            { id: 'DV005', name: 'Khám mắt tổng quát', specialtyId: 'CK003', specialtyName: 'Mắt', price: 320000, desc: 'Đo thị lực, soi đáy mắt' },
            { id: 'DV006', name: 'Khám tổng quát', specialtyId: 'CK004', specialtyName: 'Nội tổng quát', price: 450000, desc: 'Khám lâm sàng toàn diện' },
            { id: 'DV007', name: 'Xét nghiệm máu', specialtyId: 'CK004', specialtyName: 'Nội tổng quát', price: 280000, desc: 'Tổng phân tích tế bào máu' },
            { id: 'DV008', name: 'Điều trị mụn', specialtyId: 'CK005', specialtyName: 'Da liễu', price: 800000, desc: 'Điều trị mụn chuyên sâu' },
            { id: 'DV009', name: 'Nội soi tai mũi họng', specialtyId: 'CK006', specialtyName: 'Tai Mũi Họng', price: 380000, desc: 'Nội soi ống mềm' }
        ],
        mappings: [
            { id: 'MP001', keywords: 'đau ngực, khó thở, tim đập nhanh', specialtyId: 'CK001', specialtyName: 'Tim mạch', doctorId: 'BS001', doctorName: 'BS. Nguyễn Văn A', priority: 1 },
            { id: 'MP002', keywords: 'đau răng, sưng nướu, ê buốt', specialtyId: 'CK002', specialtyName: 'Nha khoa', doctorId: 'BS002', doctorName: 'BS. Trần Thị B', priority: 2 },
            { id: 'MP003', keywords: 'mờ mắt, đau mắt, chảy nước mắt', specialtyId: 'CK003', specialtyName: 'Mắt', doctorId: 'BS004', doctorName: 'BS. Phạm Thị D', priority: 1 },
            { id: 'MP004', keywords: 'mệt mỏi, chóng mặt, đau đầu', specialtyId: 'CK004', specialtyName: 'Nội tổng quát', doctorId: '', doctorName: '', priority: 3 },
            { id: 'MP005', keywords: 'mụn, ngứa da, nổi mẩn', specialtyId: 'CK005', specialtyName: 'Da liễu', doctorId: 'BS006', doctorName: 'BS. Vũ Thị F', priority: 2 }
        ],
        recycleBin: [
            { id: 'BS992', type: 'Bác sĩ', name: 'BS. Lê Văn Xóa', deletedAt: '2026-10-05 08:00' },
            { id: 'TK899', type: 'Tài khoản', name: 'Nguyễn Thị Xóa', deletedAt: '2026-10-06 14:30' },
            { id: 'CK880', type: 'Chuyên khoa', name: 'Chuyên khoa cũ', deletedAt: '2026-10-07 09:15' },
            { id: 'DV770', type: 'Dịch vụ', name: 'Dịch vụ khai trương', deletedAt: '2026-10-08 11:00' }
        ],
        transactions: [
            { id: 'GD001', date: '2026-10-14', patient: 'Nguyễn Văn A', revenue: 450000, profit: 180000, doctorConfirm: 'BS. Nguyễn Văn A', receptionConfirm: 'Lễ tân C', updatedAt: '2026-10-14 10:42', status: 'completed' },
            { id: 'GD002', date: '2026-10-14', patient: 'Trần Thị B', revenue: 1200000, profit: 500000, doctorConfirm: 'BS. Trần Thị B', receptionConfirm: 'Lễ tân G', updatedAt: '2026-10-14 09:21', status: 'completed' },
            { id: 'GD003', date: '2026-10-14', patient: 'Lê Văn C', revenue: 650000, profit: 250000, doctorConfirm: 'BS. Lê Văn C', receptionConfirm: 'Lễ tân C', updatedAt: '2026-10-14 08:15', status: 'completed' },
            { id: 'GD004', date: '2026-10-13', patient: 'Phạm Thị D', revenue: 320000, profit: 120000, doctorConfirm: 'BS. Phạm Thị D', receptionConfirm: 'Lễ tân G', updatedAt: '2026-10-13 16:20', status: 'completed' },
            { id: 'GD005', date: '2026-10-13', patient: 'Hoàng Văn E', revenue: 500000, profit: 0, doctorConfirm: '', receptionConfirm: '', updatedAt: '2026-10-13 15:00', status: 'cancelled' },
            { id: 'GD006', date: '2026-10-12', patient: 'Vũ Thị F', revenue: 800000, profit: 320000, doctorConfirm: 'BS. Vũ Thị F', receptionConfirm: 'Lễ tân C', updatedAt: '2026-10-12 14:30', status: 'completed' },
            { id: 'GD007', date: '2026-10-12', patient: 'Đặng Văn G', revenue: 380000, profit: 140000, doctorConfirm: 'BS. Đặng Văn G', receptionConfirm: 'Lễ tân G', updatedAt: '2026-10-12 11:15', status: 'completed' },
            { id: 'GD008', date: '2026-10-11', patient: 'Bùi Thị H', revenue: 280000, profit: 100000, doctorConfirm: 'BS. Bùi Thị H', receptionConfirm: 'Lễ tân C', updatedAt: '2026-10-11 10:00', status: 'completed' }
        ],
        notifications: [
            { id: 'N001', title: 'Lịch hẹn mới', message: 'Bệnh nhân Nguyễn Văn A vừa đặt lịch khám Tim mạch', time: '5 phút trước', read: false },
            { id: 'N002', title: 'Thanh toán thành công', message: 'Giao dịch GD002 đã hoàn tất 1.200.000₫', time: '1 giờ trước', read: false },
            { id: 'N003', title: 'Cảnh báo hệ thống', message: 'Có 3 bản ghi trong thùng rác cần xử lý', time: '2 giờ trước', read: false },
            { id: 'N004', title: 'Đánh giá mới', message: 'BS. Phạm Thị D vừa nhận đánh giá 5 sao', time: '1 ngày trước', read: true }
        ],
    };

    function loadDB() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) {
                console.log('[admin-data.js] Chưa có DB → seed mới');
                localStorage.setItem(STORAGE_KEY, JSON.stringify(seedData));
                return JSON.parse(JSON.stringify(seedData));
            }
            const db = JSON.parse(raw);
            let changed = false;
            for (const k of Object.keys(seedData)) {
                if (!db[k]) { db[k] = JSON.parse(JSON.stringify(seedData[k])); changed = true; }
            }
            if (changed) {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
            }
            console.log('[admin-data.js] Đã load DB:', Object.keys(db).map(k => k + '=' + (Array.isArray(db[k]) ? db[k].length : 'obj')).join(', '));
            return db;
        } catch (e) {
            console.error('[admin-data.js] Lỗi load, reset seed:', e);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(seedData));
            return JSON.parse(JSON.stringify(seedData));
        }
    }

    function saveDB(db) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
        } catch (e) {
            console.error('[admin-data.js] Save DB lỗi:', e);
        }
    }

    let DB = loadDB();

    function nextId(prefix, list) {
        const nums = list.map(item => parseInt((item.id || '').replace(prefix, ''), 10)).filter(n => !isNaN(n));
        const next = (nums.length ? Math.max(...nums) : 0) + 1;
        return prefix + String(next).padStart(3, '0');
    }

    function formatMoney(n) {
        return new Intl.NumberFormat('vi-VN').format(n) + ' ₫';
    }

    function formatDate(iso) {
        if (!iso) return '';
        return new Date(iso).toLocaleDateString('vi-VN');
    }

    const mockAPI = {
        /* ACCOUNTS */
        getAccounts(filters = {}) {
            let list = [...DB.accounts];
            if (filters.role && filters.role !== 'all') list = list.filter(a => a.role === filters.role);
            if (filters.status && filters.status !== 'all') list = list.filter(a => a.status === filters.status);
            if (filters.search) {
                const q = filters.search.toLowerCase();
                list = list.filter(a => a.name.toLowerCase().includes(q) || a.email.toLowerCase().includes(q) || a.phone.includes(q));
            }
            return Promise.resolve({ data: list, total: list.length });
        },
        createAccount(data) {
            const acc = { id: nextId('TK', DB.accounts), ...data, status: 'active', createdAt: new Date().toISOString().slice(0, 10) };
            DB.accounts.unshift(acc);
            DB.notifications.unshift({
                id: 'N' + String(Date.now()).slice(-6),
                title: 'Tài khoản mới',
                message: `Đã tạo tài khoản "${acc.name}" với vai trò ${acc.role}`,
                time: 'Vừa xong',
                read: false
            });
            saveDB(DB);
            return Promise.resolve({ data: acc });
        },
        updateAccount(id, data) {
            const i = DB.accounts.findIndex(a => a.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            DB.accounts[i] = { ...DB.accounts[i], ...data };
            saveDB(DB);
            return Promise.resolve({ data: DB.accounts[i] });
        },
        deleteAccount(id) {
            const i = DB.accounts.findIndex(a => a.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const acc = DB.accounts[i];
            DB.accounts.splice(i, 1);
            DB.recycleBin.unshift({ id: acc.id, type: 'Tài khoản', name: acc.name, deletedAt: new Date().toLocaleString('vi-VN') });
            DB.notifications.unshift({
                id: 'N' + String(Date.now()).slice(-6),
                title: 'Cảnh báo hệ thống',
                message: `Tài khoản "${acc.name}" đã được chuyển vào thùng rác`,
                time: 'Vừa xong',
                read: false
            });
            saveDB(DB);
            return Promise.resolve({ data: true });
        },
        toggleAccountStatus(id, reason) {
            const acc = DB.accounts.find(a => a.id === id);
            if (!acc) return Promise.reject({ message: 'Không tìm thấy' });
            acc.status = acc.status === 'active' ? 'locked' : 'active';
            if (reason) acc.lockReason = reason;
            saveDB(DB);
            return Promise.resolve({ data: acc });
        },

        /* DOCTORS */
        getDoctors(filters = {}) {
            let list = [...DB.doctors];
            if (filters.specialtyId && filters.specialtyId !== 'all') list = list.filter(d => d.specialtyId === filters.specialtyId);
            if (filters.search) {
                const q = filters.search.toLowerCase();
                list = list.filter(d => d.name.toLowerCase().includes(q) || d.email.toLowerCase().includes(q));
            }
            return Promise.resolve({ data: list, total: list.length });
        },
        createDoctor(data) {
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            const doc = { id: nextId('BS', DB.doctors), ...data, specialtyName: spec ? spec.name : '', status: 'available', rating: 5.0 };
            DB.doctors.unshift(doc);
            if (spec) spec.doctorCount = (spec.doctorCount || 0) + 1;
            DB.notifications.unshift({
                id: 'N' + String(Date.now()).slice(-6),
                title: 'Bác sĩ mới',
                message: `Đã thêm ${doc.name} vào chuyên khoa ${doc.specialtyName}`,
                time: 'Vừa xong',
                read: false
            });
            saveDB(DB);
            return Promise.resolve({ data: doc });
        },
        updateDoctor(id, data) {
            const i = DB.doctors.findIndex(d => d.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            DB.doctors[i] = { ...DB.doctors[i], ...data, specialtyName: spec ? spec.name : DB.doctors[i].specialtyName };
            saveDB(DB);
            return Promise.resolve({ data: DB.doctors[i] });
        },
        deleteDoctor(id) {
            const i = DB.doctors.findIndex(d => d.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const doc = DB.doctors[i];
            DB.doctors.splice(i, 1);
            DB.recycleBin.unshift({ id: doc.id, type: 'Bác sĩ', name: doc.name, deletedAt: new Date().toLocaleString('vi-VN') });
            saveDB(DB);
            return Promise.resolve({ data: true });
        },

        /* SPECIALTIES */
        getSpecialties(filters = {}) {
            let list = [...DB.specialties];
            if (filters.search) {
                const q = filters.search.toLowerCase();
                list = list.filter(s => s.name.toLowerCase().includes(q));
            }
            return Promise.resolve({ data: list, total: list.length });
        },
        createSpecialty(data) {
            const spec = { id: nextId('CK', DB.specialties), ...data, doctorCount: 0 };
            DB.specialties.unshift(spec);
            saveDB(DB);
            return Promise.resolve({ data: spec });
        },
        updateSpecialty(id, data) {
            const i = DB.specialties.findIndex(s => s.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            DB.specialties[i] = { ...DB.specialties[i], ...data };
            saveDB(DB);
            return Promise.resolve({ data: DB.specialties[i] });
        },
        deleteSpecialty(id) {
            const i = DB.specialties.findIndex(s => s.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const spec = DB.specialties[i];
            DB.specialties.splice(i, 1);
            DB.recycleBin.unshift({ id: spec.id, type: 'Chuyên khoa', name: spec.name, deletedAt: new Date().toLocaleString('vi-VN') });
            saveDB(DB);
            return Promise.resolve({ data: true });
        },

        /* SERVICES */
        getServices(filters = {}) {
            let list = [...DB.services];
            if (filters.specialtyId && filters.specialtyId !== 'all') list = list.filter(s => s.specialtyId === filters.specialtyId);
            if (filters.search) {
                const q = filters.search.toLowerCase();
                list = list.filter(s => s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q));
            }
            return Promise.resolve({ data: list, total: list.length });
        },
        createService(data) {
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            const serv = { id: nextId('DV', DB.services), ...data, specialtyName: spec ? spec.name : '' };
            DB.services.unshift(serv);
            saveDB(DB);
            return Promise.resolve({ data: serv });
        },
        updateService(id, data) {
            const i = DB.services.findIndex(s => s.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            DB.services[i] = { ...DB.services[i], ...data, specialtyName: spec ? spec.name : DB.services[i].specialtyName };
            saveDB(DB);
            return Promise.resolve({ data: DB.services[i] });
        },
        deleteService(id) {
            const i = DB.services.findIndex(s => s.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const serv = DB.services[i];
            DB.services.splice(i, 1);
            DB.recycleBin.unshift({ id: serv.id, type: 'Dịch vụ', name: serv.name, deletedAt: new Date().toLocaleString('vi-VN') });
            saveDB(DB);
            return Promise.resolve({ data: true });
        },

        /* MAPPINGS */
        getMappings(filters = {}) {
            let list = [...DB.mappings];
            if (filters.specialtyId && filters.specialtyId !== 'all') list = list.filter(m => m.specialtyId === filters.specialtyId);
            if (filters.search) {
                const q = filters.search.toLowerCase();
                list = list.filter(m => m.keywords.toLowerCase().includes(q));
            }
            return Promise.resolve({ data: list, total: list.length });
        },
        createMapping(data) {
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            const doc = data.doctorId ? DB.doctors.find(d => d.id === data.doctorId) : null;
            const map = { id: nextId('MP', DB.mappings), ...data, specialtyName: spec ? spec.name : '', doctorName: doc ? doc.name : '' };
            DB.mappings.unshift(map);
            saveDB(DB);
            return Promise.resolve({ data: map });
        },
        updateMapping(id, data) {
            const i = DB.mappings.findIndex(m => m.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const spec = DB.specialties.find(s => s.id === data.specialtyId);
            const doc = data.doctorId ? DB.doctors.find(d => d.id === data.doctorId) : null;
            DB.mappings[i] = { ...DB.mappings[i], ...data, specialtyName: spec ? spec.name : '', doctorName: doc ? doc.name : '' };
            saveDB(DB);
            return Promise.resolve({ data: DB.mappings[i] });
        },
        deleteMapping(id) {
            const i = DB.mappings.findIndex(m => m.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            DB.mappings.splice(i, 1);
            saveDB(DB);
            return Promise.resolve({ data: true });
        },

        /* RECYCLE BIN */
        getRecycleBin() { return Promise.resolve({ data: [...DB.recycleBin] }); },
        restoreItem(id) {
            const i = DB.recycleBin.findIndex(r => r.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            const item = DB.recycleBin[i];
            DB.recycleBin.splice(i, 1);
            DB.notifications.unshift({
                id: 'N' + String(Date.now()).slice(-6),
                title: 'Khôi phục thành công',
                message: `Đã khôi phục "${item.name}" (${item.type})`,
                time: 'Vừa xong',
                read: false
            });
            saveDB(DB);
            return Promise.resolve({ data: true });
        },
        deleteItemForever(id) {
            const i = DB.recycleBin.findIndex(r => r.id === id);
            if (i === -1) return Promise.reject({ message: 'Không tìm thấy' });
            DB.recycleBin.splice(i, 1);
            saveDB(DB);
            return Promise.resolve({ data: true });
        },
        emptyRecycleBin() {
            DB.recycleBin = [];
            saveDB(DB);
            return Promise.resolve({ data: true });
        },

        /* TRANSACTIONS */
        getTransactions(filters = {}) {
            let list = [...DB.transactions];
            if (filters.year) list = list.filter(t => t.date.startsWith(filters.year));
            if (filters.month && filters.month !== 'all') {
                list = list.filter(t => parseInt(t.date.split('-')[1], 10) === parseInt(filters.month, 10));
            }
            if (filters.status && filters.status !== 'all') list = list.filter(t => t.status === filters.status);
            return Promise.resolve({ data: list, total: list.length });
        },

        /* DASHBOARD */
        getDashboardStats(year, quarter) {
            let list = [...DB.transactions];
            if (year) list = list.filter(t => t.date.startsWith(String(year)));
            if (quarter && quarter !== 'all') {
                const q = parseInt(quarter.replace('Q', ''), 10);
                const from = (q - 1) * 3 + 1, to = from + 2;
                list = list.filter(t => {
                    const m = parseInt(t.date.split('-')[1], 10);
                    return m >= from && m <= to;
                });
            }
            const totalAppointments = list.length;
            const totalRevenue = list.filter(t => t.status === 'completed').reduce((s, t) => s + t.revenue, 0);
            const totalProfit = list.filter(t => t.status === 'completed').reduce((s, t) => s + t.profit, 0);
            const cancelled = list.filter(t => t.status === 'cancelled').length;
            const cancelRate = totalAppointments ? ((cancelled / totalAppointments) * 100).toFixed(1) : 0;
            const topDoctor = [...DB.doctors].sort((a, b) => b.rating - a.rating)[0];
            return Promise.resolve({
                data: {
                    totalAppointments, totalRevenue, totalProfit, cancelRate,
                    topDoctor: topDoctor ? { name: topDoctor.name, rating: topDoctor.rating } : null,
                    revenueByMonth: [
                        { label: 'T2', value: 12, prev: 8 }, { label: 'T3', value: 19, prev: 14 },
                        { label: 'T4', value: 15, prev: 10 }, { label: 'T5', value: 27, prev: 18 },
                        { label: 'T6', value: 24, prev: 15 }, { label: 'T7', value: 32, prev: 22 },
                        { label: 'CN', value: 22, prev: 16 }
                    ]
                }
            });
        },

        /* NOTIFICATIONS */
        getNotifications() { return Promise.resolve({ data: [...DB.notifications] }); },
        markAllRead() {
            DB.notifications.forEach(n => n.read = true);
            saveDB(DB);
            return Promise.resolve({ data: true });
        },
        pushNotification(notif) {
            const newNotif = {
                id: 'N' + String(Date.now()).slice(-6),
                title: notif.title || 'Thông báo mới',
                message: notif.message || '',
                time: 'Vừa xong',
                read: false
            };
            DB.notifications.unshift(newNotif);
            if (DB.notifications.length > 20) DB.notifications = DB.notifications.slice(0, 20);
            saveDB(DB);
            return Promise.resolve({ data: newNotif });
        },

        /* CURRENT USER */
        getCurrentUser() {
            const loggedInUser = localStorage.getItem('medbooking_logged_in_user');
            if (loggedInUser) {
                try {
                    const userData = JSON.parse(loggedInUser);
                    return Promise.resolve({
                        data: {
                            id: userData.id || userData.ma_quan_tri || 'AD001',
                            ma_quan_tri: userData.id || userData.ma_quan_tri || 'AD001',
                            name: userData.name || userData.ho_ten || DB.currentUser.name,
                            ho_ten: userData.name || userData.ho_ten || DB.currentUser.name,
                            email: userData.email || DB.currentUser.email,
                            avatar: (userData.name || userData.ho_ten || 'A').charAt(0).toUpperCase()
                        }
                    });
                } catch (e) {}
            }
            return Promise.resolve({ data: { ...DB.currentUser } });
        },
        updateCurrentUser(data) {
            DB.currentUser = { ...DB.currentUser, ...data };
            saveDB(DB);
            return Promise.resolve({ data: DB.currentUser });
        },

        /* RESET */
        resetAll() {
            localStorage.removeItem(STORAGE_KEY);
            DB = loadDB();
            return Promise.resolve({ data: true });
        }
    };

    global.MedBookingAPI = mockAPI;
    global.MedBookingUtils = { formatMoney, formatDate };
    console.log('[admin-data.js] ✅ Đã export MedBookingAPI');

})(window);