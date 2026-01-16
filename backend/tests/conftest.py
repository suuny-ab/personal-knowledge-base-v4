"""
Pytest configuration for loading environment variables.
"""

import os
from pathlib import Path

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
