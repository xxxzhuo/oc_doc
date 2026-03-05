"""
系统配置管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 密钥配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# 加密配置
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/bidding.db")

# CORS 配置
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
]

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
