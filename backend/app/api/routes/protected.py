"""
受保护的 API 路由示例
演示认证中间件的使用
"""
from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_current_active_user
from backend.app.models.user import User, UserResponse

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    获取用户个人资料（需要认证）
    
    Args:
        current_user: 当前活跃用户
        
    Returns:
        UserResponse: 用户个人资料
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_active_user)):
    """
    获取用户仪表板数据（需要认证）
    
    Args:
        current_user: 当前活跃用户
        
    Returns:
        dict: 仪表板数据
    """
    return {
        "message": f"欢迎回来, {current_user.username}!",
        "user_id": current_user.id,
        "dashboard_data": {
            "total_knowledge_items": 0,  # 后续会实现
            "recent_activity": [],       # 后续会实现
            "ai_conversations": 0        # 后续会实现
        }
    }


@router.get("/admin")
async def admin_only(current_user: User = Depends(get_current_active_user)):
    """
    管理员专用接口（需要认证和特定权限）
    
    Args:
        current_user: 当前活跃用户
        
    Returns:
        dict: 管理员信息
        
    Note: 这里只是示例，实际应用中需要更复杂的权限检查
    """
    # 简单的权限检查示例
    if current_user.username != "admin":
        return {
            "message": "权限不足，需要管理员权限",
            "has_access": False
        }
    
    return {
        "message": "欢迎管理员",
        "has_access": True,
        "admin_tools": [
            "用户管理",
            "系统监控", 
            "数据备份"
        ]
    }