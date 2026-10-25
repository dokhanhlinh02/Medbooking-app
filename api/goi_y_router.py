from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.bac_si_goi_y import BacSiGoiY, BacSiGoiYChiTiet
from services.goi_y_service import GoiYService

router = APIRouter(prefix="/api/goi-y", tags=["Gợi ý bác sĩ"])


@router.get("/bac-si", response_model=List[BacSiGoiY])
def lay_danh_sach_goi_y(
    chuyen_khoa_id: Optional[int] = Query(None, description="Mã chuyên khoa"),
    trieu_chung_id: Optional[int] = Query(None, description="Mã triệu chứng"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Lọc đánh giá tối thiểu")
):
    """
    Gợi ý bác sĩ — **chọn 1 trong 2**:
    - Truyền `trieu_chung_id` → tìm theo triệu chứng (ưu tiên hơn)
    - Truyền `chuyen_khoa_id` → tìm theo chuyên khoa
    """
    if not trieu_chung_id and not chuyen_khoa_id:
        raise HTTPException(
            status_code=400,
            detail="Phải cung cấp trieu_chung_id hoặc chuyen_khoa_id"
        )

    if trieu_chung_id:
        return GoiYService.theo_trieu_chung(trieu_chung_id, min_rating)
    return GoiYService.theo_chuyen_khoa(chuyen_khoa_id, min_rating)


@router.get("/bac-si-lich-trong", response_model=List[BacSiGoiYChiTiet])
def lay_co_lich_trong(
    chuyen_khoa_id: Optional[int] = Query(None),
    trieu_chung_id: Optional[int] = Query(None)
):
    """Gợi ý bác sĩ có lịch trống sớm nhất"""
    return GoiYService.co_lich_trong_som_nhat(chuyen_khoa_id, trieu_chung_id)