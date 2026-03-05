"""
项目管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update, func, join
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional, List
import json

from src.database import get_db
from src.models import Project, ProjectStatus, Bid, User, AuditLog
from src.auth import get_current_user, get_current_tenderer, get_current_bidder
from src.crypto import crypto_manager

router = APIRouter(prefix="/api/projects", tags=["项目管理"])


class ProjectCreate(BaseModel):
    """创建项目请求"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    params: dict
    deadline: datetime


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    title: str
    description: Optional[str] = None
    params: dict
    deadline: datetime
    status: str
    creator_id: int
    created_at: datetime
    bid_count: int = 0


class BidSubmit(BaseModel):
    """提交投标请求"""
    price_encrypted: str  # 前端加密后的报价
    params: Optional[dict] = None


class BidResponse(BaseModel):
    """投标响应 (不显示价格)"""
    id: int
    bidder_name: str
    bidder_company: Optional[str] = None
    params: Optional[dict] = None
    created_at: datetime


class BidDetailResponse(BaseModel):
    """投标详情响应 (显示价格 - 仅招标方)"""
    id: int
    bidder_name: str
    bidder_company: Optional[str] = None
    price: float
    params: Optional[dict] = None
    created_at: datetime


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_tenderer)
):
    """创建竞标项目 (仅招标方)"""
    project = Project(
        title=request.title,
        description=request.description,
        params_json=json.dumps(request.params),
        deadline=request.deadline,
        status=ProjectStatus.ACTIVE,
        creator_id=current_user["user_id"]
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    audit_log = AuditLog(
        user_id=current_user["user_id"],
        action="CREATE_PROJECT",
        resource_type="project",
        resource_id=project.id,
        details=json.dumps({"title": request.title})
    )
    db.add(audit_log)
    await db.commit()
    
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        params=json.loads(project.params_json),
        deadline=project.deadline,
        status=project.status.value,
        creator_id=project.creator_id,
        created_at=project.created_at
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取项目列表 (使用 JOIN 优化 N+1 查询)"""
    query = select(
        Project,
        func.count(Bid.id).label("bid_count")
    ).outerjoin(Bid).group_by(Project.id).order_by(Project.created_at.desc())
    
    if status_filter:
        query = query.where(Project.status == ProjectStatus(status_filter))
    
    result = await db.execute(query)
    rows = result.all()
    
    response = []
    for project, bid_count in rows:
        response.append(ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            params=json.loads(project.params_json) if project.params_json else {},
            deadline=project.deadline,
            status=project.status.value,
            creator_id=project.creator_id,
            created_at=project.created_at,
            bid_count=bid_count or 0
        ))
    
    return response


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    bid_count = await db.execute(
        select(func.count(Bid.id)).where(Bid.project_id == project_id)
    )
    count = bid_count.scalar() or 0
    
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        params=json.loads(project.params_json) if project.params_json else {},
        deadline=project.deadline,
        status=project.status.value,
        creator_id=project.creator_id,
        created_at=project.created_at,
        bid_count=count
    )


@router.post("/{project_id}/bids", response_model=dict)
async def submit_bid(
    project_id: int,
    request: BidSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_bidder)
):
    """提交投标 (仅投标方，前端已加密报价)"""
    project = await db.get(Project, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if project.status != ProjectStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="项目当前不接受投标")
    
    # 防止招标方给自己项目投标
    if project.creator_id == current_user["user_id"]:
        raise HTTPException(status_code=403, detail="招标方不能参与自己的项目投标")
    
    # 检查是否已投标
    existing = await db.execute(
        select(Bid).where(
            Bid.project_id == project_id,
            Bid.bidder_id == current_user["user_id"]
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="您已对该项目提交过投标")
    
    # 检查是否已截止
    if datetime.now(timezone.utc) > project.deadline.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="投标已截止")
    
    # 直接存储前端传来的密文
    bid = Bid(
        project_id=project_id,
        bidder_id=current_user["user_id"],
        price_encrypted=request.price_encrypted,
        params_json=json.dumps(request.params) if request.params else None
    )
    
    db.add(bid)
    await db.commit()
    
    audit_log = AuditLog(
        user_id=current_user["user_id"],
        action="SUBMIT_BID",
        resource_type="bid",
        resource_id=bid.id,
        details=json.dumps({"project_id": project_id})
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "投标提交成功", "bid_id": bid.id}


@router.get("/{project_id}/bids", response_model=List[BidResponse])
async def list_bids(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """查看投标列表 (不显示价格，使用 JOIN 优化查询)"""
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    query = select(Bid, User).join(User, Bid.bidder_id == User.id).where(Bid.project_id == project_id)
    
    # 投标方只能看自己的
    if current_user.get("role") == "bidder":
        query = query.where(Bid.bidder_id == current_user["user_id"])
    
    result = await db.execute(query)
    rows = result.all()
    
    response = []
    for bid, bidder in rows:
        response.append(BidResponse(
            id=bid.id,
            bidder_name=bidder.name,
            bidder_company=bidder.company,
            params=json.loads(bid.params_json) if bid.params_json else None,
            created_at=bid.created_at
        ))
    
    return response


@router.post("/{project_id}/open", response_model=dict)
async def open_bids(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_tenderer)
):
    """开标 (仅招标方)"""
    project = await db.get(Project, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if project.creator_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="您不是该项目的创建者")
    
    if datetime.now(timezone.utc) < project.deadline.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="投标尚未截止，不能开标")
    
    await db.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(status=ProjectStatus.OPENED, opened_at=datetime.now(timezone.utc))
    )
    await db.commit()
    
    audit_log = AuditLog(
        user_id=current_user["user_id"],
        action="OPEN_BIDS",
        resource_type="project",
        resource_id=project_id,
        details=json.dumps({"status": "opened"})
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "开标成功", "status": "opened"}


@router.get("/{project_id}/bids/detail", response_model=List[BidDetailResponse])
async def get_bid_details(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_tenderer)
):
    """查看投标详情 (包含价格 - 仅招标方，开标后)"""
    project = await db.get(Project, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if project.status != ProjectStatus.OPENED:
        raise HTTPException(status_code=400, detail="项目尚未开标，无法查看报价")
    
    # 使用 JOIN 一次性查询 bid 和 bidder 信息
    result = await db.execute(
        select(Bid, User)
        .join(User, Bid.bidder_id == User.id)
        .where(Bid.project_id == project_id)
    )
    rows = result.all()
    
    response = []
    for bid, bidder in rows:
        # 解密报价 (后端解密)
        try:
            decrypted = crypto_manager.decrypt_price(bid.price_encrypted)
            price = decrypted.get("price", 0)
        except Exception:
            price = 0
        
        response.append(BidDetailResponse(
            id=bid.id,
            bidder_name=bidder.name,
            bidder_company=bidder.company,
            price=price,
            params=json.loads(bid.params_json) if bid.params_json else None,
            created_at=bid.created_at
        ))
    
    response.sort(key=lambda x: x.price)
    return response
