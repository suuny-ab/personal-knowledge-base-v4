"""
用户认证集成测试
测试完整的认证流程
"""
import pytest
import asyncio
from backend.app.models.user import User, UserCreate
from backend.app.database.user_db import (
    init_db, get_session, get_user_by_username,
    create_user, hash_password
)
from backend.app.core.security import (
    create_access_token, verify_token, create_access_token
)


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    await init_db()
    async with get_session() as session:
        yield session


@pytest.mark.asyncio
async def test_complete_registration_flow(db_session):
    """测试完整注册流程"""
    # 创建用户
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Password123"
    )
    user = await create_user(
        session=db_session,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    # 验证用户已创建
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    
    # 生成令牌
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    token = create_access_token(data=token_data)
    
    # 验证令牌
    assert token is not None
    assert len(token) > 0
    
    # 验证令牌
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded.username == "testuser"
    assert decoded.user_id == user.id


@pytest.mark.asyncio
async def test_token_generation(db_session):
    """测试令牌生成"""
    # 创建测试用户
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Password123"
    )
    user = await create_user(
        session=db_session,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    # 生成令牌
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    token = create_access_token(data=token_data)
    
    # 验证令牌不为空
    assert token is not None
    assert len(token) > 0


@pytest.mark.asyncio
async def test_token_verification_valid(db_session):
    """测试有效令牌验证"""
    # 创建用户并生成令牌
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Password123"
    )
    user = await create_user(
        session=db_session,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    token_data = {
        "sub": user.username,
        "user_id": user.id
    }
    token = create_access_token(data=token_data)
    
    # 验证令牌
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded.username == "testuser"
    assert decoded.user_id == user.id


@pytest.mark.asyncio
async def test_token_verification_invalid(db_session):
    """测试无效令牌验证"""
    invalid_token = "invalid.token.here"
    decoded = verify_token(invalid_token)
    assert decoded is None
