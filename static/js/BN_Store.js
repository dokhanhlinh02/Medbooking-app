/* ============================================================
   MEDBOOKING - BN_Store.js
   KHO DỮ LIỆU TẬP TRUNG CHO HỆ THỐNG BỆNH NHÂN
   ============================================================ */

const BN_Store = (function() {
    
    const KEYS = {
        APPOINTMENTS: 'medbooking_bn_appointments',
        INITIALIZED: 'medbooking_bn_initialized'
    };

    // =========================================
    // MOCK DATA BAN ĐẦU
    // =========================================
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const tomorrow = new Date(now); tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    const lastWeek = new Date(now); lastWeek.setDate(lastWeek.getDate() - 7);
    const lastWeekStr = lastWeek.toISOString().split('T')[0];
    const lastMonth = new Date(now); lastMonth.setDate(lastMonth.getDate() - 30);
    const lastMonthStr = lastMonth.toISOString().split('T')[0];

    const INITIAL_APPOINTMENTS = [
        // Lịch sắp tới (pending)
        { 
            id: 'LH00123', 
            date: tomorrowStr, 
            time: '08:30', 
            ca: 'sang',
            doctorId: 'bs01',
            doctor: 'ThS.BS Nguyễn Văn A', 
            specialty: 'Nội Tổng Quát', 
            symptom: 'Đau đầu kéo dài, mệt mỏi', 
            status: 'pending',
            items: [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 },
                { name: 'Xét nghiệm máu cơ bản', qty: 1, price: 150000 }
            ]
        },
        { 
            id: 'LH00124', 
            date: '2026-10-20', 
            time: '14:00', 
            ca: 'chieu',
            doctorId: 'bs02',
            doctor: 'BS.CKI Trần Thị C', 
            specialty: 'Tim Mạch', 
            symptom: 'Khám định kỳ huyết áp', 
            status: 'pending',
            items: [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 }
            ]
        },
        // Lịch sử khám (completed)
        { 
            id: 'LH00098', 
            date: lastWeekStr, 
            time: '14:00', 
            ca: 'chieu',
            doctorId: 'bs02',
            doctor: 'BS.CKI Trần Thị C', 
            specialty: 'Tim Mạch', 
            symptom: 'Đau thắt ngực nhẹ khi vận động', 
            status: 'completed',
            items: [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 },
                { name: 'Điện tâm đồ (ECG)', qty: 1, price: 200000 }
            ]
        },
        { 
            id: 'LH00075', 
            date: lastMonthStr, 
            time: '09:30', 
            ca: 'sang',
            doctorId: 'bs05',
            doctor: 'BS. Nguyễn Thị Nhi', 
            specialty: 'Nhi Khoa', 
            symptom: 'Trẻ sốt cao 3 ngày', 
            status: 'completed',
            items: [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 }
            ]
        },
        // Lịch đã hủy (cancelled)
        { 
            id: 'LH00045', 
            date: '2026-08-15', 
            time: '09:00', 
            ca: 'sang',
            doctorId: 'bs03',
            doctor: 'TS.BS Lê Hoàng D', 
            specialty: 'Thần Kinh', 
            symptom: 'Mất ngủ kinh niên', 
            status: 'cancelled',
            items: [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 }
            ]
        }
    ];

    // =========================================
    // INIT
    // =========================================
    function init() {
        if (!localStorage.getItem(KEYS.INITIALIZED)) {
            localStorage.setItem(KEYS.APPOINTMENTS, JSON.stringify(INITIAL_APPOINTMENTS));
            localStorage.setItem(KEYS.INITIALIZED, 'true');
            console.log('✅ BN_Store: Đã khởi tạo dữ liệu ban đầu');
        }
    }

    // =========================================
    // READ/WRITE
    // =========================================
    function getAppointments() {
        return JSON.parse(localStorage.getItem(KEYS.APPOINTMENTS) || '[]');
    }

    function setAppointments(data) {
        localStorage.setItem(KEYS.APPOINTMENTS, JSON.stringify(data));
    }

    // =========================================
    // API
    // =========================================
    
    // Lấy 1 lịch hẹn
    function getAppointmentById(id) {
        return getAppointments().find(a => a.id === id);
    }

    // Tạo lịch hẹn mới
    function createAppointment(data) {
        const appts = getAppointments();
        
        // Sinh mã LH tự động
        const maxId = appts.reduce((max, a) => {
            const num = parseInt(a.id.replace('LH', ''));
            return num > max ? num : max;
        }, 0);
        const newId = 'LH' + String(maxId + 1).padStart(5, '0');
        
        const appointment = {
            id: newId,
            date: data.date,
            time: data.time_slot || data.time,
            ca: getCaFromTime(data.time_slot || data.time),
            doctorId: data.doctorId,
            doctor: data.doctorName,
            specialty: data.specialtyName,
            symptom: data.symptoms || '',
            status: 'pending',
            items: data.items || [
                { name: 'Tiền khám chuyên khoa', qty: 1, price: 300000 }
            ],
            createdAt: new Date().toISOString()
        };
        
        appts.push(appointment);
        setAppointments(appts);
        return { success: true, appointment };
    }

    // Cập nhật trạng thái
    function updateAppointmentStatus(id, newStatus) {
        const appts = getAppointments();
        const appt = appts.find(a => a.id === id);
        if (!appt) return { success: false };
        
        appt.status = newStatus;
        appt.updatedAt = new Date().toISOString();
        setAppointments(appts);
        return { success: true, appointment: appt };
    }

    // Đổi giờ
    function changeAppointmentTime(id, newTime, newCa) {
        const appts = getAppointments();
        const appt = appts.find(a => a.id === id);
        if (!appt) return { success: false };
        
        appt.time = newTime;
        appt.ca = newCa;
        appt.updatedAt = new Date().toISOString();
        setAppointments(appts);
        return { success: true, appointment: appt };
    }

    // Hủy lịch
    function cancelAppointment(id) {
        return updateAppointmentStatus(id, 'cancelled');
    }

    // Đặt lại lịch
    function rebookAppointment(oldId) {
        const appt = getAppointmentById(oldId);
        if (!appt) return { success: false };
        
        return {
            success: true,
            data: {
                doctorId: appt.doctorId,
                doctorName: appt.doctor,
                specialtyName: appt.specialty,
                symptom: appt.symptom
            }
        };
    }

    // =========================================
    // STATS
    // =========================================
    function getStats() {
        const appts = getAppointments();
        return {
            total: appts.length,
            pending: appts.filter(a => a.status === 'pending').length,
            completed: appts.filter(a => a.status === 'completed').length,
            cancelled: appts.filter(a => a.status === 'cancelled').length
        };
    }

    // =========================================
    // HELPERS
    // =========================================
    function getCaFromTime(timeSlot) {
        const startHour = parseInt(timeSlot.split(':')[0]);
        if (startHour >= 7 && startHour < 12) return 'sang';
        if (startHour >= 13 && startHour < 18) return 'chieu';
        return 'toi';
    }

    // =========================================
    // RESET (cho test)
    // =========================================
    function reset() {
        localStorage.removeItem(KEYS.INITIALIZED);
        localStorage.removeItem(KEYS.APPOINTMENTS);
        init();
        console.log('🔄 BN_Store: Đã reset');
    }

    // =========================================
    // PUBLIC API
    // =========================================
    return {
        init,
        getAppointments,
        getAppointmentById,
        createAppointment,
        updateAppointmentStatus,
        changeAppointmentTime,
        cancelAppointment,
        rebookAppointment,
        getStats,
        reset
    };
})();

// Auto init
BN_Store.init();