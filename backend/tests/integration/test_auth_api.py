"""
认证API集成测试
测试认证中间件和API端点的功能
"""
import pytest
import time
from fastapi.testclient import TestClient

from backend.app.main import app

# 创建同步测试客户端（兼容FastAPI 0.128.0）
client = TestClient(app=app)

# 生成唯一的测试用户名
def get_unique_username(base_name):
    """生成唯一的用户名，避免测试冲突"""
    timestamp = int(time.time() * 1000)
    return f"{base_name}_{timestamp}"


def test_root_endpoint():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "欢迎使用个人知识库智能管理系统" in data["message"]


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    """测试用户注册"""
    unique_name = get_unique_username("testuser")
    user_data = {
        "username": unique_name,
        "email": f"{unique_name}@example.com",
        "password": "Password123"
    }
    
    response = client.post("/auth/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == unique_name
    assert data["email"] == f"{unique_name}@example.com"
    assert "id" in data


def test_register_duplicate_username():
    """测试重复用户名注册"""
    unique_name = get_unique_username("testuser2")
    user_data = {
        "username": unique_name,
        "email": f"{unique_name}@example.com",
        "password": "Password123"
    }
    
    # 第一次注册
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # 第二次注册相同用户名
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "用户名已存在" in response2.json()["detail"]


def test_login_success():
    """测试成功登录"""
    unique_name = get_unique_username("testuser3")
    # 先注册用户
    user_data = {
        "username": unique_name,
        "email": f"{unique_name}@example.com",
        "password": "Password123"
    }
    client.post("/auth/register", json=user_data)
    
    # 登录
    login_data = {
        "username": unique_name,
        "password": "Password123"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_wrong_password():
    """测试密码错误登录"""
    unique_name = get_unique_username("testuser4")
    # 先注册用户
    user_data = {
        "username": unique_name,
        "email": f"{unique_name}@example.com",
        "password": "Password123"
    }
    client.post("/auth/register", json=user_data)
    
    # 使用错误密码登录
    login_data = {
        "username": unique_name,
        "password": "WrongPassword"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


def test_protected_endpoint_without_token():
    """测试未认证访问受保护端点"""
    response = client.get("/protected/profile")
    
    # FastAPI 默认返回 401 而不是 403
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_protected_endpoint_with_valid_token():
    """测试带有效令牌访问受保护端点"""
    unique_name = get_unique_username("testuser5")
    # 注册并登录获取令牌
    user_data = {
        "username": unique_name,
        "email": f"{unique_name}@example.com",
        "password": "Password123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": unique_name,
        "password": "Password123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # 使用令牌访问受保护端点
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected/profile", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == unique_name


def test_invalid_token():
    """测试无效令牌"""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/protected/profile", headers=headers)
    
    assert response.status_code == 401
    assert "无效的认证凭据" in response.json()["detail"]