import importlib
import math
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from models.models import NguoiDung, ChuyenKhoa
from models.lich_hen import LichHen
from models.bac_si import BacSi, BacSiVariant
from schemas.bac_si import BacSiCreate, BacSiUpdate

import auth as root_auth

class BacSiService:

    @staticmethod
    def create_doctor(db: Session, data: BacSiCreate, current_user: NguoiDung) -> BacSi:
        # 1. Kiểm tra email người dùng đã tồn tại chưa
        existing_user = db.query(NguoiDung).filter(NguoiDung.email == data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được sử dụng trên hệ thống."
            )

        # 2. Kiểm tra Chuyên khoa có tồn tại không
        specialty_id = getattr(data, "chuyen_khoa_id", None) or getattr(data, "ma_chuyen_khoa", None)
        chk_ck = db.query(ChuyenKhoa).filter(
            (ChuyenKhoa.id == specialty_id) if hasattr(ChuyenKhoa, "id") else (ChuyenKhoa.ma_chuyen_khoa == specialty_id)
        ).first()
        if not chk_ck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chuyên khoa với ID {specialty_id} không tồn tại."
            )

        # 3. Tạo tài khoản Người dùng (NguoiDung)
        hashed_password = str(root_auth.get_password_hash(data.mat_khau))
        phone_val: str = str(data.so_dien_thoai) if data.so_dien_thoai is not None else ""

        new_user = NguoiDung(
            email=data.email,
            mat_khau=hashed_password,
            ho_ten=data.ho_ten,
            so_dien_thoai=phone_val,
            vai_tro="bac_si",
            trang_thai=True
        )
        db.add(new_user)
        db.flush()

        # 4. Tạo hồ sơ Bác sĩ chuẩn hóa trường
        ck_id_val = getattr(chk_ck, "id", None) or getattr(chk_ck, "ma_chuyen_khoa", None)
        doctor = BacSi(
            nguoi_dung_id=new_user.id,
            chuyen_khoa_id=ck_id_val,
            hoc_vi=data.hoc_vi or "",
            kinh_nghiem=data.kinh_nghiem or 1,
            gia_kham=data.gia_kham or 200000.0,
            rating=0.0
        )
        db.add(doctor)
        db.flush()

        # 5. Lưu các biến thể/cơ sở nếu có
        if getattr(data, "variants", None):
            for v in data.variants:
                variant_record = BacSiVariant(
                    bac_si_id=doctor.id,
                    ten_co_so=v.ten_co_so or "",
                    dia_chi_co_so=v.dia_chi_co_so or "",
                    chuyen_khoa_phu=v.chuyen_khoa_phu or "",
                    khung_gio_phu=v.khung_gio_phu or ""
                )
                db.add(variant_record)

        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def get_doctor_by_id(db: Session, doctor_id: int, is_admin: bool = False) -> BacSi:
        doctor = db.query(BacSi).filter(BacSi.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bác sĩ không tồn tại hoặc đã bị ẩn."
            )
        return doctor

    @staticmethod
    def get_paginated_doctors(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        chuyen_khoa_id: Optional[int] = None,
        hoc_vi: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        doctor_status: Optional[int] = None,
        sort_by: str = "id",
        sort_order: str = "desc",
        is_admin: bool = False,
        patient_history_specialty_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        # 1. Join đúng khóa ngoại giữa BacSi và NguoiDung
        query = db.query(BacSi).join(NguoiDung, BacSi.nguoi_dung_id == NguoiDung.id)

        # 2. Phân quyền hiển thị theo trạng thái hoạt động của NguoiDung
        if not is_admin:
            query = query.filter(NguoiDung.trang_thai == True)
        else:
            if doctor_status is not None:
                query = query.filter(NguoiDung.trang_thai == bool(doctor_status))

        # 3. Tìm kiếm theo từ khóa
        if keyword:
            kw = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    NguoiDung.ho_ten.ilike(kw),
                    NguoiDung.email.ilike(kw),
                    NguoiDung.so_dien_thoai.ilike(kw)
                )
            )

        # 4. Bộ lọc thuộc tính
        if chuyen_khoa_id:
            query = query.filter(BacSi.chuyen_khoa_id == chuyen_khoa_id)
        if hoc_vi:
            query = query.filter(BacSi.hoc_vi.ilike(f"%{hoc_vi.strip()}%"))
        if min_price is not None:
            query = query.filter(BacSi.gia_kham >= min_price)
        if max_price is not None:
            query = query.filter(BacSi.gia_kham <= max_price)

        # 5. Sắp xếp an toàn
        sort_column_map = {
            "ten": NguoiDung.ho_ten,
            "rating": BacSi.rating,
            "gia_kham": BacSi.gia_kham,
            "id": BacSi.id
        }
        target_col = sort_column_map.get(sort_by, BacSi.id)
        if sort_order.lower() == "asc":
            query = query.order_by(target_col.asc())
        else:
            query = query.order_by(target_col.desc())

        total_records = query.count()
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        offset = (page - 1) * page_size
        raw_doctors = query.offset(offset).limit(page_size).all()

        # 6. Gắn nhãn badge & format dữ liệu trả về
        items: List[Dict[str, Any]] = []
        for doc in raw_doctors:
            user_obj = getattr(doc, "user", None)
            ck_obj = getattr(doc, "chuyen_khoa", None)

            completed_appts = db.query(func.count(LichHen.id))\
                .filter(LichHen.bac_si_id == doc.id, LichHen.trang_thai.in_(["Completed", "Đã hoàn thành"]))\
                .scalar() or 0
            is_hot = completed_appts >= 20 or (doc.rating is not None and doc.rating >= 4.8)

            is_related = False
            if patient_history_specialty_ids and doc.chuyen_khoa_id in patient_history_specialty_ids:
                is_related = True

            doc_dict = {
                "ma_bac_si": doc.id,
                "ho_ten": user_obj.ho_ten if user_obj else "",
                "email": user_obj.email if user_obj else "",
                "so_dien_thoai": user_obj.so_dien_thoai if user_obj else "",
                "ma_chuyen_khoa": doc.chuyen_khoa_id,
                "ten_chuyen_khoa": ck_obj.ten_chuyen_khoa if ck_obj else "",
                "hoc_vi": getattr(doc, "hoc_vi", "") or "",
                "kinh_nghiem": getattr(doc, "kinh_nghiem", 0) or 0,
                "gia_kham": float(getattr(doc, "gia_kham", 0.0) or 0.0),
                "rating": float(getattr(doc, "rating", 0.0) or 0.0),
                "status": 1 if (user_obj and user_obj.trang_thai) else 0,
                "is_hot": is_hot,
                "is_new": False,
                "is_related": is_related,
                "variants": getattr(doc, "variants", [])
            }
            items.append(doc_dict)

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages
        }

    @staticmethod
    def update_doctor(db: Session, doctor_id: int, data: BacSiUpdate, current_user: NguoiDung) -> BacSi:
        doctor = db.query(BacSi).filter(BacSi.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bác sĩ cần chỉnh sửa."
            )

        # 1. Cập nhật thông tin User
        if doctor.user:
            if data.ho_ten is not None:
                doctor.user.ho_ten = data.ho_ten
            if data.so_dien_thoai is not None:
                doctor.user.so_dien_thoai = data.so_dien_thoai
            if getattr(data, "status", None) is not None:
                doctor.user.trang_thai = bool(data.status)

        # 2. Cập nhật thông tin Bác sĩ
        specialty_id = getattr(data, "chuyen_khoa_id", None) or getattr(data, "ma_chuyen_khoa", None)
        if specialty_id is not None:
            doctor.chuyen_khoa_id = specialty_id
        if data.hoc_vi is not None:
            doctor.hoc_vi = data.hoc_vi
        if data.kinh_nghiem is not None:
            doctor.kinh_nghiem = data.kinh_nghiem
        if data.gia_kham is not None:
            doctor.gia_kham = data.gia_kham

        # 3. Ghi đè biến thể phụ thuộc nếu có
        if getattr(data, "variants", None) is not None:
            try:
                db.query(BacSiVariant).filter(
                    (BacSiVariant.bac_si_id == doctor_id) if hasattr(BacSiVariant, "bac_si_id") else (BacSiVariant.ma_bac_si == doctor_id)
                ).delete()
                for v in data.variants:
                    new_var = BacSiVariant(
                        bac_si_id=doctor_id,
                        ten_co_so=v.ten_co_so or "",
                        dia_chi_co_so=v.dia_chi_co_so or "",
                        chuyen_khoa_phu=v.chuyen_khoa_phu or "",
                        khung_gio_phu=v.khung_gio_phu or ""
                    )
                    db.add(new_var)
            except Exception:
                pass

        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def delete_doctor(db: Session, doctor_id: int, delete_type: str, current_user: NguoiDung) -> Dict[str, Any]:
        doctor = db.query(BacSi).filter(BacSi.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bác sĩ cần xóa không tồn tại."
            )

        if delete_type.lower() == "soft":
            if doctor.user:
                doctor.user.trang_thai = False
            db.commit()
            return {"message": "Đã ẩn bác sĩ thành công (Soft Delete).", "doctor_id": doctor_id, "status": 0}

        elif delete_type.lower() == "hard":
            active_appointments = db.query(LichHen).filter(
                LichHen.bac_si_id == doctor_id,
                LichHen.trang_thai.in_(["Pending", "Chờ xác nhận", "Confirmed", "Đã xác nhận"])
            ).count()

            if active_appointments > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Không thể xóa vĩnh viễn: Bác sĩ đang có {active_appointments} lịch hẹn đang xử lý."
                )

            user_obj = doctor.user
            db.delete(doctor)
            if user_obj:
                db.delete(user_obj)

            db.commit()
            return {"message": "Đã xóa vĩnh viễn bác sĩ khỏi cơ sở dữ liệu (Hard Delete).", "doctor_id": doctor_id}

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kiểu xóa không hợp lệ. Vui lòng chọn 'soft' hoặc 'hard'."
            )