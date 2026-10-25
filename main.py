from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
# 1. Khởi tạo cơ sở dữ liệu và nạp models
from database.database import engine, Base
import models
from pydantic import BaseModel

# 2. Import TẤT CẢ các router từ thư mục routers
from routers.auth_router import router as auth_router
from routers.lich_hen import router as lich_hen_router
from routers.bac_si import router as bac_si_router

from routers.le_tan import router as le_tan_router

# Đảm bảo nạp models để tự động sinh bảng dữ liệu
_ = models
Base.metadata.create_all(bind=engine)

# Xác định đường dẫn thư mục gốc
BASE_DIR = Path(__file__).resolve().parent

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="MedBooking API System",
    description="Hệ thống quản lý phòng khám: Xác thực, Lịch hẹn, Bác sĩ và Lễ tân.",
    version="1.0.0",
)

# Cấu hình CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 3. Đăng ký TẤT CẢ các router vào ứng dụng
app.include_router(auth_router)
app.include_router(lich_hen_router)
app.include_router(bac_si_router)
app.include_router(le_tan_router)


@app.get("/", tags=["Frontend"])
@app.get("/home.html", tags=["Frontend"])
def serve_homepage():
    file_path = BASE_DIR / "templates" / "dk_dn" / "home.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file home.html"}

# Route kiểm tra tình trạng hoạt động (HealthCheck)
@app.get("/health", tags=["HealthCheck"])
def read_root():
    return {
        "status": "online",
        "service": "MedBooking API",
        "docs": "/docs",
    }

@app.get("/dk_dn/dk.html", tags=["Frontend"])
def serve_register_page():
    # Điều chỉnh lại đường dẫn nếu file dk.html nằm ở thư mục khác (ví dụ: templates/dk_dn/dk.html)
    file_path = BASE_DIR / "templates" / "dk_dn" / "dk.html"
    if not file_path.exists():
        file_path = BASE_DIR / "templates" / "dk.html"
        
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file dk.html"}

@app.get("/dk_dn/dn.html", tags=["Frontend"])
def serve_login_page():
    file_path = BASE_DIR / "templates" / "dk_dn" / "dn.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file dn.html"}

# API KIỂM TRA ĐĂNG NHẬP & ĐIỀU HƯỚNG THEO EMAIL
# ============================================================
class LoginCheckPayload(BaseModel):
    email: str
    password: str

@app.post("/api/check-login-redirect", tags=["Auth Logic"])
def check_login_redirect(payload: LoginCheckPayload):
    email = payload.email.strip()
    email_lower = email.lower()

    # 1. Admin: Ad hoặc ad ở đầu email
    if email_lower.startswith("ad"):
        return {"redirect_url": "/admin/home_a.html", "role": "admin"}
    
    # 2. Bác sĩ: bs. hoặc Bs. ở đầu email
    elif email_lower.startswith("bs."):
        return {"redirect_url": "/bac_si/home_bs.html", "role": "bac_si"}
    
    # 3. Lễ tân: lt. hoặc Lt. ở đầu email
    elif email_lower.startswith("lt."):
        return {"redirect_url": "/le_tan/dashboard.html", "role": "le_tan"}
    
    # 4. Bệnh nhân: Ràng buộc kết thúc bằng @gmail.com
    elif email_lower.endswith("@gmail.com"):
        return {"redirect_url": "/benh_nhan/home_bn.html", "role": "benh_nhan"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng email không hợp lệ hoặc không thuộc quyền hạn nào trong hệ thống!"
        )

    # ROUTE FRONTEND CHO TRANG QUÊN MẬT KHẨU
# ============================================================
@app.get("/quen_mk.html", tags=["Frontend"])
def serve_forgot_password_page():
    # Trỏ đúng vào thư mục chứa file HTML (templates/dk_dn/quen_mk.html)
    file_path = BASE_DIR / "templates" / "dk_dn" / "quen_mk.html"
    if not file_path.exists():
        file_path = BASE_DIR / "templates" / "quen_mk.html"
        
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quen_mk.html"}


# ============================================================
# API XỬ LÝ QUÊN MẬT KHẨU / ĐẶT LẠI MẬT KHẨU
# ============================================================
class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str = None  # Mật khẩu mới (nếu có bước cập nhật trực tiếp)

@app.post("/api/forgot-password", tags=["Auth Logic"])
def handle_forgot_password(payload: ForgotPasswordRequest):
    email = payload.email.strip().lower()

    # Kiểm tra xem email có tồn tại hoặc đúng định dạng hệ thống không
    # (Bạn có thể thay thế bằng câu lệnh truy vấn Database thực tế tại đây)
    is_valid_email = email.startswith("ad") or email.startswith("bs.") or email.startswith("lt.") or email.endswith("@gmail.com")

    if not is_valid_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email này chưa được đăng ký trong hệ thống!"
        )

    # Nếu người dùng gửi kèm mật khẩu mới để cập nhật
    if payload.new_password:
        # TODO: Viết logic cập nhật mật khẩu mới vào cơ sở dữ liệu cho tài khoản `email` ở đây
        return {
            "success": True,
            "message": "Đổi mật khẩu thành công! Bạn có thể đăng nhập lại bằng mật khẩu mới."
        }

    # Nếu chỉ là bước yêu cầu gửi mã xác nhận / kiểm tra email hợp lệ
    return {
        "success": True,
        "message": "Email hợp lệ. Vui lòng nhập mật khẩu mới của bạn."
    }

