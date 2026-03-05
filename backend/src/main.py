"""
暗标竞标系统 - API 主入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import SlowAPI, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import os

from config.settings import HOST, PORT, ALLOWED_ORIGINS, LOG_LEVEL, RATE_LIMIT_PER_MINUTE
from src.database import init_db, create_sample_data
from src.routes import auth, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan 上下文管理器 (替代 @app.on_event("startup"))"""
    # 启动时
    logger.info("🚀 暗标竞标系统启动中...")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 初始化数据库
    await init_db()
    logger.info("✓ 数据库初始化完成")
    
    # 创建示例数据
    await create_sample_data()
    
    logger.info(f"✓ 服务运行在 http://{HOST}:{PORT}")
    logger.info(f"✓ API 文档：http://{HOST}:{PORT}/docs")
    
    yield
    
    # 关闭时
    logger.info("👋 服务关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="暗标竞标系统",
    description="安全、透明、公平的电子竞标平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 初始化速率限制
app.state.limiter = SlowAPI(key_func=get_remote_address)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "暗标竞标系统",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
