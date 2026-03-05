"""
认证模块 - JWT Token 管理
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import AsyncSessionLocal
from src.models import User, UserRole

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(lambda: AsyncSessionLocal())
) -> dict:
    """
    获取当前用户 - 真正的认证依赖
    :param token: JWT 令牌 (从 Authorization: Bearer <token> 头解析)
    :param db: 数据库会话
    :return: 用户信息字典
    :raises: HTTPException 401 如果 token 无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码 token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 提取用户 ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 从数据库查询用户
    try:
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        # 返回用户信息 (包含角色，从 DB 获取确保准确)
        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
            "company": user.company
        }
    except Exception as e:
        raise credentials_exception
    finally:
        await db.close()


async def get_current_tenderer(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    获取当前招标方用户
    :raises: HTTPException 403 如果用户不是招标方
    """
    if current_user.get("role") != "tenderer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有招标方可以执行此操作"
        )
    return current_user


async def get_current_bidder(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    获取当前投标方用户
    :raises: HTTPException 403 如果用户不是投标方
    """
    if current_user.get("role") != "bidder":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有投标方可以执行此操作"
        )
    return current_user


def is_token_expired(token: str) -> bool:
    """
    检查 token 是否过期
    :param token: JWT 令牌
    :return: True 如果过期
    """
    payload = decode_access_token(token)
    if payload is None:
        return True
    
    exp = payload.get("exp")
    if exp is None:
        return True
    
    return datetime.now(timezone.utc).timestamp() > exp
