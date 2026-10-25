from decimal import Decimal
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import extract
from sqlalchemy.orm import Session

from models.models import NguoiDung, ChuyenKhoa, DichVu, ThanhToan as HoaDon  #[cite: 4]
from models.lich_hen import LichHen, LogTrangThai  #[cite: 3]
from models.bac_si import BacSi  #[cite: 1]

class AdminService:

    # --- Quản trị người dùng & Phân quyền ---
    @staticmethod
    def get_users(db: Session, vai_tro: Optional[str] = None) -> List[NguoiDung]:
        query = db.query(NguoiDung)
        if vai_tro:
            query = query.filter(NguoiDung.vai_tro == vai_tro)
        return query.order_by(NguoiDung.id.desc()).all()  #[cite: 4]

    @staticmethod
    def toggle_user_status(db: Session, user_id: int) -> Dict[str, Any]:
        user = db.query(NguoiDung).filter(NguoiDung.id == user_id).first()  #[cite: 4]
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại.")
        user.trang_thai = not user.trang_thai  # Đảo trạng thái boolean
        db.commit()
        return {"message": "Cập nhật trạng thái thành công.", "user_id": user_id, "trang_thai": 1 if user.trang_thai else 0}

    # --- Quản trị Chuyên khoa ---
    @staticmethod
    def create_chuyen_khoa(db: Session, ten: str, mo_ta: Optional[str] = None) -> ChuyenKhoa:
        ck = ChuyenKhoa(ten_chuyen_khoa=ten, mo_ta=mo_ta or "")
        db.add(ck)
        db.commit()
        db.refresh(ck)
        return ck

    # --- Quản trị Dịch vụ ---
    @staticmethod
    def create_dich_vu(db: Session, chuyen_khoa_id: int, ten: str, gia: Decimal, mo_ta: Optional[str] = None) -> DichVu:
        dv = DichVu(chuyen_khoa_id=chuyen_khoa_id, ten_dich_vu=ten, gia_tien=gia, mo_ta=mo_ta or "")  #[cite: 4]
        db.add(dv)
        db.commit()
        db.refresh(dv)
        return dv

    # --- Dashboard Thống kê 4 kỳ trong năm & Báo cáo chi tiết ---
    @staticmethod
    def get_quarterly_dashboard(db: Session, year: int, quarter: Optional[str] = None) -> Dict[str, Any]:
        quarter_months = {
            "Q1": [1, 2, 3],
            "Q2": [4, 5, 6],
            "Q3": [7, 8, 9],
            "Q4": [10, 11, 12]
        }

        query = db.query(LichHen).filter(
            extract('year', LichHen.ngay_kham) == year,
            LichHen.trang_thai == "Completed"
        )

        months_filter = None
        if quarter and quarter.upper() in quarter_months:
            months_filter = quarter_months[quarter.upper()]
            query = query.filter(extract('month', LichHen.ngay_kham).in_(months_filter))

        completed_appointments = query.order_by(LichHen.ngay_kham.desc(), LichHen.khung_gio.desc()).all()  #[cite: 3]

        total_records = len(completed_appointments)
        total_revenue = Decimal("0.0")
        transaction_logs: List[Dict[str, Any]] = []

        chart_labels: List[str] = []
        chart_data_map: Dict[int, float] = {}

        if months_filter:
            for m in months_filter:
                chart_labels.append(f"Tháng {m}")
                chart_data_map[m] = 0.0
        else:
            for m in range(1, 13):
                chart_labels.append(f"T{m}")
                chart_data_map[m] = 0.0

        for appt in completed_appointments:
            bill = db.query(HoaDon).filter(HoaDon.lich_hen_id == appt.id).first()  #[cite: 3, 4]
            default_price = appt.bac_si.gia_kham if (appt.bac_si and appt.bac_si.gia_kham) else Decimal("0.0")  #[cite: 1]
            amount = Decimal(str(bill.tong_tien)) if (bill and bill.tong_tien) else default_price  #[cite: 4]
            total_revenue += amount

            month_idx = appt.ngay_kham.month
            if month_idx in chart_data_map:
                chart_data_map[month_idx] += float(amount)

            bac_si_name = appt.bac_si.user.ho_ten if (appt.bac_si and appt.bac_si.user) else "Chưa rõ"  #[cite: 1, 4]

            checkin_log = db.query(LogTrangThai).filter(
                LogTrangThai.lich_hen_id == appt.id,  #[cite: 3]
                LogTrangThai.trang_thai_moi.in_(["DaDen", "Confirmed"])
            ).first()

            le_tan_name = checkin_log.nguoi_thuc_hien if checkin_log else "Hệ thống"  #[cite: 3]

            transaction_logs.append({
                "ma_lich_hen": appt.id,  #[cite: 3]
                "ngay_kham": str(appt.ngay_kham),
                "khung_gio": str(appt.khung_gio),  #[cite: 3]
                "benh_nhan": appt.benh_nhan.user.ho_ten if (appt.benh_nhan and appt.benh_nhan.user) else "Ẩn danh",  #[cite: 4]
                "bac_si": bac_si_name,
                "le_tan_xac_nhan": le_tan_name,
                "so_tien": float(amount),
                "loi_nhuan": float(amount * Decimal("0.35")),
                "trang_thai": "Hoàn thành"
            })

        total_profit = total_revenue * Decimal("0.35")

        top_doctors = db.query(BacSi).join(NguoiDung, BacSi.nguoi_dung_id == NguoiDung.id)\
            .filter(NguoiDung.trang_thai == True)\
            .order_by(BacSi.rating.desc())\
            .limit(5).all()  #[cite: 1, 4]

        top_doc_list = [
            {"ma_bac_si": d.id, "ho_ten": d.user.ho_ten if d.user else "", "rating": float(d.rating or 0.0)}  #[cite: 1, 4]
            for d in top_doctors
        ]

        return {
            "year": year,
            "quarter": quarter or "ALL",
            "has_data": total_records > 0,
            "total_completed": total_records,
            "total_revenue": float(total_revenue),
            "total_profit": float(total_profit),
            "top_doctors": top_doc_list,
            "chart": {
                "labels": chart_labels,
                "values": list(chart_data_map.values())
            },
            "transactions": transaction_logs
        }