
/**
 * LT_Store.js - Lễ Tân Store
 * Quản lý dữ liệu localStorage cho module Lễ Tân
 * Prefix: medbooking_
 */

(function () {
    'use strict';

    const PREFIX = 'medbooking_';

    const KEYS = {
        APPOINTMENTS: PREFIX + 'appointments',
        PAYMENTS: PREFIX + 'payments',
        CHECKINS: PREFIX + 'checkins',
        INITIALIZED: PREFIX + 'initialized'
    };

    // Lấy ngày theo múi giờ địa phương, tránh lệch ngày do UTC.
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');

        return `${year}-${month}-${day}`;
    }

    function todayStr() {
        return formatDate(new Date());
    }

    function tomorrowStr() {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        return formatDate(date);
    }

    // Đọc dữ liệu từ localStorage.
    function readJSON(key, fallback) {
        try {
            const raw = localStorage.getItem(key);

            if (!raw) {
                return fallback;
            }

            return JSON.parse(raw);
        } catch (error) {
            console.error('LT_Store read error:', key, error);
            return fallback;
        }
    }

    // Ghi dữ liệu vào localStorage.
    function writeJSON(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('LT_Store write error:', key, error);
            return false;
        }
    }

    // Dữ liệu mẫu ban đầu.
    function seedAppointments() {
        const today = todayStr();
        const tomorrow = tomorrowStr();

        return [
            {
                id: 'LH101',
                patientName: 'Nguyễn Văn X',
                patientId: 'BN001',
                phone: '0912345678',
                doctor: 'ThS.BS Nguyễn Văn A',
                doctorId: 'bs01',
                specialty: 'Tim mạch',
                ca: 'sang',
                time: '08:30-09:30',
                date: today,
                symptom: 'Đau ngực, khó thở khi vận động',
                status: 'pending',
                items: [
                    {
                        name: 'Phí khám Tim mạch',
                        qty: 1,
                        price: 200000
                    },
                    {
                        name: 'Điện tâm đồ (ECG)',
                        qty: 1,
                        price: 150000
                    }
                ]
            },
            {
                id: 'LH102',
                patientName: 'Trần Thị B',
                patientId: 'BN002',
                phone: '0912345679',
                doctor: 'BS.CKI Trần Thị C',
                doctorId: 'bs02',
                specialty: 'Nội tổng quát',
                ca: 'chieu',
                time: '14:30-15:30',
                date: today,
                symptom: 'Sốt cao 3 ngày, mệt mỏi',
                status: 'confirmed',
                items: [
                    {
                        name: 'Phí khám Nội tổng quát',
                        qty: 1,
                        price: 180000
                    },
                    {
                        name: 'Xét nghiệm máu',
                        qty: 1,
                        price: 250000
                    },
                    {
                        name: 'X-quang ngực',
                        qty: 1,
                        price: 200000
                    }
                ]
            },
            {
                id: 'LH103',
                patientName: 'Lê Thị M',
                patientId: 'BN003',
                phone: '0912345680',
                doctor: 'BS.CKI Trần Thị C',
                doctorId: 'bs02',
                specialty: 'Nội tổng quát',
                ca: 'sang',
                time: '09:30-10:30',
                date: today,
                symptom: 'Đau bụng, buồn nôn',
                status: 'checked',
                items: [
                    {
                        name: 'Phí khám Nội tổng quát',
                        qty: 1,
                        price: 180000
                    },
                    {
                        name: 'Siêu âm bụng',
                        qty: 1,
                        price: 300000
                    }
                ]
            },
            {
                id: 'LH104',
                patientName: 'Phạm Văn K',
                patientId: 'BN004',
                phone: '0912345681',
                doctor: 'TS.BS Lê Hoàng D',
                doctorId: 'bs03',
                specialty: 'Thần kinh',
                ca: 'toi',
                time: '18:30-19:30',
                date: today,
                symptom: 'Đau đầu kéo dài, mất ngủ',
                status: 'checked',
                items: [
                    {
                        name: 'Phí khám Thần kinh (ngoài giờ)',
                        qty: 1,
                        price: 330000
                    },
                    {
                        name: 'Chụp CT sọ não',
                        qty: 1,
                        price: 800000
                    }
                ]
            },
            {
                id: 'LH105',
                patientName: 'Hoàng Thị N',
                patientId: 'BN005',
                phone: '0912345682',
                doctor: 'ThS.BS Nguyễn Văn A',
                doctorId: 'bs01',
                specialty: 'Tim mạch',
                ca: 'sang',
                time: '10:30-11:30',
                date: tomorrow,
                symptom: 'Tái khám định kỳ',
                status: 'confirmed',
                items: [
                    {
                        name: 'Phí khám Tim mạch',
                        qty: 1,
                        price: 200000
                    }
                ]
            },
            {
                id: 'LH106',
                patientName: 'Vũ Đức P',
                patientId: 'BN006',
                phone: '0912345683',
                doctor: 'BS.CKI Trần Thị C',
                doctorId: 'bs02',
                specialty: 'Nội tổng quát',
                ca: 'chieu',
                time: '15:30-16:30',
                date: today,
                symptom: 'Ho khan, đau họng',
                status: 'pending',
                items: [
                    {
                        name: 'Phí khám Nội tổng quát',
                        qty: 1,
                        price: 180000
                    },
                    {
                        name: 'Test Covid',
                        qty: 1,
                        price: 100000
                    }
                ]
            }
        ];
    }

    // Dữ liệu bổ sung cho ngày 15/10/2026.
    function getExtraAppointments() {
        return [
            {
                id: 'LH107',
                patientName: 'Đỗ Minh Anh',
                patientId: 'BN007',
                phone: '0912345684',
                doctor: 'ThS.BS Nguyễn Văn A',
                doctorId: 'bs01',
                specialty: 'Tim mạch',
                ca: 'sang',
                time: '07:30-08:30',
                date: '2026-10-15',
                symptom: 'Khám sức khỏe định kỳ',
                status: 'confirmed',
                items: [
                    {
                        name: 'Phí khám Tim mạch',
                        qty: 1,
                        price: 200000
                    }
                ]
            },
            {
                id: 'LH108',
                patientName: 'Nguyễn Thu Hà',
                patientId: 'BN008',
                phone: '0912345685',
                doctor: 'BS.CKI Trần Thị C',
                doctorId: 'bs02',
                specialty: 'Nội tổng quát',
                ca: 'chieu',
                time: '13:30-14:30',
                date: '2026-10-15',
                symptom: 'Đau họng, ho nhẹ',
                status: 'pending',
                items: [
                    {
                        name: 'Phí khám Nội tổng quát',
                        qty: 1,
                        price: 180000
                    }
                ]
            },
            {
                id: 'LH109',
                patientName: 'Trần Quốc Bảo',
                patientId: 'BN009',
                phone: '0912345686',
                doctor: 'TS.BS Lê Hoàng D',
                doctorId: 'bs03',
                specialty: 'Thần kinh',
                ca: 'toi',
                time: '19:30-20:30',
                date: '2026-10-15',
                symptom: 'Đau đầu, chóng mặt',
                status: 'confirmed',
                items: [
                    {
                        name: 'Phí khám Thần kinh (ngoài giờ)',
                        qty: 1,
                        price: 330000
                    }
                ]
            }
        ];
    }

    // Khởi tạo và cập nhật dữ liệu mẫu.
    function initIfNeeded() {
        if (!localStorage.getItem(KEYS.INITIALIZED)) {
            writeJSON(KEYS.APPOINTMENTS, seedAppointments());
            writeJSON(KEYS.PAYMENTS, []);
            writeJSON(KEYS.CHECKINS, []);

            localStorage.setItem(KEYS.INITIALIZED, '1');
        }

        const appointments = readJSON(KEYS.APPOINTMENTS, []);

        // Chuyển lịch hẹn mẫu sang ngày 15/10/2026.
        // LH105 được giữ ở ngày 16/10/2026.
        const demoDates = {
            LH101: '2026-10-15',
            LH102: '2026-10-15',
            LH103: '2026-10-15',
            LH104: '2026-10-15',
            LH105: '2026-10-16',
            LH106: '2026-10-15'
        };

        appointments.forEach(appointment => {
            if (demoDates[appointment.id]) {
                appointment.date = demoDates[appointment.id];
            }
        });

        // Chỉ thêm lịch hẹn nếu mã lịch chưa tồn tại.
        const extraAppointments = getExtraAppointments();
        const existingIds = new Set(
            appointments.map(appointment => appointment.id)
        );

        extraAppointments.forEach(appointment => {
            if (!existingIds.has(appointment.id)) {
                appointments.push(appointment);
                existingIds.add(appointment.id);
            }
        });

        writeJSON(KEYS.APPOINTMENTS, appointments);
    }

    const LT_Store = {
        // Lấy danh sách lịch hẹn.
        getAppointments() {
            initIfNeeded();
            return readJSON(KEYS.APPOINTMENTS, []);
        },

        // Lấy lịch hẹn theo mã.
        getAppointmentById(id) {
            const appointments = this.getAppointments();

            return appointments.find(
                appointment => appointment.id === id
            ) || null;
        },

        // Cập nhật trạng thái lịch hẹn.
        updateAppointmentStatus(id, newStatus, reason) {
            const appointments = this.getAppointments();

            const index = appointments.findIndex(
                appointment => appointment.id === id
            );

            if (index === -1) {
                return {
                    success: false,
                    error: 'Không tìm thấy lịch hẹn'
                };
            }

            const oldStatus = appointments[index].status;

            appointments[index].status = newStatus;
            appointments[index].statusUpdatedAt =
                new Date().toISOString();
            appointments[index].statusReason = reason || '';

            const saved = writeJSON(KEYS.APPOINTMENTS, appointments);

            if (!saved) {
                return {
                    success: false,
                    error: 'Không thể lưu trạng thái lịch hẹn'
                };
            }

            return {
                success: true,
                oldStatus,
                newStatus
            };
        },

        // Đổi khung giờ khám.
        changeAppointmentTime(id, newTime, newCa) {
            const appointments = this.getAppointments();

            const index = appointments.findIndex(
                appointment => appointment.id === id
            );

            if (index === -1) {
                return {
                    success: false,
                    error: 'Không tìm thấy lịch hẹn'
                };
            }

            appointments[index].time = newTime;
            appointments[index].ca = newCa;
            appointments[index].timeUpdatedAt =
                new Date().toISOString();

            const saved = writeJSON(KEYS.APPOINTMENTS, appointments);

            if (!saved) {
                return {
                    success: false,
                    error: 'Không thể lưu khung giờ mới'
                };
            }

            return { success: true };
        },

        // Kiểm tra khung giờ của bác sĩ có còn trống không.
        isSlotAvailable(doctorId, date, timeSlot, excludeApptId) {
            const appointments = this.getAppointments();

            return !appointments.some(appointment =>
                appointment.id !== excludeApptId &&
                appointment.doctorId === doctorId &&
                appointment.date === date &&
                appointment.time === timeSlot &&
                appointment.status !== 'cancelled' &&
                appointment.status !== 'noshow'
            );
        },

        // Tạo dữ liệu check-in.
        createCheckin(data) {
            const checkins = readJSON(KEYS.CHECKINS, []);

            const checkin = {
                id: 'CI' + Date.now(),
                appointmentId: data.appointmentId,
                patientId: data.patientId,
                cashierId: data.cashierId,
                cashierName: data.cashierName,
                vitals: data.vitals || {},
                checkedAt: new Date().toISOString()
            };

            checkins.push(checkin);

            const saved = writeJSON(KEYS.CHECKINS, checkins);

            if (!saved) {
                return {
                    success: false,
                    error: 'Không thể lưu thông tin check-in'
                };
            }

            const statusResult = this.updateAppointmentStatus(
                data.appointmentId,
                'checked',
                'Check-in tại quầy'
            );

            if (!statusResult.success) {
                return statusResult;
            }

            return {
                success: true,
                checkin
            };
        },

        // Lấy danh sách check-in.
        getCheckins() {
            return readJSON(KEYS.CHECKINS, []);
        },

        // Lấy danh sách giao dịch thanh toán.
        getPayments() {
            return readJSON(KEYS.PAYMENTS, []);
        },

        // Thêm giao dịch thanh toán.
        addPayment(transaction) {
            const payments = this.getPayments();

            payments.push(transaction);

            const saved = writeJSON(KEYS.PAYMENTS, payments);

            return {
                success: saved
            };
        },

        // Tạo hóa đơn thanh toán.
        createPayment(data) {
            if (!data || !data.appointmentId) {
                return {
                    success: false,
                    message: 'Thiếu mã lịch hẹn'
                };
            }

            if (this.isAlreadyPaid(data.appointmentId)) {
                return {
                    success: false,
                    message: 'Hóa đơn đã được thu rồi'
                };
            }

            const payments = this.getPayments();
            const now = new Date();
            const year = now.getFullYear();

            const payment = {
                id: 'PM' + Date.now(),
                invoiceId: data.invoiceId ||
                    ('HD-' + year + '-' +
                    data.appointmentId.replace('LH', '')),
                appointmentId: data.appointmentId,
                patientId: data.patientId || null,
                patientName: data.patientName || '',
                doctorId: data.doctorId || null,
                doctorName: data.doctorName || '',
                specialty: data.specialty || '',
                ca: data.ca || '',
                date: data.date || todayStr(),
                items: Array.isArray(data.items) ? data.items : [],
                totalAmount: parseInt(data.totalAmount, 10) || 0,
                paymentMethod: data.paymentMethod || 'cash',
                cashierId: data.cashierId || null,
                cashierName: data.cashierName || '',
                paidAt: now.toISOString(),
                createdAt: now.toISOString()
            };

            payments.push(payment);

            const saved = writeJSON(KEYS.PAYMENTS, payments);

            if (!saved) {
                return {
                    success: false,
                    message: 'Không thể lưu giao dịch vào hệ thống'
                };
            }

            return {
                success: true,
                payment
            };
        },

        // Giữ tương thích với các trang đang sử dụng hàm này.
        markAsPaid(appointmentId) {
            return { success: true };
        },

        // Kiểm tra lịch hẹn đã thanh toán chưa.
        isAlreadyPaid(appointmentId) {
            const payments = this.getPayments();

            return payments.some(
                payment => payment.appointmentId === appointmentId
            );
        },

        // Thống kê lịch hẹn và doanh thu trong ngày hiện tại.
        getDashboardStats() {
            const appointments = this.getAppointments();
            const payments = this.getPayments();
            const today = todayStr();

            const todayAppointments = appointments.filter(
                appointment => appointment.date === today
            );

            const byCa = {
                sang: todayAppointments.filter(
                    appointment => appointment.ca === 'sang'
                ).length,

                chieu: todayAppointments.filter(
                    appointment => appointment.ca === 'chieu'
                ).length,

                toi: todayAppointments.filter(
                    appointment => appointment.ca === 'toi'
                ).length
            };

            const todayPayments = payments.filter(payment => {
                if (!payment.paidAt) {
                    return false;
                }

                return formatDate(new Date(payment.paidAt)) === today;
            });

            const revenueToday = todayPayments.reduce(
                (sum, payment) =>
                    sum + (parseInt(payment.totalAmount, 10) || 0),
                0
            );

            return {
                totalToday: todayAppointments.length,

                checkedIn: todayAppointments.filter(
                    appointment => appointment.status === 'checked'
                ).length,

                pending: todayAppointments.filter(
                    appointment => appointment.status === 'pending'
                ).length,

                confirmed: todayAppointments.filter(
                    appointment => appointment.status === 'confirmed'
                ).length,

                cancelled: todayAppointments.filter(
                    appointment => appointment.status === 'cancelled'
                ).length,

                noshow: todayAppointments.filter(
                    appointment => appointment.status === 'noshow'
                ).length,

                revenueToday,
                byCa
            };
        },

        // Xử lý lịch hẹn chưa đến khám khi đã qua ngày.
        processOvernightAppointments() {
            const appointments = this.getAppointments();
            const today = todayStr();
            const changed = [];

            appointments.forEach(appointment => {
                if (
                    appointment.date < today &&
                    (
                        appointment.status === 'pending' ||
                        appointment.status === 'confirmed'
                    )
                ) {
                    appointment.status = 'noshow';
                    appointment.statusUpdatedAt =
                        new Date().toISOString();
                    appointment.statusReason = 'Tự động: Qua ngày';

                    changed.push(appointment.id);
                }
            });

            if (changed.length > 0) {
                writeJSON(KEYS.APPOINTMENTS, appointments);
            }

            return changed;
        },

        // Xóa dữ liệu localStorage của module và tạo lại dữ liệu mẫu.
        reset() {
            Object.values(KEYS).forEach(key => {
                localStorage.removeItem(key);
            });

            initIfNeeded();
        }
    };

    // Cho phép các trang HTML khác sử dụng LT_Store.
    window.LT_Store = LT_Store;

    // Khởi tạo dữ liệu khi tải file.
    initIfNeeded();

    console.log('LT_Store.js loaded');
})();