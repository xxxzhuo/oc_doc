"""
认证模块 - JWT Token 管理
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    :param data: 令牌数据 (通常包含 user_id, email, role)
    :param expires_delta: 过期时间增量
    :return: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码访问令牌
    :param token: JWT 令牌
    :return: 令牌数据，如果无效则返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_from_token(token: str) -> Optional[dict]:
    """
    从令牌获取当前用户信息
    :param token: JWT 令牌
    :return: 用户信息字典
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "name": payload.get("name")
    }
