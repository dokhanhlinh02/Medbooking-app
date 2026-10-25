import importlib
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung
from models.bac_si import BacSi
from models.lich_hen import LichHen
from schemas.bac_si import (
    BacSiCreate,
    BacSiUpdate,
    BacSiResponse,
    BacSiPaginationResponse
)

from services.bac_si_service import BacSiService

# Nạp module auth từ thư mục gốc
import auth as root_auth

router = APIRouter(prefix="/doctors", tags=["Quản lý Bác sĩ"])

@router.post(
    "",
    response_model=BacSiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm mới Bác sĩ & Dị bản (Admin only)"
)
def create_doctor(
    payload: BacSiCreate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    doctor = BacSiService.create_doctor(db=db, data=payload, current_user=current_user)
    paginated_res = BacSiService.get_paginated_doctors(
        db=db, page=1, page_size=1, keyword=doctor.user.email, is_admin=True
    )
    return paginated_res["items"][0]


@router.get(
    "",
    response_model=BacSiPaginationResponse,
    summary="Tìm kiếm, Lọc, Sắp xếp & Phân trang danh sách Bác sĩ"
)
def get_doctors(
    page: int = Query(1, ge=1, description="Số thứ tự trang"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    keyword: Optional[str] = Query(None, description="Tìm theo tên, email, sđt"),
    chuyen_khoa_id: Optional[int] = Query(None, description="Lọc theo ID chuyên khoa"),
    hoc_vi: Optional[str] = Query(None, description="Lọc theo học vị (Thạc sĩ, CKI...)"),
    min_price: Optional[float] = Query(None, ge=0, description="Giá khám tối thiểu"),
    max_price: Optional[float] = Query(None, ge=0, description="Giá khám tối đa"),
    doctor_status: Optional[int] = Query(None, description="Trạng thái (1: Hoạt động, 0: Đã ẩn)"),
    sort_by: str = Query("created_at", description="created_at, updated_at, ten, rating, gia_kham"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Chiều sắp xếp: asc hoặc desc"),  # Đã đổi regex thành pattern
    db: Session = Depends(get_db),
    current_user: Optional[NguoiDung] = Depends(root_auth.get_optional_current_user)
):
    is_admin = bool(current_user and current_user.vai_tro == "admin")

    patient_specialties: List[int] = []
    if current_user and current_user.vai_tro == "benh_nhan":
        history = db.query(LichHen.bac_si_id).filter(
            LichHen.benh_nhan_id == current_user.id
        ).all()
        doc_ids = [h[0] for h in history if h[0]]
        if doc_ids:
            ck_records = db.query(BacSi.chuyen_khoa_id).filter(BacSi.id.in_(doc_ids)).all()
            patient_specialties = [c[0] for c in ck_records if c[0]]

    return BacSiService.get_paginated_doctors(
        db=db,
        page=page,
        page_size=limit,
        keyword=keyword,
        chuyen_khoa_id=chuyen_khoa_id,
        hoc_vi=hoc_vi,
        min_price=min_price,
        max_price=max_price,
        doctor_status=doctor_status,
        sort_by=sort_by,
        sort_order=order,
        is_admin=is_admin,
        patient_history_specialty_ids=patient_specialties
    )


@router.get(
    "/{doctor_id}",
    response_model=BacSiResponse,
    summary="Xem chi tiết Bác sĩ"
)
def get_doctor_detail(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[NguoiDung] = Depends(root_auth.get_optional_current_user)
):
    is_admin = bool(current_user and current_user.vai_tro == "admin")
    doc = BacSiService.get_doctor_by_id(db, doctor_id, is_admin=is_admin)
    paginated_res = BacSiService.get_paginated_doctors(
        db=db, page=1, page_size=1, keyword=doc.user.email, is_admin=is_admin
    )
    return paginated_res["items"][0]


@router.put(
    "/{doctor_id}",
    response_model=BacSiResponse,
    summary="Chỉnh sửa Bác sĩ & Cập nhật Dị bản (Admin only)"
)
def update_doctor(
    doctor_id: int,
    payload: BacSiUpdate,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    updated_doc = BacSiService.update_doctor(
        db=db, doctor_id=doctor_id, data=payload, current_user=current_user
    )
    paginated_res = BacSiService.get_paginated_doctors(
        db=db, page=1, page_size=1, keyword=updated_doc.user.email, is_admin=True
    )
    return paginated_res["items"][0]


@router.delete(
    "/{doctor_id}",
    summary="Xóa Bác sĩ: Ẩn (Soft) hoặc Vĩnh viễn (Hard) (Admin only)"
)
def delete_doctor(
    doctor_id: int,
    delete_type: str = Query("soft", alias="type", pattern="^(soft|hard)$", description="soft: Ẩn, hard: Xóa vĩnh viễn"),  # Đã đổi regex thành pattern
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    return BacSiService.delete_doctor(
        db=db, doctor_id=doctor_id, delete_type=delete_type, current_user=current_user
    )