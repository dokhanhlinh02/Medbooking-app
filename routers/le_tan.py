import importlib
from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung
from models.lich_hen import LichHen, LogTrangThai, LichLamViec  # [cite: 3]
from models.bac_si import BacSi  # [cite: 5]

import auth as root_auth

router = APIRouter(prefix="/appointments", tags=["Quản lý Lịch hẹn"])


class BookingRequest(BaseModel):
    bac_si_id: int
    dich_vu_id: int
    ngay_kham: date
    khung_gio: str
    ghi_chu: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    trang_thai_moi: str
    ghi_chu: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED, summary="Bệnh nhân đặt lịch khám mới")
def create_appointment(
        payload: BookingRequest,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.get_current_user)
):
    benh_nhan = current_user.benh_nhan_profile
    if not benh_nhan:
        raise HTTPException(status_code=400, detail="Tài khoản hiện tại chưa có hồ sơ bệnh nhân.")

    doctor = db.query(BacSi).filter(BacSi.id == payload.bac_si_id).first()  # [cite: 5]
    if not doctor:
        raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại.")

    # --- LOẠI 3: Kiểm tra Bác sĩ nghỉ, không có lịch trực, hoặc slot đã bị disable (con_trong = False)[cite: 3] ---
    lich_truc = db.query(LichLamViec).filter(
        LichLamViec.bac_si_id == payload.bac_si_id,
        LichLamViec.ngay_kham == payload.ngay_kham,
        LichLamViec.khung_gio == payload.khung_gio,
        LichLamViec.con_trong == True
    ).first()

    if not lich_truc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[Loại 3] Bác sĩ không có lịch làm việc, đã nghỉ, hoặc khung giờ này đã đóng (Slot disabled)."
        )

    # --- LOẠI 2: Kiểm tra Bác sĩ trùng lịch (Đã có bệnh nhân khác đặt slot này)[cite: 3] ---
    bs_trung_lich = db.query(LichHen).filter(
        LichHen.bac_si_id == payload.bac_si_id,
        LichHen.ngay_kham == payload.ngay_kham,
        LichHen.khung_gio == payload.khung_gio,
        LichHen.trang_thai.notin_(["Cancelled", "Đã hủy"])
    ).first()

    if bs_trung_lich:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[Loại 2] Bác sĩ đã có lịch hẹn khác vào khung giờ này."
        )

    # --- LOẠI 1: Kiểm tra Bệnh nhân trùng lịch với chính mình[cite: 3] ---
    bn_trung_lich = db.query(LichHen).filter(
        LichHen.benh_nhan_id == benh_nhan.id,
        LichHen.ngay_kham == payload.ngay_kham,
        LichHen.khung_gio == payload.khung_gio,
        LichHen.trang_thai.notin_(["Cancelled", "Đã hủy"])
    ).first()

    if bn_trung_lich:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="[Loại 1] Bạn đã có một lịch hẹn khác trùng vào ngày và khung giờ này."
        )

    # --- TẠO LỊCH HẸN & KHÓA SLOT (Slot Disable)[cite: 3] ---
    appt = LichHen(
        benh_nhan_id=benh_nhan.id,
        bac_si_id=payload.bac_si_id,
        dich_vu_id=payload.dich_vu_id,
        ngay_kham=payload.ngay_kham,
        khung_gio=payload.khung_gio,
        trang_thai="Chờ xác nhận",
        ghi_chu=payload.ghi_chu or ""
    )

    db.add(appt)
    db.flush()

    # Cập nhật trạng thái slot thành False để disable[cite: 3]
    lich_truc.con_trong = False

    # Đã bỏ tham số ghi_chu để khớp hoàn toàn với định nghĩa model LogTrangThai[cite: 3]
    log = LogTrangThai(
        lich_hen_id=appt.id,  # [cite: 3]
        trang_thai_cu="",
        trang_thai_moi="Chờ xác nhận",
        thoi_gian=datetime.now(timezone.utc),
        nguoi_thuc_hien=current_user.ho_ten
    )
    db.add(log)
    db.commit()
    db.refresh(appt)

    return {"message": "Đặt lịch khám thành công.", "ma_lich_hen": appt.id}


@router.get("", summary="Xem danh sách lịch hẹn (Sắp xếp: Ngày giảm dần, Giờ tăng dần)")
def get_appointments(
        status_filter: Optional[str] = Query(None, description="Chờ xác nhận, Confirmed, Completed, Cancelled..."),
        ngay: Optional[date] = Query(None, description="Lọc theo ngày khám"),
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.get_current_user)
):
    query = db.query(LichHen)

    if current_user.vai_tro == "benh_nhan":
        if current_user.benh_nhan_profile:
            query = query.filter(LichHen.benh_nhan_id == current_user.benh_nhan_profile.id)
        else:
            return []
    elif current_user.vai_tro == "bac_si":
        doc_profile = db.query(BacSi).filter(BacSi.nguoi_dung_id == current_user.id).first()  # [cite: 5]
        if doc_profile:
            query = query.filter(LichHen.bac_si_id == doc_profile.id)
        else:
            return []

    if status_filter:
        query = query.filter(LichHen.trang_thai == status_filter)
    if ngay:
        query = query.filter(LichHen.ngay_kham == ngay)

    # Sắp xếp chuẩn: ngay_kham giảm dần (desc), khung_gio tăng dần (asc)[cite: 3]
    return query.order_by(LichHen.ngay_kham.desc(), LichHen.khung_gio.asc()).all()


@router.put("/{ma_lich_hen}/status", summary="Cập nhật trạng thái lịch hẹn kèm ghi log hệ thống")
def update_appointment_status(
        ma_lich_hen: int,
        payload: UpdateStatusRequest,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.get_current_user)
):
    appt = db.query(LichHen).filter(LichHen.id == ma_lich_hen).first()  # [cite: 3]
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn tương ứng.")

    old_status = str(appt.trang_thai)
    appt.trang_thai = payload.trang_thai_moi

    # Đã bỏ tham số ghi_chu để khớp với model LogTrangThai[cite: 3]
    log = LogTrangThai(
        lich_hen_id=appt.id,  # [cite: 3]
        trang_thai_cu=old_status,
        trang_thai_moi=payload.trang_thai_moi,
        thoi_gian=datetime.now(timezone.utc),
        nguoi_thuc_hien=current_user.ho_ten
    )
    db.add(log)
    db.commit()

    return {
        "message": "Cập nhật trạng thái thành công.",
        "ma_lich_hen": ma_lich_hen,
        "trang_thai": payload.trang_thai_moi
    }