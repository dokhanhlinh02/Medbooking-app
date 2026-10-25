import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ============================================================
# 1. Cấu hình chuỗi kết nối cơ sở dữ liệu (Database URL)
# ============================================================
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./medbooking.db"
)
# Tự động chuyển đổi chuỗi kết nối PostgreSQL sang psycopg2 để khớp với thư viện đã cài
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
# 2. Khởi tạo Engine
# ============================================================
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
)

# ============================================================
# 3. Khởi tạo SessionFactory
# ============================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================
# 4. Khởi tạo Base Model
# ============================================================
Base = declarative_base()


# ============================================================
# 5. Dependency injection lấy DB session cho các Router FastAPI
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
