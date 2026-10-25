from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Date,
    DateTime, ForeignKey, Boolean
)

from sqlalchemy.orm import relationship
from database.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class LichLamViec(Base):
    """Khớp với CREATE TABLE dbo.lich_lam_viec"""
    __tablename__ = "lich_lam_viec"
    __table_args__ = {"extend_existing": True}

    # Đảm bảo có ít nhất một cột được đặt primary_key=True
    id = Column(Integer, primary_key=True, index=True) 
    
    # Các cột khác...
    con_trong = Column(Boolean, nullable=False, default=True)


    le_tan_ma_le_tan = Column(Integer, ForeignKey("le_tan.ma_le_tan"), nullable=True)
    bac_si_id = Column(Integer, ForeignKey("bac_si.id", ondelete="CASCADE"), nullable=False)
    ngay_kham = Column(Date, nullable=False)
    khung_gio = Column(String(100), nullable=False)
    con_trong = Column(Boolean, nullable=False, default=True)


class LichHen(Base):
    """Khớp với CREATE TABLE dbo.lich_hen"""
    __tablename__ = "lich_hen"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    benh_nhan_id = Column(Integer, ForeignKey("benh_nhan.id"), nullable=False)

    # Cho phép null để khi bệnh nhân vừa đặt lịch chưa cần gán ngay, chờ Admin phân công
    bac_si_id = Column(Integer, ForeignKey("bac_si.id"), nullable=True)

    # Bổ sung liên kết tới Lễ tân để lễ tân tiếp nhận thông tin bệnh nhân
    le_tan_ma_le_tan = Column(Integer, ForeignKey("le_tan.ma_le_tan"), nullable=True)

    dich_vu_id = Column(Integer, ForeignKey("dich_vu.id"), nullable=False)
    ngay_kham = Column(Date, nullable=False)
    khung_gio = Column(String(100), nullable=False)
    trang_thai = Column(String(50), nullable=False, default="Chờ xác nhận",
                        index=True)  # Chờ xác nhận, Đã phân công, Hoàn thành
    ghi_chu = Column(String(255), nullable=True)
    created_at = Column(DateTime)

    # Alias thuộc tính cũ để tránh gãy code nghiệp vụ khác nếu có
    @property
    def ma_lich_hen(self):
        return self.id

    # Relationships
    benh_nhan = relationship("BenhNhan", backref="lich_hen_list")
    bac_si = relationship("BacSi", backref="lich_hen_list")
    le_tan = relationship("LeTan", backref="lich_hen_list")  # Thêm relationship cho Lễ tân
    dich_vu = relationship("DichVu", backref="lich_hen_list")
    logs = relationship("LogTrangThai", back_populates="lich_hen", cascade="all, delete-orphan")

class LogTrangThai(Base):
    """Khớp với CREATE TABLE dbo.log_trang_thai"""
    __tablename__ = "log_trang_thai"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lich_hen_id = Column(Integer, ForeignKey("lich_hen.id", ondelete="CASCADE"), nullable=False)
    trang_thai_cu = Column(String(50), nullable=True)
    trang_thai_moi = Column(String(50), nullable=False)
    nguoi_thuc_hien = Column(String(100), nullable=False)
    thoi_gian = Column(DateTime, default=utc_now)

    lich_hen = relationship("LichHen", back_populates="logs")