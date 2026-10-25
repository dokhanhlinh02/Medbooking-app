from typing import List, Optional
from datetime import date
from models.bac_si_goi_y import BacSiGoiY, BacSiGoiYChiTiet
from database.database import get_db


class GoiYService:
    @staticmethod
    def theo_chuyen_khoa(
        chuyen_khoa_id: int,
        min_rating: Optional[float] = None
    ) -> List[BacSiGoiY]:
        """
        Gợi ý bác sĩ theo chuyên khoa
        :param chuyen_khoa_id: Mã chuyên khoa
        :param min_rating: Lọc điểm tối thiểu (tùy chọn)
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        base_sql = """
            SELECT 
                bs.id,
                nd.ho_ten,
                bs.hoc_vi,
                ck.ten_chuyen_khoa,
                bs.kinh_nghiem,
                bs.gia_kham,
                bs.rating,
                bs.so_luong_danh_gia
            FROM bac_si bs
            JOIN nguoi_dung nd ON bs.nguoi_dung_id = nd.id
            JOIN chuyen_khoa ck ON bs.chuyen_khoa_id = ck.id
            WHERE bs.chuyen_khoa_id = ?
              AND nd.trang_thai = 1
        """
        params = [chuyen_khoa_id]

        if min_rating is not None:
            base_sql += " AND bs.rating >= ?"
            params.append(min_rating)

        base_sql += " ORDER BY bs.rating DESC, bs.so_luong_danh_gia DESC"
        cursor.execute(base_sql, params)

        columns = [col[0] for col in cursor.description]
        result = [BacSiGoiY(**dict(zip(columns, row))) for row in cursor.fetchall()]

        conn.close()
        return result



    @staticmethod
    def theo_trieu_chung(
        trieu_chung_id: int,
        min_rating: Optional[float] = None
    ) -> List[BacSiGoiY]:
        """
        Gợi ý bác sĩ theo triệu chứng (nối bảng trieu_chung_bac_si)
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        base_sql = """
            SELECT DISTINCT
                bs.id,
                nd.ho_ten,
                bs.hoc_vi,
                ck.ten_chuyen_khoa,
                bs.kinh_nghiem,
                bs.gia_kham,
                bs.rating,
                bs.so_luong_danh_gia
            FROM bac_si bs
            JOIN nguoi_dung nd ON bs.nguoi_dung_id = nd.id
            JOIN chuyen_khoa ck ON bs.chuyen_khoa_id = ck.id
            JOIN trieu_chung_bac_si tcb ON bs.id = tcb.bac_si_id
            WHERE tcb.trieu_chung_id = ?
              AND nd.trang_thai = 1
        """
        params = [trieu_chung_id]

        if min_rating is not None:
            base_sql += " AND bs.rating >= ?"
            params.append(min_rating)

        base_sql += " ORDER BY bs.rating DESC, bs.so_luong_danh_gia DESC"
        cursor.execute(base_sql, params)

        columns = [col[0] for col in cursor.description]
        result = [BacSiGoiY(**dict(zip(columns, row))) for row in cursor.fetchall()]

        conn.close()
        return result



    @staticmethod
    def co_lich_trong_som_nhat(
        chuyen_khoa_id: Optional[int] = None,
        trieu_chung_id: Optional[int] = None
    ) -> List[BacSiGoiYChiTiet]:
        """
        Gợi ý bác sĩ có lịch trống sớm nhất
        Ưu tiên lọc theo triệu chứng nếu có
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        base_sql = """
            SELECT
                bs.id,
                nd.ho_ten,
                bs.hoc_vi,
                ck.ten_chuyen_khoa,
                bs.kinh_nghiem,
                bs.gia_kham,
                bs.rating,
                bs.so_luong_danh_gia,
                MIN(lv.ngay_kham) AS ngay_trong_som_nhat,
                STRING_AGG(DISTINCT lv.khung_gio, ', ') AS khung_gio_trong
            FROM bac_si bs
            JOIN nguoi_dung nd ON bs.nguoi_dung_id = nd.id
            JOIN chuyen_khoa ck ON bs.chuyen_khoa_id = ck.id
            JOIN lich_lam_viec lv ON bs.id = lv.bac_si_id
        """
        params = []

        if trieu_chung_id:
            base_sql += " JOIN trieu_chung_bac_si tcb ON bs.id = tcb.bac_si_id "

        base_sql += """
            WHERE nd.trang_thai = 1
              AND lv.con_trong = 1
              AND lv.ngay_kham >= CAST(GETDATE() AS DATE)
        """

        if trieu_chung_id:
            base_sql += " AND tcb.trieu_chung_id = ? "
            params.append(trieu_chung_id)
        elif chuyen_khoa_id:
            base_sql += " AND bs.chuyen_khoa_id = ? "
            params.append(chuyen_khoa_id)

        base_sql += """
            GROUP BY bs.id, nd.ho_ten, bs.hoc_vi, ck.ten_chuyen_khoa,
                     bs.kinh_nghiem, bs.gia_kham, bs.rating, bs.so_luong_danh_gia
            ORDER BY ngay_trong_som_nhat ASC, bs.rating DESC
        """

        cursor.execute(base_sql, params)
        columns = [col[0] for col in cursor.description]
        result = [BacSiGoiYChiTiet(**dict(zip(columns, row))) for row in cursor.fetchall()]

        conn.close()
        return result