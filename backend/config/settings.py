"""
系统配置管理
⚠️ 安全提示：生产环境必须设置环境变量，不要使用默认值
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 密钥配置 - 必须从环境变量读取
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("❌ 错误：未设置 SECRET_KEY 环境变量")
    print("   请复制 .env.example 为 .env 并设置 SECRET_KEY")
    print("   生成方法：python -c \"import secrets; print(secrets.token_hex(32))\"")
    sys.exit(1)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# 加密配置 - 必须从环境变量读取
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    print("❌ 错误：未设置 ENCRYPTION_KEY 环境变量")
    print("   请复制 .env.example 为 .env 并设置 ENCRYPTION_KEY")
    print("   生成方法：python -c \"import secrets; print(secrets.token_hex(32))\"")
    sys.exit(1)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/bidding.db")

# CORS 配置
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# 速率限制
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 5))
