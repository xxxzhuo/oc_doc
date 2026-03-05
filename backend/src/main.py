"""
暗标竞标系统 - API 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from config.settings import HOST, PORT, ALLOWED_ORIGINS, LOG_LEVEL
from src.database import init_db, create_sample_data
from src.routes import auth, projects

# 配置日志
logger.add(
    "logs/bidding_{time}.log",
    rotation="1 day",
    retention="7 days",
    level=LOG_LEVEL
)

# 创建 FastAPI 应用
app = FastAPI(
    title="暗标竞标系统",
    description="安全、透明、公平的电子竞标平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 暗标竞标系统启动中...")
    
    # 初始化数据库
    await init_db()
    logger.info("✓ 数据库初始化完成")
    
    # 创建示例数据
    await create_sample_data()
    
    logger.info(f"✓ 服务运行在 http://{HOST}:{PORT}")
    logger.info(f"✓ API 文档：http://{HOST}:{PORT}/docs")


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
    # 创建日志目录
    import os
    os.makedirs("logs", exist_ok=True)
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
