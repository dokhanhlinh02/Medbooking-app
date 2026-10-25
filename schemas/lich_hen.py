from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Lịch làm việc / Ca khám ---
class LichLamViecBase(BaseModel):
    bac_si_id: int  # Khớp với model LichLamViec
    ngay_kham: date  # Khớp với model LichLamViec
    khung_gio: str   # Khớp với model LichLamViec (chuỗi khung giờ)
    con_trong: bool = True  # Khớp với quản lý slot con_trong


class LichLamViecCreate(LichLamViecBase):
    pass


class LichLamViecResponse(LichLamViecBase):
    id: int  # Khớp với primary key id của LichLamViec

    class Config:
        from_attributes = True


# --- Log trạng thái lịch hẹn ---
class LogTrangThaiResponse(BaseModel):
    id: int
    lich_hen_id: int  # Khớp với model LogTrangThai
    trang_thai_cu: Optional[str] = None
    trang_thai_moi: str
    thoi_gian: datetime
    nguoi_thuc_hien: str  # Khớp với kiểu String của nguoi_thuc_hien trong model LogTrangThai

    class Config:
        from_attributes = True


# --- Đặt lịch & Cập nhật trạng thái ---
class BookingRequest(BaseModel):
    bac_si_id: int
    dich_vu_id: int
    ngay_kham: date
    khung_gio: str  # Khớp định dạng chuỗi khung giờ
    ghi_chu: Optional[str] = None


class UpdateAppointmentStatusRequest(BaseModel):
    trang_thai_moi: str = Field(..., description="Chờ xác nhận, Confirmed, In Progress, Completed, Cancelled, DaDen")
    ghi_chu: Optional[str] = None


class LichHenResponse(BaseModel):
    id: int  # Khớp với id chính của LichHen
    benh_nhan_id: int
    bac_si_id: int
    dich_vu_id: int
    ngay_kham: date
    khung_gio: str
    trang_thai: str
    created_at: Optional[datetime] = None
    ghi_chu: Optional[str] = None
    logs: List[LogTrangThaiResponse] = []

    class Config:
        from_attributes = True

class LichHenCreate(BaseModel):
    benh_nhan_id: int
    ngay_kham: datetime
    trieu_chung: str

class AdminPhanCongSchema(BaseModel):
    bac_si_id: int
    le_tan_id: int