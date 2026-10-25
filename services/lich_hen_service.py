from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.lich_hen import LichHen, LogTrangThai
from models.bac_si import BacSi
from models.models import BenhNhan, NguoiDung, ThanhToan as HoaDon
from schemas.lich_hen import BookingRequest

class LichHenService:

    @staticmethod
    def create_appointment(db: Session, data: BookingRequest, patient_id: int) -> LichHen:
        # 1. Tìm bản ghi bệnh nhân từ ID tài khoản đăng nhập (nguoi_dung_id)
        benh_nhan = db.query(BenhNhan).filter(BenhNhan.nguoi_dung_id == patient_id).first()
        if not benh_nhan:
            benh_nhan = db.query(BenhNhan).filter(BenhNhan.id == patient_id).first()

        if not benh_nhan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hồ sơ bệnh nhân cho tài khoản này."
            )

        # 2. Lấy ID bác sĩ (Hỗ trợ cả ma_bac_si hoặc bac_si_id từ payload)
        doc_id = getattr(data, "bac_si_id", None) or getattr(data, "ma_bac_si", None)
        doctor = db.query(BacSi).filter(BacSi.id == doc_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bác sĩ không tồn tại hoặc đã bị ẩn."
            )

        # 3. Chuẩn hóa khung giờ thành String
        raw_slot = getattr(data, "khung_gio", None) or getattr(data, "gio_kham", None) or "08:00 - 09:00"
        time_slot = str(raw_slot)

        # 4. Kiểm tra trùng lịch hẹn theo ngay_kham và khung_gio
        conflict = db.query(LichHen).filter(
            LichHen.bac_si_id == doctor.id,
            LichHen.ngay_kham == data.ngay_kham,
            LichHen.khung_gio == time_slot,
            LichHen.trang_thai.notin_(["Cancelled", "Đã hủy"])
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Khung giờ khám này của bác sĩ đã có bệnh nhân khác đặt."
            )

        # 5. Lấy hoặc gán mặc định dich_vu_id
        selected_service_id = getattr(data, "dich_vu_id", None) or 1

        # 6. Tạo mới bản ghi LichHen
        appt = LichHen(
            benh_nhan_id=benh_nhan.id,
            bac_si_id=doctor.id,
            dich_vu_id=selected_service_id,
            ngay_kham=data.ngay_kham,
            khung_gio=time_slot,
            trang_thai="Chờ xác nhận",
            ghi_chu=getattr(data, "ghi_chu", "") or ""
        )
        db.add(appt)
        db.flush()

        # 7. Khởi tạo hóa đơn thanh toán tương ứng
        try:
            hoa_don = HoaDon(
                lich_hen_id=appt.id,
                tong_tien=getattr(doctor, "gia_kham", Decimal("0.0")) or Decimal("0.0"),
                trang_thai="Chưa thanh toán"
            )
            db.add(hoa_don)
        except Exception:
            pass

        # 8. Ghi log trạng thái chuẩn theo model LogTrangThai (chỉ truyền các trường có sẵn)
        user_obj = db.query(NguoiDung).filter(NguoiDung.id == patient_id).first()
        user_name = user_obj.ho_ten if user_obj else "Bệnh nhân"

        log = LogTrangThai(
            lich_hen_id=appt.id,
            trang_thai_cu="",
            trang_thai_moi="Chờ xác nhận",
            thoi_gian=datetime.now(timezone.utc),
            nguoi_thuc_hien=user_name
        )
        db.add(log)

        db.commit()
        db.refresh(appt)
        return appt

    @staticmethod
    def update_status(
        db: Session,
        ma_lich_hen: int,
        trang_thai_moi: str,
        user_id: int,
        ghi_chu: Optional[str] = None
    ) -> LichHen:
        appt = db.query(LichHen).filter(LichHen.id == ma_lich_hen).first()
        if not appt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy lịch hẹn."
            )

        old_status = str(appt.trang_thai)
        appt.trang_thai = trang_thai_moi

        # Lấy tên người thực hiện từ user_id để ghi log
        user_obj = db.query(NguoiDung).filter(NguoiDung.id == user_id).first()
        user_name = user_obj.ho_ten if user_obj else "Hệ thống"

        log = LogTrangThai(
            lich_hen_id=appt.id,
            trang_thai_cu=old_status,
            trang_thai_moi=trang_thai_moi,
            thoi_gian=datetime.now(timezone.utc),
            nguoi_thuc_hien=user_name
        )
        db.add(log)

        db.commit()
        db.refresh(appt)
        return appt