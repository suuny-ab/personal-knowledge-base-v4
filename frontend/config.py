"""
前端配置文件
统一管理 API 端点、UI 设置和其他配置
"""
from typing import Dict, Any

# ========================================
# API 配置
# ========================================
API_BASE_URL = "http://localhost:8000"

API_ENDPOINTS = {
    # 认证相关
    "auth": {
        "register": f"{API_BASE_URL}/auth/register",
        "login": f"{API_BASE_URL}/auth/login",
        "verify": f"{API_BASE_URL}/auth/verify",
    },
    # 知识库管理
    "kb": {
        "list": f"{API_BASE_URL}/kb/list",
        "upload": f"{API_BASE_URL}/kb/upload",
        "delete": f"{API_BASE_URL}/kb/delete",
        "parse": f"{API_BASE_URL}/kb/parse",
    },
    # RAG 检索
    "rag": {
        "query": f"{API_BASE_URL}/rag/query",
        "contexts": f"{API_BASE_URL}/rag/contexts",
    },
    # AI 对话
    "ai": {
        "chat": f"{API_BASE_URL}/ai/chat",
        "history": f"{API_BASE_URL}/ai/history",
        "switch_model": f"{API_BASE_URL}/ai/switch-model",
    },
    # 知识整合
    "integration": {
        "synthesize": f"{API_BASE_URL}/integration/synthesize",
        "optimize": f"{API_BASE_URL}/integration/optimize",
    },
    # GitHub 同步
    "github": {
        "bind": f"{API_BASE_URL}/github/bind",
        "sync": f"{API_BASE_URL}/github/sync",
        "status": f"{API_BASE_URL}/github/status",
    },
}

# ========================================
# UI 配置
# ========================================
UI_CONFIG = {
    # 页面标题
    "app_title": "个人知识库智能管理系统",
    
    # 主题配置
    "theme": {
        "primaryColor": "#1E3A8A",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F3F4F6",
        "textColor": "#1F2937",
        "font": "PingFang SC",
    },
    
    # 布局配置
    "layout": {
        "sidebar_width": 280,
        "content_max_width": 1200,
    },
    
    # 默认模型
    "default_llm": "deepseek-chat",
    "available_models": ["deepseek-chat", "deepseek-reasoner", "glm-4.7"],
}

# ========================================
# 存储配置
# ========================================
STORAGE_CONFIG = {
    # 本地存储键名
    "keys": {
        "token": "auth_token",
        "user_id": "user_id",
        "username": "username",
        "current_model": "current_llm_model",
        "theme": "theme_preference",
    },
}

# ========================================
# 功能配置
# ========================================
FEATURE_CONFIG = {
    # 分页配置
    "pagination": {
        "kb_page_size": 12,
        "search_page_size": 10,
        "chat_history_page_size": 20,
    },
    
    # 检索配置
    "search": {
        "top_k": 5,
        "min_score": 0.6,
    },
    
    # 对话配置
    "chat": {
        "max_history": 50,
        "context_limit": 4000,
    },
    
    # 同步配置
    "sync": {
        "auto_sync": False,
        "sync_interval": 300,  # 5 分钟
    },
}

# ========================================
# 错误消息
# ========================================
ERROR_MESSAGES = {
    "network_error": "网络连接失败，请检查网络设置",
    "auth_error": "认证失败，请重新登录",
    "server_error": "服务器错误，请稍后重试",
    "invalid_input": "输入格式不正确",
    "file_error": "文件上传失败",
}


def get_api_url(service: str, endpoint: str) -> str:
    """
    获取 API 端点 URL
    
    Args:
        service: 服务名称 (auth, kb, rag, ai, integration, github)
        endpoint: 端点名称
    
    Returns:
        完整的 API URL
    """
    return API_ENDPOINTS.get(service, {}).get(endpoint, "")


def get_theme_config() -> Dict[str, Any]:
    """
    获取 Streamlit 主题配置
    
    Returns:
        主题配置字典
    """
    return UI_CONFIG["theme"]


def get_feature_config(feature: str) -> Dict[str, Any]:
    """
    获取功能配置
    
    Args:
        feature: 功能名称 (pagination, search, chat, sync)
    
    Returns:
        功能配置字典
    """
    return FEATURE_CONFIG.get(feature, {})
