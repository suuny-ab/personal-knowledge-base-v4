"""
用户数据库单元测试
测试数据库连接和 CRUD 操作
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.user_db import (
    User, hash_password, verify_password,
    get_user_by_username, get_user_by_email, create_user,
    update_user_github_info, init_db, get_session
)


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    # 初始化测试数据库
    await init_db()
    
    async with get_session() as session:
        yield session


@pytest.mark.asyncio
async def test_hash_password():
    """测试密码哈希"""
    password = "Password123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert isinstance(hashed, str)
    assert len(hashed) > 0


@pytest.mark.asyncio
async def test_verify_password_success():
    """测试密码验证成功"""
    password = "Password123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


@pytest.mark.asyncio
async def test_verify_password_failure():
    """测试密码验证失败"""
    password1 = "Password123"
    password2 = "WrongPassword"
    hashed = hash_password(password1)
    
    assert verify_password(password2, hashed) is False


@pytest.mark.asyncio
async def test_create_user_success(db_session: AsyncSession):
    """测试成功创建用户"""
    user = await create_user(
        session=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Password123")
    )
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_create_user_duplicate_username(db_session: AsyncSession):
    """测试重复用户名"""
    await create_user(
        session=db_session,
        username="testuser",
        email="test1@example.com",
        hashed_password=hash_password("Password123")
    )
    
    # 尝试创建相同用户名应该失败（数据库约束）
    with pytest.raises(Exception):
        await create_user(
            session=db_session,
            username="testuser",  # 重复
            email="test2@example.com",
            hashed_password=hash_password("Password456")
        )


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession):
    """测试根据用户名获取用户"""
    # 先创建用户
    created_user = await create_user(
        session=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Password123")
    )
    
    # 查询用户
    found_user = await get_user_by_username(db_session, "testuser")
    
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(db_session: AsyncSession):
    """测试查询不存在的用户"""
    user = await get_user_by_username(db_session, "nonexistent")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """测试根据邮箱获取用户"""
    # 先创建用户
    created_user = await create_user(
        session=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Password123")
    )
    
    # 查询用户
    found_user = await get_user_by_email(db_session, "test@example.com")
    
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_update_user_github_info(db_session: AsyncSession):
    """测试更新 GitHub 信息"""
    # 先创建用户
    user = await create_user(
        session=db_session,
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Password123")
    )
    
    # 更新 GitHub 信息
    updated_user = await update_user_github_info(
        session=db_session,
        user_id=user.id,
        github_token="ghp_test_token",
        github_repo="test/repo"
    )
    
    assert updated_user is not None
    assert updated_user.github_token == "ghp_test_token"
    assert updated_user.github_repo == "test/repo"
