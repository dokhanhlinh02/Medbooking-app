from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from config import settings
from models.user import User
from database.database import get_db
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str=Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Token không hợp lệ")
    user = db.query(User).get(user_id)
    if not user: raise HTTPException(404)
    return user

def require_admin(user=Depends(get_current_user)):
    if user.role.role_name != "admin":
        raise HTTPException(403, "Chỉ quản trị viên thực hiện")
    return user