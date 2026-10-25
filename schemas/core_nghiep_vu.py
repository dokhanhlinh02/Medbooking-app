from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# --- Core Schemas ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    mat_khau: str = Field(min_length=6, description="Mật khẩu ít nhất 6 ký tự")
    ho_ten: str
    so_dien_thoai: Optional[str] = None
    vai_tro: str = Field(default="benh_nhan", description="benh_nhan, bac_si, le_tan, admin")
    ngay_sinh: Optional[date] = Field(None, description="Ngày sinh không được là ngày hôm nay hoặc tương lai")

    @field_validator("ngay_sinh")
    @classmethod
    def validate_ngay_sinh(cls, value: Optional[date]) -> Optional[date]:
        """Ràng buộc: Ngày sinh không được là ngày hôm nay hoặc trong tương lai."""
        if value and value >= date.today():
            raise ValueError("Ngày sinh không hợp lệ (không được là ngày hôm nay hoặc trong tương lai).")
        return value


class UserLoginRequest(BaseModel):
    email: EmailStr
    mat_khau: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    ho_ten: str
    vai_tro: str


class ChangePasswordRequest(BaseModel):
    mat_khau_cu: str
    mat_khau_moi: str = Field(min_length=6, description="Mật khẩu mới ít nhất 6 ký tự")


# --- Nghiệp vụ Schemas ---
class BookingCreateRequest(BaseModel):
    bac_si_id: int = Field(..., description="ID của bác sĩ (khớp với model)")
    dich_vu_id: int = Field(..., description="ID của dịch vụ khám")
    ngay_kham: date
    khung_gio: str = Field(..., description="Khung giờ khám (VD: 08:00 - 09:00)")
    ghi_chu: Optional[str] = None


class UpdateTrangThaiRequest(BaseModel):
    trang_thai_moi: str = Field(description="Pending, Confirmed, DaDen, In Progress, Completed, Cancelled")
    ghi_chu: Optional[str] = None


class ThanhToanRequest(BaseModel):
    phuong_thuc: str = Field(default="TienMat", description="TienMat, ChuyenKhoan, The")
    ghi_chu: Optional[str] = None