"""
用户认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.models import User, UserRole
from src.auth import verify_password, get_password_hash, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    """注册请求"""
    name: str
    email: EmailStr
    password: str
    role: str  # 'tenderer' or 'bidder'
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
    """
    用户注册
    """
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 验证角色
    if request.role not in ["tenderer", "bidder"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色必须是 'tenderer' 或 'bidder'"
        )
    
    # 创建新用户
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
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    """
    # 查找用户
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
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
async def get_current_user(
    current_user: dict = Depends(lambda: {"id": 1, "name": "示例用户", "email": "user@example.com", "role": "bidder"})
):
    """
    获取当前用户信息
    (实际实现需要从 token 解析)
    """
    return UserResponse(**current_user)
