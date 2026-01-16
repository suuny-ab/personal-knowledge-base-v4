"""
FastAPI 主应用
个人知识库智能管理系统后端 API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import auth, protected
from backend.app.database.user_db import init_db

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Personal Knowledge Base API",
    description="个人知识库智能管理系统后端 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(protected.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    await init_db()


@app.get("/")
async def root():
    """根路径，返回 API 基本信息"""
    return {
        "message": "欢迎使用个人知识库智能管理系统",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "认证": "/auth",
            "受保护接口": "/protected"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "API 运行正常"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)