# ============================================================
# ROUTE FRONTEND CHO BỆNH NHÂN
# ============================================================
@app.get("/benh_nhan/home_bn.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "home_bn.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file home_bn.html"}

@app.get("/benh_nhan/ho_so_ca_nhan.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_profile_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "ho_so_ca_nhan.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file ho_so_ca_nhan.html"}

@app.get("/benh_nhan/dat_lich.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_booking_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "dat_lich.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file dat_lich.html"}

@app.get("/benh_nhan/danh_sach_lich_hen.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_appointments_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "danh_sach_lich_hen.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file danh_sach_lich_hen.html"}

@app.get("/benh_nhan/danh_sach_bac_si.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_doctors_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "danh_sach_bac_si.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file danh_sach_bac_si.html"}

@app.get("/benh_nhan/chi_tiet_bac_si.html", response_class=HTMLResponse, tags=["Frontend Benh Nhan"])
def serve_patient_doctor_detail_page():
    file_path = BASE_DIR / "templates" / "benh_nhan" / "chi_tiet_bac_si.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file chi_tiet_bac_si.html"}


# ============================================================
# ROUTE FRONTEND CHO ADMIN
# ============================================================
@app.get("/admin/home_a.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_home_page():
    file_path = BASE_DIR / "templates" / "admin" / "home_a.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file home_a.html"}

@app.get("/admin/ho_so_ca_nhan.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_profile_page():
    file_path = BASE_DIR / "templates" / "admin" / "ho_so_ca_nhan.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file ho_so_ca_nhan.html"}

@app.get("/admin/dashboard.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_dashboard():
    file_path = BASE_DIR / "templates" / "admin" / "dashboard.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file dashboard.html"}

@app.get("/admin/quan_ly_tai_khoan.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_accounts():
    file_path = BASE_DIR / "templates" / "admin" / "quan_ly_tai_khoan.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quan_ly_tai_khoan.html"}

@app.get("/admin/quan_ly_bac_si.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_doctors():
    file_path = BASE_DIR / "templates" / "admin" / "quan_ly_bac_si.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quan_ly_bac_si.html"}

@app.get("/admin/quan_ly_chuyen_khoa.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_specialties():
    file_path = BASE_DIR / "templates" / "admin" / "quan_ly_chuyen_khoa.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quan_ly_chuyen_khoa.html"}

@app.get("/admin/quan_ly_dich_vu.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_services():
    file_path = BASE_DIR / "templates" / "admin" / "quan_ly_dich_vu.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quan_ly_dich_vu.html"}

@app.get("/admin/quan_ly_mapping.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_mapping():
    file_path = BASE_DIR / "templates" / "admin" / "quan_ly_mapping.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file quan_ly_mapping.html"}

@app.get("/admin/nhat_ky_giao_dich.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_transactions():
    file_path = BASE_DIR / "templates" / "admin" / "nhat_ky_giao_dich.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file nhat_ky_giao_dich.html"}

@app.get("/admin/thung_rac.html", response_class=HTMLResponse, tags=["Frontend Admin"])
def serve_admin_recycle_bin():
    file_path = BASE_DIR / "templates" / "admin" / "thung_rac.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file thung_rac.html"}


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/api/current-user", tags=["API User"])
def get_current_user_profile(request: Request):
    """
    API trả về thông tin tài khoản hiện tại. 
    Hệ thống frontend sẽ gọi API này để tự động điền tên và email động.
    """
    user_email = request.session.get("user_email") if hasattr(request, "session") else None
    user_name = request.session.get("user_name") if hasattr(request, "session") else None
    
    return {
        "ma_quan_tri": "AD001",
        "ho_ten": user_name if user_name else "",
        "email": user_email if user_email else ""
    }


#4. ROUTES FRONTEND - BÁC SĨ (BAC_SI)
# ==========================================

@app.get("/bac_si/home_bs.html", response_class=HTMLResponse, tags=["Frontend Doctor"])
def serve_doctor_home():
    file_path = BASE_DIR / "templates" / "bac_si" / "home_bs.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file home_bs.html"}

@app.get("/bac_si/ho_so_ca_nhan.html", tags=["Doctor Frontend"])
def serve_doctor_profile():
    file_path = BASE_DIR / "templates" / "bac_si" / "ho_so_ca_nhan.html"
    if not file_path.exists():
        file_path = BASE_DIR / "templates" / "ho_so_ca_nhan.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file ho_so_ca_nhan.html"}

@app.get("/bac_si/danh_sach_ca_kham.html", response_class=HTMLResponse, tags=["Frontend Doctor"])
def serve_doctor_appointments():
    file_path = BASE_DIR / "templates" / "bac_si" / "danh_sach_ca_kham.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file danh_sach_ca_kham.html"}

@app.get("/bac_si/chan_doan_ke_don.html", response_class=HTMLResponse, tags=["Frontend Doctor"])
def serve_doctor_diagnosis():
    file_path = BASE_DIR / "templates" / "bac_si" / "chan_doan_ke_don.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Không tìm thấy file chan_doan_ke_don.html"}

#==========================================
# --- CÁC ROUTE CHO PHÂN HỆ LỄ TÂN (LE TAN) ---
#==========================================

@app.get("/le_tan/{filename}", tags=["Receptionist Frontend"])
def serve_le_tan_pages(filename: str):
    file_path = BASE_DIR / "templates" / "le_tan" / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return {"error": f"Không tìm thấy file {filename}"}



import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)