import importlib
from datetime import datetime, date, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung, DichVu, HoaDon, BenhNhan
from models.bac_si import BacSi
from models.lich_hen import LichHen, LogTrangThai
from schemas.core_nghiep_vu import BookingCreateRequest, UpdateTrangThaiRequest, ThanhToanRequest
from services.bac_si_service import BacSiService
from services.lich_hen_service import LichHenService
from schemas.lich_hen import BookingRequest

import auth as root_auth

router = APIRouter(tags=["2. Backend Nghiệp vụ - Phòng khám"])


def _format_appointment_item(a: LichHen) -> dict:
    appt_id = getattr(a, "id", None) or getattr(a, "ma_lich_hen", None)
    time_val = getattr(a, "khung_gio", None) or getattr(a, "gio_kham", None) or ""

    patient_name = ""
    if hasattr(a, "benh_nhan") and a.benh_nhan:
        patient_name = getattr(a.benh_nhan.user, "ho_ten", "") if hasattr(a.benh_nhan,
                                                                          "user") and a.benh_nhan.user else ""

    doctor_name = ""
    if hasattr(a, "bac_si") and a.bac_si:
        doctor_name = getattr(a.bac_si.user, "ho_ten", "") if hasattr(a.bac_si, "user") and a.bac_si.user else ""

    return {
        "ma_lich_hen": appt_id,
        "ngay_kham": str(a.ngay_kham),
        "khung_gio": str(time_val),
        "benh_nhan": patient_name,
        "bac_si": doctor_name,
        "trang_thai": a.trang_thai,
    }


# --- API bac-si & API bac-si/{id} ---
@router.get("/bac-si", summary="Danh sách bác sĩ & tìm kiếm")
def get_doctors(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=50),
        keyword: Optional[str] = None,
        chuyen_khoa_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user: Optional[NguoiDung] = Depends(root_auth.get_optional_current_user),
):
    is_admin = bool(current_user and current_user.vai_tro == "admin")
    return BacSiService.get_paginated_doctors(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        chuyen_khoa_id=chuyen_khoa_id,
        is_admin=is_admin,
    )


@router.get("/bac-si/{doctor_id}", summary="Chi tiết hồ sơ một bác sĩ")
def get_doctor_detail(
        doctor_id: int,
        db: Session = Depends(get_db),
        current_user: Optional[NguoiDung] = Depends(root_auth.get_optional_current_user),
):
    is_admin = bool(current_user and current_user.vai_tro == "admin")
    doc = BacSiService.get_doctor_by_id(db=db, doctor_id=doctor_id, is_admin=is_admin)
    return {
        "ma_bac_si": doc.id,
        "ho_ten": doc.user.ho_ten if (hasattr(doc, "user") and doc.user) else "",
        "hoc_vi": getattr(doc, "hoc_vi", "") or "",
        "gia_kham": float(getattr(doc, "gia_kham", 0) or 0),
        "rating": float(getattr(doc, "rating", 0.0) or 0.0),
        "chuyen_khoa": doc.chuyen_khoa.ten_chuyen_khoa if (hasattr(doc, "chuyen_khoa") and doc.chuyen_khoa) else "",
    }


# --- API dich-vu ---
@router.get("/dich-vu", summary="Bảng giá danh mục dịch vụ")
def get_services(db: Session = Depends(get_db)):
    services = db.query(DichVu).all()
    return [
        {
            "ma_dich_vu": getattr(s, "id", None) or getattr(s, "ma_dich_vu", None),
            "ten_dich_vu": s.ten_dich_vu,
            "gia": float(getattr(s, "gia", None) or getattr(s, "gia_dich_vu", 0) or 0),
            "mo_ta": getattr(s, "mo_ta", ""),
        }
        for s in services
    ]


# --- API POST/GET lich-hen ---
@router.post("/lich-hen", summary="Bệnh nhân đặt lịch hẹn")
def create_appointment(
        payload: BookingCreateRequest,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.require_role(["benh_nhan", "admin", "le_tan"])),
):
    # Khớp đúng các trường bac_si_id, dich_vu_id, khung_gio từ BookingCreateRequest sang BookingRequest
    book_schema = BookingRequest(
        bac_si_id=getattr(payload, "bac_si_id", None) or getattr(payload, "ma_bac_si", 1),
        dich_vu_id=getattr(payload, "dich_vu_id", 1),
        ngay_kham=payload.ngay_kham,
        khung_gio=getattr(payload, "khung_gio", None) or getattr(payload, "gio_kham", "08:00 - 09:00"),
        ghi_chu=getattr(payload, "ghi_chu", None),
    )
    appt = LichHenService.create_appointment(
        db=db, data=book_schema, patient_id=current_user.id
    )
    appt_id = getattr(appt, "id", None) or getattr(appt, "ma_lich_hen", None)
    return {
        "message": "Đặt lịch hẹn thành công.",
        "ma_lich_hen": appt_id,
        "trang_thai": appt.trang_thai,
    }


