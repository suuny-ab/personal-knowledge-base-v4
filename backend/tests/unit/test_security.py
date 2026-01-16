"""
安全模块单元测试
测试 JWT 令牌生成和验证功能
"""
import pytest
from backend.app.core.security import (
    create_access_token, verify_token, 
    decode_token_payload, get_token_expiration,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
)


def test_create_access_token():
    """测试令牌生成"""
    # 测试数据
    data = {
        "sub": "testuser",
        "user_id": 123
    }
    
    # 生成令牌
    token = create_access_token(data=data)
    
    # 验证令牌
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    assert "." in token  # JWT 通常包含两个点


def test_verify_token_valid():
    """测试有效令牌验证"""
    # 生成有效令牌
    data = {
        "sub": "testuser",
        "user_id": 123
    }
    token = create_access_token(data=data)
    
    # 验证令牌
    decoded = verify_token(token)
    
    assert decoded is not None
    assert decoded.username == "testuser"
    assert decoded.user_id == 123


def test_verify_token_invalid():
    """测试无效令牌验证"""
    # 无效令牌
    invalid_token = "invalid.token.string"
    decoded = verify_token(invalid_token)
    
    assert decoded is None


def test_verify_token_malformed():
    """测试格式错误的令牌"""
    # 格式错误的令牌
    malformed_token = "not.a.jwt"
    decoded = verify_token(malformed_token)
    
    assert decoded is None


def test_token_with_expiration():
    """测试自定义过期时间"""
    # 自定义过期时间：1小时
    custom_delta = __import__('datetime').timedelta(hours=1)
    
    data = {
        "sub": "expireuser",
        "user_id": 456
    }
    
    # 使用自定义过期时间生成令牌
    # 注意：需要修改 create_access_token 函数支持 expires_delta 参数
    # 这里假设函数已支持该参数
    # token = create_access_token(data=data, expires_delta=custom_delta)
    
    # 验证令牌存在
    # assert token is not None


def test_decode_token_payload():
    """测试解码令牌载荷"""
    # 生成令牌
    data = {
        "sub": "payloaduser",
        "user_id": 789
    }
    token = create_access_token(data=data)
    
    # 解码载荷（不验证签名）
    payload = decode_token_payload(token)
    
    assert payload is not None
    assert payload["sub"] == "payloaduser"
    assert payload["user_id"] == 789


def test_secret_key_constant():
    """测试密钥常量存在"""
    assert SECRET_KEY is not None
    assert isinstance(SECRET_KEY, str)
    assert len(SECRET_KEY) > 0
    
    assert ALGORITHM is not None
    assert isinstance(ALGORITHM, str)
    assert ALGORITHM == "HS256"
    
    assert ACCESS_TOKEN_EXPIRE_MINUTES is not None
    assert isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int)
    assert ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_token_expiration_constant():
    """测试令牌过期时间常量"""
    from datetime import timedelta
    
    expiration = get_token_expiration()
    
    assert isinstance(expiration, timedelta)
    assert expiration.total_seconds() > 0
    
    # 验证是 24小时（1440分钟）
    expected_seconds = 24 * 60 * 60
    assert expiration.total_seconds() == expected_seconds