from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class LeTan(Base):
    __tablename__ = "le_tan"
    __table_args__ = {"extend_existing": True}

    ma_le_tan = Column(
        Integer,
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    quay_lam_viec = Column(String(50), nullable=True)
    ca_truc = Column(String(50), nullable=True)
    ngay_vao_lam = Column(DateTime, default=utc_now)

    user = relationship("NguoiDung")