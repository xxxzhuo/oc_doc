"""
数据库连接和管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from src.models import Base

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=False)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """初始化数据库 - 创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    用作依赖注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_sample_data():
    """创建示例数据 (用于测试)"""
    from src.models import User, UserRole
    from src.auth import get_password_hash
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        # 检查是否已有数据
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if len(users) > 0:
            return  # 已有数据，跳过
        
        # 创建示例用户
        tenderer = User(
            name="张三",
            email="tenderer@example.com",
            role=UserRole.TENDERER,
            company="某某采购单位",
            password_hash=get_password_hash("password123")
        )
        
        bidder1 = User(
            name="李四",
            email="bidder1@example.com",
            role=UserRole.BIDDER,
            company="供应商 A 公司",
            password_hash=get_password_hash("password123")
        )
        
        bidder2 = User(
            name="王五",
            email="bidder2@example.com",
            role=UserRole.BIDDER,
            company="供应商 B 公司",
            password_hash=get_password_hash("password123")
        )
        
        session.add_all([tenderer, bidder1, bidder2])
        await session.commit()
        
        print("✓ 示例数据创建成功")
        print(f"  招标方：tenderer@example.com / password123")
        print(f"  投标方 1: bidder1@example.com / password123")
        print(f"  投标方 2: bidder2@example.com / password123")
