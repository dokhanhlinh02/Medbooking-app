from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class BacSiGoiY(BaseModel):
    """Thông tin bác sĩ gợi ý"""
    id: int
    ho_ten: str
    hoc_vi: Optional[str] = None
    ten_chuyen_khoa: str
    kinh_nghiem: int = Field(ge=0, description="Số năm kinh nghiệm")
    gia_kham: float = Field(ge=0)
    rating: float = Field(ge=0, le=5, description="Điểm đánh giá 0-5")
    so_luong_danh_gia: int = 0

class BacSiGoiYChiTiet(BacSiGoiY):
    """Bác sĩ kèm lịch trống"""
    ngay_trong_som_nhat: Optional[date] = None
    khung_gio_trong: Optional[str] = None