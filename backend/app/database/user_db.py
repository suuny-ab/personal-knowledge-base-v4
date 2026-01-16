"""
用户数据库连接和操作
使用 SQLAlchemy 2.0 实现 SQLite 异步数据库
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from contextlib import asynccontextmanager
from datetime import datetime
import bcrypt
from typing import Optional
import os

# 数据库 URL
DATABASE_URL = "sqlite+aiosqlite:///./data/users/users.db"

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 声明基类
class Base(DeclarativeBase):
    pass


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    github_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_repo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


async def init_db():
    """初始化数据库，创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        yield session


def hash_password(password: str) -> str:
    """
    使用 bcrypt 哈希密码
    
    Args:
        password: 明文密码
    
    Returns:
        哈希后的密码
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
    
    Returns:
        密码是否匹配
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await session.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, username: str, email: str, hashed_password: str) -> User:
    """
    创建新用户
    
    Args:
        session: 数据库会话
        username: 用户名
        email: 邮箱
        hashed_password: 哈希后的密码
    
    Returns:
        创建的用户对象
    """
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_github_info(
    session: AsyncSession,
    user_id: int,
    github_token: Optional[str] = None,
    github_repo: Optional[str] = None
) -> Optional[User]:
    """
    更新用户的 GitHub 信息
    
    Args:
        session: 数据库会话
        user_id: 用户 ID
        github_token: GitHub 访问令牌
        github_repo: GitHub 仓库名称
    
    Returns:
        更新后的用户对象
    """
    user = await get_user_by_id(session, user_id)
    if user:
        if github_token is not None:
            user.github_token = github_token
        if github_repo is not None:
            user.github_repo = github_repo
        user.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(user)
    return user
