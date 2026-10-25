from fastapi import APIRouter

# 1. Phân hệ Core (Đăng ký, Đăng nhập, /me, JWT, Phân quyền)
from api.core_auth import router as core_auth_router

# 2. Phân hệ Nghiệp vụ (Bác sĩ, Dịch vụ, Đặt lịch, Cập nhật trạng thái, Thanh toán, Audit log)
from api.nghiep_vu import router as nghiep_vu_router

# 3. Phân hệ Quản trị (Dashboard thống kê 4 kỳ, Quản lý tài khoản, Chuyên khoa)
from api.admin import router as admin_router

# Khởi tạo API Router tổng
api_router = APIRouter()

# Đăng ký các router vào hub trung tâm
api_router.include_router(core_auth_router)
api_router.include_router(nghiep_vu_router)
api_router.include_router(admin_router)

__all__ = ["api_router"]