from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class LeTanBase(BaseModel):
    quay_lam_viec: Optional[str] = Field(None, max_length=50)
    ca_truc: Optional[str] = Field(None, max_length=50)


class LeTanCreate(LeTanBase):
    ma_le_tan: int


class LeTanResponse(LeTanBase):
    ma_le_tan: int
    ngay_vao_lam: datetime

    class Config:
        from_attributes = True


# Schema cho thao tác đổi ca/khung giờ của Lễ tân
class RescheduleRequest(BaseModel):
    ngay_moi: date
    khung_gio_moi: str = Field(..., description="Khung giờ mới (VD: 08:00 - 09:00)")


# Schema hiển thị bảng check-in tại quầy
class CheckInRecordResponse(BaseModel):
    ma_lich_hen: int
    benh_nhan: str
    ma_bhyt: Optional[str] = None
    ngay_kham: date
    khung_gio: str
    bac_si: str
    chuyen_khoa: Optional[str] = None
    trang_thai: str

    class Config:
        from_attributes = True