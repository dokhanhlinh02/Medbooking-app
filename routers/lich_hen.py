from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


# Giả sử hàm lấy thời gian chuẩn của bạn
# from utils.time import utc_now

router = APIRouter(prefix="/appointments", tags=["Quản lý Lịch hẹn"])

class LichHen(Base):
    """Khớp với CREATE TABLE dbo.lich_hen"""
    __tablename__ = "lich_hen"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    benh_nhan_id = Column(Integer, ForeignKey("benh_nhan.id"), nullable=False)

    # Cho phép null để khi bệnh nhân vừa đặt lịch chưa cần gán ngay, chờ Admin phân công
    bac_si_id = Column(Integer, ForeignKey("bac_si.id"), nullable=True)

    # Bổ sung liên kết tới Lễ tân để lễ tân tiếp nhận thông tin bệnh nhân
    le_tan_id = Column(Integer, ForeignKey("le_tan.id"), nullable=True)

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