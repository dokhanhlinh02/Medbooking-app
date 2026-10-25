import importlib
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung
from services.admin_service import AdminService

import auth as root_auth

router = APIRouter(prefix="/admin", tags=["Phân hệ Admin"])


class ChuyenKhoaCreateRequest(BaseModel):
    ten_chuyen_khoa: str
    mo_ta: Optional[str] = None


class DichVuCreateRequest(BaseModel):
    chuyen_khoa_id: int = Field(..., description="ID chuyên khoa trực thuộc dịch vụ")
    ten_dich_vu: str
    gia_dich_vu: Decimal = Field(..., description="Giá tiền dịch vụ")
    mo_ta: Optional[str] = None


@router.get("/dashboard-stats", summary="Thống kê doanh thu, lợi nhuận theo kỳ và chi tiết giao dịch")
def get_dashboard_quarterly_stats(
    year: int = Query(2026, description="Năm thống kê"),
    quarter: Optional[str] = Query(None, description="Q1, Q2, Q3, Q4 hoặc để trống để xem cả năm"),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    _ = current_user
    return AdminService.get_quarterly_dashboard(db=db, year=year, quarter=quarter)


@router.get("/users", summary="Danh sách người dùng theo vai trò")
def list_users(
    role: Optional[str] = Query(None, description="benh_nhan, bac_si, le_tan, admin"),
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    _ = current_user
    users = AdminService.get_users(db=db, vai_tro=role)
    return [
        {
            "user_id": u.id,  # Khớp với cột id chính của bảng nguoi_dung
            "email": u.email,
            "ho_ten": u.ho_ten,
            "so_dien_thoai": u.so_dien_thoai,
            "vai_tro": u.vai_tro,
            "trang_thai": 1 if u.trang_thai else 0  # Chuyển đổi boolean thành int/status tương thích
        }
        for u in users
    ]


@router.put("/users/{user_id}/toggle-status", summary="Khóa / Mở khóa tài khoản")
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    _ = current_user
    return AdminService.toggle_user_status(db=db, user_id=user_id)


@router.post("/specialties", summary="Thêm mới chuyên khoa khám")
def add_specialty(
    payload: ChuyenKhoaCreateRequest,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    _ = current_user
    ck = AdminService.create_chuyen_khoa(db=db, ten=payload.ten_chuyen_khoa, mo_ta=payload.mo_ta)
    return {"message": "Tạo chuyên khoa thành công.", "ma_chuyen_khoa": ck.id}  # Khớp với id của chuyên khoa


@router.post("/services", summary="Thêm dịch vụ & bảng giá")
def add_service(
    payload: DichVuCreateRequest,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(root_auth.require_role(["admin"]))
):
    _ = current_user
    dv = AdminService.create_dich_vu(
        db=db,
        chuyen_khoa_id=payload.chuyen_khoa_id,
        ten=payload.ten_dich_vu,
        gia=payload.gia_dich_vu,
        mo_ta=payload.mo_ta
    )
    return {"message": "Tạo dịch vụ thành công.", "ma_dich_vu": dv.id}  # Khớp với id của dịch vụ