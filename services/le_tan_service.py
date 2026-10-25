from datetime import date, datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.lich_hen import LichHen, LogTrangThai

class LeTanService:

    @staticmethod
    def _format_appointment(a: LichHen) -> Dict[str, Any]:
        """Hàm dùng chung format dữ liệu hiển thị lịch hẹn"""
        return {
            "ma_lich_hen": a.id,
            "benh_nhan": a.benh_nhan.user.ho_ten if (a.benh_nhan and a.benh_nhan.user) else "",
            "ma_bhyt": getattr(a, "ma_bhyt", "") or "",  # Dùng getattr để tránh cảnh báo Unresolved attribute trên IDE
            "ngay_kham": a.ngay_kham,
            "khung_gio": a.khung_gio,
            "bac_si": a.bac_si.user.ho_ten if (a.bac_si and a.bac_si.user) else "",
            "chuyen_khoa": a.bac_si.chuyen_khoa.ten_chuyen_khoa if (a.bac_si and a.bac_si.chuyen_khoa) else "",
            "trang_thai": a.trang_thai
        }

    @classmethod
    def get_daily_checkin_list(cls, db: Session, ngay: Optional[date] = None) -> List[Dict[str, Any]]:
        search_date = ngay or date.today()
        # Sắp xếp theo ngày khám giảm dần, khung giờ tăng dần
        appointments = db.query(LichHen).filter(
            LichHen.ngay_kham == search_date,
            LichHen.trang_thai.in_(["Chờ xác nhận", "Pending", "Confirmed"])
        ).order_by(LichHen.ngay_kham.desc(), LichHen.khung_gio.asc()).all()

        return [cls._format_appointment(a) for a in appointments]

    @staticmethod
    def confirm_checkin(db: Session, ma_lich_hen: int, receptionist_name: str) -> Dict[str, Any]:
        appt = db.query(LichHen).filter(LichHen.id == ma_lich_hen).first()
        if not appt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch hẹn.")

        old_status = str(appt.trang_thai)
        appt.trang_thai = "DaDen"

        log = LogTrangThai(
            lich_hen_id=appt.id,
            trang_thai_cu=old_status,
            trang_thai_moi="DaDen",
            thoi_gian=datetime.now(timezone.utc),
            nguoi_thuc_hien=receptionist_name
        )
        db.add(log)
        db.commit()
        return {"message": "Xác nhận check-in thành công.", "ma_lich_hen": ma_lich_hen, "trang_thai": "DaDen"}

    @staticmethod
    def reschedule_appointment(
        db: Session,
        ma_lich_hen: int,
        ngay_moi: date,
        khung_gio_moi: str,
        receptionist_name: str
    ) -> Dict[str, Any]:
        appt = db.query(LichHen).filter(LichHen.id == ma_lich_hen).first()
        if not appt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch hẹn.")

        if appt.trang_thai in ["Completed", "Cancelled", "Đã hoàn thành", "Đã hủy"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể đổi lịch hẹn đã kết thúc hoặc đã hủy.")

        # Kiểm tra trùng lịch bác sĩ (Loại 2)
        conflict = db.query(LichHen).filter(
            LichHen.bac_si_id == appt.bac_si_id,
            LichHen.ngay_kham == ngay_moi,
            LichHen.khung_gio == khung_gio_moi,
            LichHen.id != ma_lich_hen,
            LichHen.trang_thai.notin_(["Cancelled", "Đã hủy"])
        ).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khung giờ mới này bác sĩ đã có lịch hẹn khác.")

        appt.ngay_kham = ngay_moi
        appt.khung_gio = khung_gio_moi

        log = LogTrangThai(
            lich_hen_id=appt.id,
            trang_thai_cu=str(appt.trang_thai),
            trang_thai_moi=str(appt.trang_thai),
            thoi_gian=datetime.now(timezone.utc),
            nguoi_thuc_hien=receptionist_name
        )
        db.add(log)
        db.commit()
        return {"message": "Đã đổi lịch hẹn thành công."}