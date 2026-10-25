import importlib
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from models.models import NguoiDung, BenhNhan

# Nạp trực tiếp module auth ở thư mục gốc (không bị trùng với routers/auth.py)
import auth as root_auth

router = APIRouter(prefix="/auth", tags=["Xác thực & Tài khoản"])


class RegisterPatientRequest(BaseModel):
    ho_ten: str
    email: EmailStr
    so_dien_thoai: str
    mat_khau: str


class ChangePasswordRequest(BaseModel):
    mat_khau_cu: str
    mat_khau_moi: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    vai_tro: str
    user_id: int
    ho_ten: str

class PatientUpdateSchema(BaseModel):
    fullname: str
    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Đăng ký tài khoản Bệnh nhân")
def register_patient(payload: RegisterPatientRequest, db: Session = Depends(get_db)):
    exist = db.query(NguoiDung).filter(NguoiDung.email == payload.email).first()
    if exist:
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng.")

    user = NguoiDung(
        email=payload.email,
        mat_khau=root_auth.get_password_hash(payload.mat_khau),
        ho_ten=payload.ho_ten,
        so_dien_thoai=payload.so_dien_thoai,
        vai_tro="benh_nhan",
        trang_thai=True  # Sửa từ 1 thành True (kiểu bool)
    )
    db.add(user)
    db.flush()

    # Sửa từ ma_benh_nhan thành nguoi_dung_id khớp với models.py
    patient_profile = BenhNhan(nguoi_dung_id=user.id)
    db.add(patient_profile)
    db.commit()
    return {"message": "Đăng ký tài khoản thành công.", "user_id": user.id}


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập hệ thống lấy JWT Token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(NguoiDung).filter(NguoiDung.email == form_data.username).first()
    if not user or not root_auth.verify_password(form_data.password, user.mat_khau):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác."
        )

    if user.trang_thai == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị tạm khóa."
        )

    access_token_expires = timedelta(minutes=root_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = root_auth.create_access_token(
        data={"id": user.id, "sub": user.email, "role": user.vai_tro},
        expires_delta=access_token_expires
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "vai_tro": user.vai_tro,
        "user_id": user.id,
        "ho_ten": user.ho_ten
    }

@router.get("/me", summary="Lấy thông tin tài khoản hiện tại")
def get_me(current_user: NguoiDung = Depends(root_auth.get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "ho_ten": current_user.ho_ten,
        "so_dien_thoai": current_user.so_dien_thoai,
        "vai_tro": current_user.vai_tro
    }

@router.post("/change-password", summary="Thay đổi mật khẩu tài khoản hiện tại")
def change_password(
        payload: ChangePasswordRequest,
        current_user: NguoiDung = Depends(root_auth.get_current_user),
        db: Session = Depends(get_db)
):
    # Kiểm tra mật khẩu cũ có khớp không
    if not root_auth.verify_password(payload.mat_khau_cu, current_user.mat_khau):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu cũ không chính xác."
        )

    # Cập nhật mật khẩu mới đã mã hóa bằng bcrypt
    current_user.mat_khau = root_auth.get_password_hash(payload.mat_khau_moi)
    db.commit()

    return {"message": "Đổi mật khẩu thành công."}

# API lấy thông tin hồ sơ cá nhân
@router.get("/ho-so/{email}")
def get_ho_so(email: str, db: Session = Depends(get_db)):
    profile = benh_nhan_service.get_profile_by_email(db, email)
    if not profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin bệnh nhân!")
    return {
        "success": True,
        "data": profile
    }

# API cập nhật hồ sơ cá nhân
@router.put("/ho-so/{email}")
def update_ho_so(email: str, payload: PatientUpdateSchema, db: Session = Depends(get_db)):
    updated_data = benh_nhan_service.update_profile_by_email(db, email, payload)
    return {
        "success": True,
        "message": "Cập nhật hồ sơ thành công!",
        "data": updated_data
    }