"""
项目管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
import json

from src.database import get_db
from src.models import Project, ProjectStatus, Bid, User, AuditLog
from src.crypto import crypto_manager

router = APIRouter(prefix="/api/projects", tags=["项目管理"])


class ProjectCreate(BaseModel):
    """创建项目请求"""
    title: str
    description: str = None
    params: dict  # 产品参数
    deadline: datetime  # 截止时间


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    title: str
    description: str = None
    params: dict
    deadline: datetime
    status: str
    creator_id: int
    created_at: datetime
    bid_count: int = 0


class BidSubmit(BaseModel):
    """提交投标请求"""
    price: float  # 报价
    params: dict = None  # 投标参数


class BidResponse(BaseModel):
    """投标响应 (不显示价格)"""
    id: int
    bidder_name: str
    bidder_company: str = None
    params: dict = None
    created_at: datetime


class BidDetailResponse(BaseModel):
    """投标详情响应 (显示价格 - 仅招标方)"""
    id: int
    bidder_name: str
    bidder_company: str = None
    price: float  # 解密后的价格
    params: dict = None
    created_at: datetime


@router.post("", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(lambda: {"id": 1, "role": "tenderer"})
):
    """
    创建竞标项目 (仅招标方)
    """
    if current_user.get("role") != "tenderer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有招标方可以创建项目"
        )
    
    project = Project(
        title=request.title,
        description=request.description,
        params_json=json.dumps(request.params),
        deadline=request.deadline,
        status=ProjectStatus.ACTIVE,
        creator_id=current_user["id"]
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user["id"],
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
    """
    获取项目列表
    """
    query = select(Project).order_by(Project.created_at.desc())
    
    if status_filter:
        query = query.where(Project.status == ProjectStatus(status_filter))
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    response = []
    for project in projects:
        # 统计投标数量
        bid_count = await db.execute(
            select(Bid).where(Bid.project_id == project.id)
        )
        count = len(bid_count.scalars().all())
        
        response.append(ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            params=json.loads(project.params_json) if project.params_json else {},
            deadline=project.deadline,
            status=project.status.value,
            creator_id=project.creator_id,
            created_at=project.created_at,
            bid_count=count
        ))
    
    return response


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取项目详情
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 统计投标数量
    bid_count = await db.execute(
        select(Bid).where(Bid.project_id == project_id)
    )
    count = len(bid_count.scalars().all())
    
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
    current_user: dict = Depends(lambda: {"id": 2, "role": "bidder"})
):
    """
    提交投标 (仅投标方)
    报价会被加密存储
    """
    if current_user.get("role") != "bidder":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有投标方可以提交投标"
        )
    
    # 检查项目是否存在且处于投标中状态
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project.status != ProjectStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目当前不接受投标"
        )
    
    # 检查是否已投标
    existing = await db.execute(
        select(Bid).where(
            Bid.project_id == project_id,
            Bid.bidder_id == current_user["id"]
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已对该项目提交过投标"
        )
    
    # 检查是否已截止
    if datetime.utcnow() > project.deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投标已截止"
        )
    
    # 加密报价
    price_encrypted = crypto_manager.encrypt_price(request.price)
    
    # 创建投标记录
    bid = Bid(
        project_id=project_id,
        bidder_id=current_user["id"],
        price_encrypted=price_encrypted,
        params_json=json.dumps(request.params) if request.params else None
    )
    
    db.add(bid)
    await db.commit()
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user["id"],
        action="SUBMIT_BID",
        resource_type="bid",
        resource_id=bid.id,
        details=json.dumps({"project_id": project_id, "price": "ENCRYPTED"})
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "投标提交成功", "bid_id": bid.id}


@router.get("/{project_id}/bids", response_model=List[BidResponse])
async def list_bids(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(lambda: {"id": 1, "role": "tenderer"})
):
    """
    查看投标列表 (不显示价格)
    - 招标方：可以看到所有投标 (不含价格)
    - 投标方：只能看到自己的投标
    """
    # 检查项目是否存在
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 构建查询
    query = select(Bid).where(Bid.project_id == project_id)
    
    # 投标方只能看自己的
    if current_user.get("role") == "bidder":
        query = query.where(Bid.bidder_id == current_user["id"])
    
    result = await db.execute(query)
    bids = result.scalars().all()
    
    response = []
    for bid in bids:
        # 获取投标方信息
        bidder_result = await db.execute(
            select(User).where(User.id == bid.bidder_id)
        )
        bidder = bidder_result.scalar_one_or_none()
        
        response.append(BidResponse(
            id=bid.id,
            bidder_name=bidder.name if bidder else "未知",
            bidder_company=bidder.company if bidder else None,
            params=json.loads(bid.params_json) if bid.params_json else None,
            created_at=bid.created_at
        ))
    
    return response


@router.post("/{project_id}/open", response_model=dict)
async def open_bids(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(lambda: {"id": 1, "role": "tenderer"})
):
    """
    开标 (仅招标方)
    开标后可以查看所有报价
    """
    if current_user.get("role") != "tenderer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有招标方可以开标"
        )
    
    # 检查项目
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project.creator_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是该项目的创建者"
        )
    
    # 检查是否已截止
    if datetime.utcnow() < project.deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投标尚未截止，不能开标"
        )
    
    # 更新项目状态
    await db.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(status=ProjectStatus.OPENED, opened_at=datetime.utcnow())
    )
    await db.commit()
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user["id"],
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
    current_user: dict = Depends(lambda: {"id": 1, "role": "tenderer"})
):
    """
    查看投标详情 (包含价格 - 仅招标方，开标后)
    """
    if current_user.get("role") != "tenderer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有招标方可以查看报价详情"
        )
    
    # 检查项目
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if project.status != ProjectStatus.OPENED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目尚未开标，无法查看报价"
        )
    
    # 获取所有投标
    result = await db.execute(
        select(Bid).where(Bid.project_id == project_id)
    )
    bids = result.scalars().all()
    
    response = []
    for bid in bids:
        # 获取投标方信息
        bidder_result = await db.execute(
            select(User).where(User.id == bid.bidder_id)
        )
        bidder = bidder_result.scalar_one_or_none()
        
        # 解密报价
        decrypted = crypto_manager.decrypt_price(bid.price_encrypted)
        
        response.append(BidDetailResponse(
            id=bid.id,
            bidder_name=bidder.name if bidder else "未知",
            bidder_company=bidder.company if bidder else None,
            price=decrypted["price"],
            params=json.loads(bid.params_json) if bid.params_json else None,
            created_at=bid.created_at
        ))
    
    # 按价格排序
    response.sort(key=lambda x: x.price)
    
    return response
