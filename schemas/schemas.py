from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ==================== NGƯỜI DÙNG (USER) ====================
class NguoiDungBase(BaseModel):
    email: EmailStr
    ho_ten: str = Field(..., min_length=2, max_length=100)
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    vai_tro: str = Field(default="benh_nhan")
    trang_thai: bool = Field(default=True)  # Khớp kiểu bool với model NguoiDung
    ngay_sinh: Optional[date] = Field(None, description="Ngày sinh không được là ngày hôm nay hoặc tương lai")

    @field_validator("ngay_sinh")
    @classmethod
    def validate_ngay_sinh(cls, value: Optional[date]) -> Optional[date]:
        """Ràng buộc: Ngày sinh không được là ngày hôm nay hoặc trong tương lai."""
        if value and value >= date.today():
            raise ValueError("Ngày sinh không hợp lệ (không được là ngày hôm nay hoặc trong tương lai).")
        return value


class NguoiDungCreate(NguoiDungBase):
    mat_khau: str = Field(..., min_length=8)


class NguoiDungUpdate(BaseModel):
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100)
    so_dien_thoai: Optional[str] = None
    trang_thai: Optional[bool] = None


class NguoiDungResponse(NguoiDungBase):
    id: int  # Khớp với cột id chính của bảng nguoi_dung

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    mat_khau_cu: str
    mat_khau_moi: str = Field(..., min_length=8, description="Mật khẩu mới ít nhất 8 ký tự")


# ==================== BỆNH NHÂN ====================
class BenhNhanBase(BaseModel):
    ngay_sinh: Optional[date] = None
    gioitinh: Optional[str] = Field(None, alias="gioi_tinh")  # Hỗ trợ tương thích ngược với model
    dia_chi: Optional[str] = None
    tid_su_benh: Optional[str] = Field(None, alias="tien_su_benh")

    @field_validator("ngay_sinh")
    @classmethod
    def validate_ngay_sinh(cls, value: Optional[date]) -> Optional[date]:
        if value and value >= date.today():
            raise ValueError("Ngày sinh không hợp lệ (không được là ngày hôm nay hoặc trong tương lai).")
        return value


class BenhNhanCreate(BenhNhanBase):
    nguoi_dung_id: int  # Khớp với khóa ngoại nguoi_dung_id trong model BenhNhan


class BenhNhanUpdate(BenhNhanBase):
    pass


class BenhNhanResponse(BenhNhanBase):
    id: int  # Khớp với id chính của benh_nhan
    nguoi_dung_id: int
    user: Optional[NguoiDungResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== CHUYÊN KHOA ====================
class ChuyenKhoaBase(BaseModel):
    ten_chuyen_khoa: str = Field(..., min_length=2, max_length=100)
    mo_ta: Optional[str] = None


class ChuyenKhoaCreate(ChuyenKhoaBase):
    pass


class ChuyenKhoaUpdate(BaseModel):
    ten_chuyen_khoa: Optional[str] = None
    mo_ta: Optional[str] = None


class ChuyenKhoaResponse(ChuyenKhoaBase):
    id: int  # Khớp với id chính của chuyên khoa

    class Config:
        from_attributes = True


# ==================== DỊCH VỤ ====================
class DichVuBase(BaseModel):
    chuyen_khoa_id: int
    ten_dich_vu: str = Field(..., min_length=2, max_length=100)
    gia_tien: Decimal = Field(..., ge=0, alias="gia_dich_vu")  # Khớp với gia_tien trong model DichVu
    mo_ta: Optional[str] = None
    dang_hoat_dong: bool = True


class DichVuCreate(DichVuBase):
    pass


class DichVuUpdate(BaseModel):
    ten_dich_vu: Optional[str] = None
    gia_tien: Optional[Decimal] = Field(None, ge=0)
    mo_ta: Optional[str] = None
    dang_hoat_dong: Optional[bool] = None


class DichVuResponse(DichVuBase):
    id: int  # Khớp với id của dịch vụ

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== HÓA ĐƠN / THANH TOÁN ====================
class HoaDonBase(BaseModel):
    lich_hen_id: int  # Khớp với model ThanhToan
    tong_tien: Decimal = Field(..., ge=0)
    phuong_thuc: Optional[str] = None
    trang_thai_thanh_toan: str = Field(default="Chưa thanh toán", alias="trang_thai")


class HoaDonCreate(HoaDonBase):
    pass


class HoaDonResponse(HoaDonBase):
    id: int  # Khớp với id của bảng thanh_toan
    ngay_thanh_toan: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True