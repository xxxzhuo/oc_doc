"""
用户认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.models import User, UserRole
from src.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user,
    is_token_expired
)
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 速率限制器
limiter = Limiter(key_func=get_remote_address)


class RegisterRequest(BaseModel):
    """注册请求"""
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str
    company: str = None


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    name: str
    email: str
    role: str
    company: str = None


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    if request.role not in ["tenderer", "bidder"]:
        raise HTTPException(status_code=400, detail="角色必须是 'tenderer' 或 'bidder'")
    
    user = User(
        name=request.name,
        email=request.email,
        role=UserRole(request.role),
        company=request.company,
        password_hash=get_password_hash(request.password)
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value,
        company=user.company
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # 登录限流：5 次/分钟
async def login(
    request: Request,
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录 (限流：5 次/分钟)"""
    result = await db.execute(select(User).where(User.email == login_request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "name": user.name
        },
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "company": user.company
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user["user_id"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        company=current_user.get("company")
    )
