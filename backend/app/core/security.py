"""
JWT 认证和授权工具
使用 python-jose 实现 JWT 令牌生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.app.models.user import TokenData

# 密钥配置（实际应从环境变量读取）
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据（通常包含用户信息）
        expires_delta: 令牌过期时间（可选）
    
    Returns:
        编码后的 JWT 令牌
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 编码 JWT
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    验证并解码令牌
    
    Args:
        token: JWT 令牌
    
    Returns:
        解码后的 TokenData，如果验证失败返回 None
    """
    try:
        # 解码 JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # 提取用户信息
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            return None
        
        token_data = TokenData(
            username=username,
            user_id=user_id
        )
        return token_data
    
    except JWTError:
        return None


def decode_token_payload(token: str) -> Optional[dict]:
    """
    解码令牌载荷（不进行验证）
    
    Args:
        token: JWT 令牌
    
    Returns:
        解码后的字典，如果解码失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def get_token_expiration() -> timedelta:
    """
    获取令牌过期时间
    
    Returns:
        令牌过期时间间隔
    """
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
