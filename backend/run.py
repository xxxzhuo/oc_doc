"""
启动脚本 - 统一入口
使用方法：
    python run.py
    或
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
"""
import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from config.settings import HOST, PORT, LOG_LEVEL


def main():
    """启动服务"""
    # 创建日志目录
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 检查环境变量
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  警告：未找到 .env 文件，将使用默认配置")
        print(f"   请复制 .env.example 为 .env 并配置必要的环境变量")
        print()
    
    print("🚀 启动暗标竞标系统...")
    print(f"   服务地址：http://{HOST}:{PORT}")
    print(f"   API 文档：http://{HOST}:{PORT}/docs")
    print(f"   日志级别：{LOG_LEVEL}")
    print()
    
    # 启动服务
    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
