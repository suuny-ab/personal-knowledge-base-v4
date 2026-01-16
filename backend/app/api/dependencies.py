"""
认证中间件依赖
提供 FastAPI 依赖注入的认证功能
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from backend.app.core.security import verify_token
from backend.app.database.user_db import get_user_by_username
from backend.app.models.user import User

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    获取当前认证用户
    
    Args:
        credentials: HTTP Bearer 令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 令牌无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 验证 JWT 令牌
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（检查用户是否激活）
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 活跃用户对象
        
    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户未激活"
        )
    return current_user


async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    可选的认证依赖
    如果提供了有效令牌则返回用户，否则返回 None
    
    Args:
        credentials: 可选的 HTTP Bearer 令牌
        
    Returns:
        Optional[User]: 用户对象或 None
    """
    if not credentials:
        return None
        
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
            
        username: str = payload.get("sub")
        if username is None:
            return None
            
        user = await get_user_by_username(username)
        return user
        
    except JWTError:
        return None