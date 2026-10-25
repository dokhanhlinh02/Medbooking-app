import importlib
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung, BenhNhan, Admin, ChuyenKhoa
from models.bac_si import BacSi
from schemas.core_nghiep_vu import UserRegisterRequest, TokenResponse

import auth as root_auth

router = APIRouter(prefix="/auth", tags=["1. Backend Core - Auth"])


@router.post("/register", summary="Đăng ký tài khoản người dùng", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. Kiểm tra email đã tồn tại hay chưa
    existing = db.query(NguoiDung).filter(NguoiDung.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng."
        )

    # 2. Băm mật khẩu và tạo bản ghi NguoiDung
    hashed_pwd = root_auth.get_password_hash(payload.mat_khau)
    new_user = NguoiDung(
        email=payload.email,
        mat_khau=hashed_pwd,
        ho_ten=payload.ho_ten,
        so_dien_thoai=payload.so_dien_thoai or "",
        vai_tro=payload.vai_tro,
        trang_thai=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    uid: int = int(new_user.id)

    # 3. Tự động sinh hồ sơ theo vai trò
    if new_user.vai_tro == "benh_nhan":
        profile = BenhNhan(
            nguoi_dung_id=uid,
            tien_su_benh=""
        )
        db.add(profile)
        db.commit()

    elif new_user.vai_tro == "bac_si":
        default_ck = db.query(ChuyenKhoa).first()
        if not default_ck:
            default_ck = ChuyenKhoa(ten_chuyen_khoa="Đa khoa", mo_ta="Khoa khám tổng quát")
            db.add(default_ck)
            db.commit()
            db.refresh(default_ck)

        bac_si_profile = BacSi(
            nguoi_dung_id=uid,
            chuyen_khoa_id=default_ck.id,
            hoc_vi="Bác sĩ",
            kinh_nghiem=1,
            gia_kham=200000.0,
            rating=5.0,
            so_luong_danh_gia=1
        )
        db.add(bac_si_profile)
        db.commit()

    elif new_user.vai_tro == "admin":
        admin_profile = Admin(
            nguoi_dung_id=uid,
            phong_ban="Ban Giám Đốc",
            cap_do="SuperAdmin",
            ghi_chu="Quản trị viên khởi tạo"
        )
        db.add(admin_profile)
        db.commit()

    return {
        "message": "Đăng ký tài khoản thành công.",
        "user_id": uid,
        "vai_tro": new_user.vai_tro
    }


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập & cấp phát Token JWT")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")

    # Trích xuất thông tin gửi lên từ form Swagger Authorize hoặc JSON
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form_data = await request.form()
        identifier = str(form_data.get("username", "")).strip()
    else:
        try:
            body = await request.json()
        except Exception:
            body = {}
        identifier = str(body.get("email", "") or body.get("username", "") or body.get("so_dien_thoai", "")).strip()

    # Mặc định tài khoản admin nếu để trống
    if not identifier:
        identifier = "admin@medbooking.com"

    # 1. Tìm user trong database theo Email hoặc Số điện thoại
    user = db.query(NguoiDung).filter(
        (NguoiDung.email == identifier) | (NguoiDung.so_dien_thoai == identifier)
    ).first()

    # 2. Nếu chưa có user -> Tự động sinh mới kèm đúng hồ sơ phân quyền
    if not user:
        # Nhận diện vai trò dựa trên chữ gõ vào username
        lower_id = identifier.lower()
        if "admin" in lower_id:
            role = "admin"
        elif "bacsi" in lower_id or "doctor" in lower_id:
            role = "bac_si"
        else:
            role = "benh_nhan"

        email_val = identifier if "@" in identifier else f"{identifier}@medbooking.com"

        user = NguoiDung(
            email=email_val,
            ho_ten=f"User {identifier}",
            mat_khau="123456",
            vai_tro=role,
            trang_thai=True,
            so_dien_thoai="0900000000"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Tạo kèm hồ sơ tương ứng
        if role == "benh_nhan":
            db.add(BenhNhan(nguoi_dung_id=user.id, tien_su_benh=""))
            db.commit()
        elif role == "bac_si":
            ck = db.query(ChuyenKhoa).first()
            if not ck:
                ck = ChuyenKhoa(ten_chuyen_khoa="Đa khoa", mo_ta="Khoa khám tổng quát")
                db.add(ck)
                db.commit()
                db.refresh(ck)
            db.add(BacSi(
                nguoi_dung_id=user.id,
                chuyen_khoa_id=ck.id,
                gia_kham=250000.0,
                rating=5.0
            ))
            db.commit()

    # 3. Bỏ qua kiểm tra mật khẩu -> Cấp phát Token JWT ngay lập tức
    uid: int = int(user.id)
    token = root_auth.create_access_token(
        data={"id": uid, "role": user.vai_tro, "sub": user.email}
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=uid,
        ho_ten=user.ho_ten or "",
        vai_tro=user.vai_tro
    )


@router.get("/me", summary="Lấy thông tin người dùng đang đăng nhập")
def get_current_user_profile(current_user: NguoiDung = Depends(root_auth.get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "ho_ten": current_user.ho_ten,
        "so_dien_thoai": current_user.so_dien_thoai,
        "vai_tro": current_user.vai_tro,
        "trang_thai": 1 if current_user.trang_thai else 0
    }