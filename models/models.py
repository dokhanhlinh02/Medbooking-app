from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Numeric,
    Date, DateTime, Boolean, ForeignKey, Text
)

from sqlalchemy.orm import relationship
from database.database import Base


def utc_now():
    """Hàm lấy mốc thời gian UTC chuẩn cho Python 3.12+"""
    return datetime.now(timezone.utc)


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mat_khau = Column(String(255), nullable=False)
    ho_ten = Column(String(100), nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)
    vai_tro = Column(String(20), nullable=False, default="benh_nhan")
    trang_thai = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships nội bộ
    benh_nhan_profile = relationship("BenhNhan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    admin_profile = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Admin(Base):
    __tablename__ = "admin"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nguoi_dung_id = Column(
        Integer,
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    phong_ban = Column(String(100), nullable=True)
    cap_do = Column(String(50), nullable=True)
    ghi_chu = Column(String(255), nullable=True)

    user = relationship("NguoiDung", back_populates="admin_profile")


class BenhNhan(Base):
    __tablename__ = "benh_nhan"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nguoi_dung_id = Column(
        Integer,
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    ngay_sinh = Column(Date, nullable=True)
    gioitinh = Column(String(10), nullable=True)
    dia_chi = Column(String(255), nullable=True)
    tien_su_benh = Column(Text, nullable=True)

    user = relationship("NguoiDung", back_populates="benh_nhan_profile")


class ChuyenKhoa(Base):
    __tablename__ = "chuyen_khoa"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ten_chuyen_khoa = Column(String(100), nullable=False, unique=True)
    mo_ta = Column(String(255), nullable=True)

    dich_vu_list = relationship("DichVu", back_populates="chuyen_khoa")
    trieu_chung_list = relationship("TrieuChung", back_populates="chuyen_khoa")


class DichVu(Base):
    __tablename__ = "dich_vu"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    chuyen_khoa_id = Column(
        Integer,
        ForeignKey("chuyen_khoa.id"),
        nullable=False
    )
    ten_dich_vu = Column(String(100), nullable=False)
    gia_tien = Column(Numeric(18, 2), nullable=False, default=0.0)
    mo_ta = Column(String(255), nullable=True)
    dang_hoat_dong = Column(Boolean, nullable=False, default=True)

    chuyen_khoa = relationship("ChuyenKhoa", back_populates="dich_vu_list")


class ThanhToan(Base):
    __tablename__ = "thanh_toan"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lich_hen_id = Column(Integer, nullable=False)
    tong_tien = Column(Numeric(18, 2), nullable=False, default=0.0)
    phuong_thuc = Column(String(50), nullable=True)
    trang_thai_thanh_toan = Column(String(50), nullable=False, default="Chưa thanh toán")
    ngay_thanh_toan = Column(DateTime, nullable=True)


class TrieuChung(Base):
    __tablename__ = "trieu_chung"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ten_trieu_chung = Column(String(255), nullable=False)
    chuyen_khoa_id = Column(Integer, ForeignKey("chuyen_khoa.id", ondelete="CASCADE"), nullable=False)

    chuyen_khoa = relationship("ChuyenKhoa", back_populates="trieu_chung_list")


class TrieuChungBacSi(Base):
    __tablename__ = "trieu_chung_bac_si"
    __table_args__ = {"extend_existing": True}

    trieu_chung_id = Column(Integer, ForeignKey("trieu_chung.id", ondelete="CASCADE"), primary_key=True)
    bac_si_id = Column(Integer, primary_key=True)


# Alias tương thích ngược
HoaDon = ThanhToan