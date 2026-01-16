"""
用户数据模型
使用 Pydantic v2 定义用户相关的数据模型
"""
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    github_token: Optional[str] = Field(None, description="GitHub 访问令牌")
    github_repo: Optional[str] = Field(None, description="GitHub 仓库名称")


class UserCreate(UserBase):
    """用户创建模型（注册）"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码"
    )
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        """验证用户名只包含字母、数字和下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """验证密码强度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    github_token: Optional[str] = None
    github_repo: Optional[str] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    """用户响应模型（不包含敏感信息）"""
    id: int
    created_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")


class TokenData(BaseModel):
    """Token 数据模型（用于解码）"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    """通用用户响应模型"""
    id: int
    username: str
    email: str
    github_token: Optional[str] = None
    github_repo: Optional[str] = None
    created_at: datetime
    is_active: bool = True