@router.get("/lich-hen", summary="Tra cứu danh sách lịch hẹn")
def list_appointments(
        ngay: Optional[date] = None,
        trang_thai: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.get_current_user),
):
    query = db.query(LichHen)
    role = getattr(current_user, "vai_tro", "")
    u_id = getattr(current_user, "id", 0)

    if role == "benh_nhan":
        patient = db.query(BenhNhan).filter(BenhNhan.nguoi_dung_id == u_id).first()
        p_id = patient.id if patient else u_id
        query = query.filter(LichHen.benh_nhan_id == p_id)
    elif role == "bac_si":
        doctor = db.query(BacSi).filter(BacSi.nguoi_dung_id == u_id).first()
        d_id = doctor.id if doctor else u_id
        query = query.filter(LichHen.bac_si_id == d_id)

    if ngay:
        query = query.filter(LichHen.ngay_kham == ngay)
    if trang_thai:
        query = query.filter(LichHen.trang_thai == trang_thai)

    appts = query.order_by(LichHen.ngay_kham.desc(), LichHen.id.desc()).all()
    return [_format_appointment_item(a) for a in appts]


# --- API PUT trang-thai & Log trạng thái ---
@router.put("/lich-hen/{ma_lich_hen}/trang-thai", summary="Chuyển trạng thái ca khám & Ghi audit log")
def update_status(
        ma_lich_hen: int,
        payload: UpdateTrangThaiRequest,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.require_role(["bac_si", "le_tan", "admin"])),
):
    appt = LichHenService.update_status(
        db=db,
        ma_lich_hen=ma_lich_hen,
        trang_thai_moi=payload.trang_thai_moi,
        user_id=current_user.id,
    )
    appt_id = getattr(appt, "id", None) or getattr(appt, "ma_lich_hen", None)
    return {
        "message": "Cập nhật thành công.",
        "ma_lich_hen": appt_id,
        "trang_thai": appt.trang_thai,
    }


# --- API thanh-toan ---
@router.post("/thanh-toan/{ma_lich_hen}", summary="Xác nhận thanh toán viện phí")
def process_payment(
        ma_lich_hen: int,
        payload: ThanhToanRequest,
        db: Session = Depends(get_db),
        current_user: NguoiDung = Depends(root_auth.require_role(["le_tan", "admin"])),
):
    bill = db.query(HoaDon).filter(
        (HoaDon.lich_hen_id == ma_lich_hen) if hasattr(HoaDon, "lich_hen_id") else (HoaDon.ma_lich_hen == ma_lich_hen)
    ).first()

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hóa đơn của ca khám này.",
        )

    # Sử dụng payload để khắc phục cảnh báo "Parameter payload value is not used"
    if hasattr(bill, "phuong_thuc") and payload.phuong_thuc:
        bill.phuong_thuc = payload.phuong_thuc

    current_status = getattr(bill, "trang_thai", None) or getattr(bill, "trang_thai_thanh_toan", "Chưa thanh toán")
    if current_status in ["Da Thanh Toan", "Đã thanh toán"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hóa đơn đã được thanh toán.",
        )

    if hasattr(bill, "trang_thai"):
        bill.trang_thai = "Da Thanh Toan"
    elif hasattr(bill, "trang_thai_thanh_toan"):
        bill.trang_thai_thanh_toan = "Da Thanh Toan"

    staff_name = current_user.ho_ten if current_user else "Hệ thống"

    log = LogTrangThai(
        lich_hen_id=ma_lich_hen,
        trang_thai_cu="ChuaThanhToan",
        trang_thai_moi="DaThanhToan",
        thoi_gian=datetime.now(timezone.utc),
        nguoi_thuc_hien=staff_name,
    )
    db.add(log)

    db.commit()
    bill_id = getattr(bill, "id", None) or getattr(bill, "ma_hoa_don", None)
    return {
        "message": f"Thanh toán thành công qua {payload.phuong_thuc}. {payload.ghi_chu or ''}",
        "ma_hoa_don": bill_id,
        "tong_tien": float(getattr(bill, "tong_tien", 0.0) or 0.0),
    }


# noinspection SqlNoDataSourceInspection
@router.get("/trieu-chung", summary="Danh sách triệu chứng theo chuyên khoa")
def get_symptoms(chuyen_khoa_id: Optional[int] = None, db: Session = Depends(get_db)):
    from sqlalchemy import text
    if chuyen_khoa_id:
        sql = text("SELECT id, ten_trieu_chung, chuyen_khoa_id FROM trieu_chung WHERE chuyen_khoa_id = :ck_id")
        rows = db.execute(sql, {"ck_id": chuyen_khoa_id}).fetchall()
    else:
        sql = text("SELECT id, ten_trieu_chung, chuyen_khoa_id FROM trieu_chung")
        rows = db.execute(sql).fetchall()

    return [{"id": r[0], "ten_trieu_chung": r[1], "chuyen_khoa_id": r[2]} for r in rows]