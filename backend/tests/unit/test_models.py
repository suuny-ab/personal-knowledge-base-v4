"""
用户模型单元测试
测试 Pydantic v2 模型的验证逻辑
"""
import pytest
from backend.app.models.user import (
    UserBase, UserCreate, UserUpdate, User, UserLogin,
    UserResponse, Token, TokenData
)


def test_user_base_valid():
    """测试 UserBase 模型验证"""
    user = UserBase(
        username="testuser",
        email="test@example.com",
        github_token=None,
        github_repo=None
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_base_invalid_email():
    """测试无效邮箱"""
    with pytest.raises(Exception):
        UserBase(
            username="testuser",
            email="invalid-email",  # 无效的邮箱格式
            github_token=None,
            github_repo=None
        )


def test_user_create_valid_password():
    """测试有效密码创建"""
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Password123"  # 有效密码：大小写 + 数字
    )
    assert user.password == "Password123"


def test_user_create_missing_uppercase():
    """测试缺少大写字母"""
    with pytest.raises(ValueError, match="大写字母"):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"  # 只有小写
        )


def test_user_create_missing_lowercase():
    """测试缺少小写字母"""
    with pytest.raises(ValueError, match="小写字母"):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="PASSWORD123"  # 只有大写
        )


def test_user_create_missing_digit():
    """测试缺少数字"""
    with pytest.raises(ValueError, match="数字"):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="PasswordABC"  # 没有数字
        )


def test_user_create_short_password():
    """测试密码过短"""
    with pytest.raises(Exception):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="Pass1"  # 少于 8 位
        )


def test_user_create_short_username():
    """测试用户名过短"""
    with pytest.raises(Exception):
        UserCreate(
            username="ab",  # 少于 3 位
            email="test@example.com",
            password="Password123"
        )


def test_user_create_invalid_username_special():
    """测试用户名包含特殊字符"""
    with pytest.raises(ValueError, match="字母、数字和下划线"):
        UserCreate(
            username="test@user",  # 包含 @ 符号
            email="test@example.com",
            password="Password123"
        )


def test_user_update_partial():
    """测试部分更新用户"""
    user = UserUpdate(
        email="new@example.com",
        github_token="new_token"
    )
    assert user.email == "new@example.com"
    assert user.github_token == "new_token"
    assert user.github_repo is None


def test_token_model():
    """测试 Token 模型"""
    token = Token(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        token_type="bearer"
    )
    assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    assert token.token_type == "bearer"


def test_user_response():
    """测试 UserResponse 模型"""
    from datetime import datetime
    
    user_response = UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        github_token=None,
        github_repo=None,
        created_at=datetime.utcnow(),
        is_active=True
    )
    assert user_response.id == 1
    assert user_response.username == "testuser"
    assert user_response.hashed_password is None  # 响应模型不包含密码
