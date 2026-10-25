from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Float
from sqlalchemy.orm import relationship
from database.database import Base


class BacSi(Base):
    __tablename__ = "bac_si"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nguoi_dung_id = Column(
        Integer,
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    chuyen_khoa_id = Column(
        Integer,
        ForeignKey("chuyen_khoa.id"),
        nullable=False
    )

    hoc_vi = Column(String(50), nullable=True)
    kinh_nghiem = Column(Integer, default=0)
    gia_kham = Column(Numeric(18, 2), nullable=False, default=0.0)
    rating = Column(Float, nullable=False, default=0.0)
    so_luong_danh_gia = Column(Integer, nullable=False, default=0)

    # Quan hệ độc lập, không ép buộc hai chiều
    user = relationship("NguoiDung")
    chuyen_khoa = relationship("ChuyenKhoa")


BacSiVariant = BacSi