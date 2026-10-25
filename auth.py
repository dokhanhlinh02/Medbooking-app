from datetime import datetime, timedelta, timezone
from typing import List, Optional, Any, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import NguoiDung

SECRET_KEY: str = "MEDBOOKING_SECRET_KEY_SUPER_SECURE_2026"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    # 1. Hỗ trợ mật khẩu dạng thô từ file SEED.SQL (chưa qua băm bcrypt)
    if not hashed_password.startswith("$2b$") and not hashed_password.startswith("$2a$"):
        return plain_password == hashed_password
    # 2. Mật khẩu đã băm bcrypt chuẩn sinh từ API
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta is not None:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(token)


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[NguoiDung]:
    if not token:
        return None
    try:
        payload: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_val = payload.get("id")
        if user_id_val is None:
            return None
        parsed_id = int(str(user_id_val))
        return db.query(NguoiDung).filter(NguoiDung.id == parsed_id).first()
    except (JWTError, ValueError):
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> NguoiDung:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để thực hiện tác vụ.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_val = payload.get("id")
        if user_id_val is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không chứa định danh người dùng."
            )
        parsed_id = int(str(user_id_val))
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn."
        )

    user = db.query(NguoiDung).filter(NguoiDung.id == parsed_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng sở hữu token."
        )
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: NguoiDung = Depends(get_current_user)) -> NguoiDung:
        if current_user.vai_tro not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện thao tác này."
            )
        return current_user
    return role_checker