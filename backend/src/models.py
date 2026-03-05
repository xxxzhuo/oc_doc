"""
数据库模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    TENDERER = "tenderer"  # 招标方
    BIDDER = "bidder"      # 投标方


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"      # 草稿
    ACTIVE = "active"    # 投标中
    CLOSED = "closed"    # 已截止
    OPENED = "opened"    # 已开标


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), nullable=False)
    company = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    projects = relationship("Project", back_populates="creator", foreign_keys="Project.creator_id")
    bids = relationship("Bid", back_populates="bidder")


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    params_json = Column(Text)  # 公开的产品参数 (JSON)
    deadline = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    opened_at = Column(DateTime)

    # 关系
    creator = relationship("User", back_populates="projects", foreign_keys=[creator_id])
    bids = relationship("Bid", back_populates="project", cascade="all, delete-orphan")


class Bid(Base):
    """投标表"""
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price_encrypted = Column(Text, nullable=False)  # AES-256 加密的报价
    params_json = Column(Text)  # 投标方填写的参数 (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 唯一约束：每个投标方对每个项目只能投标一次
    __table_args__ = (
        UniqueConstraint('project_id', 'bidder_id', name='uq_project_bidder'),
    )

    # 关系
    project = relationship("Project", back_populates="bids")
    bidder = relationship("User", back_populates="bids")


class AuditLog(Base):
    """操作日志表"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # 操作类型
    resource_type = Column(String(50))  # 资源类型
    resource_id = Column(Integer)  # 资源 ID
    details = Column(Text)  # 详细信息 (JSON)
    ip_address = Column(String(45))  # IP 地址
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
