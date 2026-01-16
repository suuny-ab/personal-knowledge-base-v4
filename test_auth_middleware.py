"""
认证中间件功能验证脚本
"""
import asyncio
from datetime import datetime
from backend.app.database.user_db import init_db, create_user, get_user_by_username, hash_password, get_session
from backend.app.core.security import create_access_token, verify_token


async def test_auth_middleware():
    print("🚀 开始认证中间件功能验证...")
    
    try:
        # 初始化数据库
        await init_db()
        print("✅ 数据库初始化成功")
        
        # 获取数据库会话
        session_gen = get_session()
        session = await anext(session_gen)
        
        # 使用唯一的时间戳创建测试用户
        timestamp = datetime.now().strftime("%H%M%S")
        username = f"testuser_{timestamp}"
        email = f"test{timestamp}@example.com"
        
        # 创建测试用户
        hashed_pwd = hash_password('Password123')
        user = await create_user(
            session=session,
            username=username, 
            email=email, 
            hashed_password=hashed_pwd
        )
        print(f"✅ 用户创建成功: {user.username}")
        
        # 生成JWT令牌
        token = create_access_token({'sub': user.username})
        print(f"✅ JWT令牌生成成功: {token[:20]}...")
        
        # 验证令牌
        token_data = verify_token(token)
        if token_data and token_data.username == user.username:
            print("✅ JWT令牌验证成功")
        else:
            print("❌ JWT令牌验证失败")
            return False
        
        # 测试获取用户
        db_user = await get_user_by_username(session, user.username)
        if db_user and db_user.username == user.username:
            print("✅ 用户检索成功")
        else:
            print("❌ 用户检索失败")
            return False
        
        # 测试依赖注入功能
        from backend.app.api.dependencies import get_current_user
        print("✅ 认证中间件依赖导入成功")
        
        # 测试API路由导入
        from backend.app.api.routes import auth, protected
        print("✅ API路由模块导入成功")
        
        # 测试FastAPI应用
        from backend.app.main import app
        print(f"✅ FastAPI应用导入成功: {app.title}")
        
        # 清理测试数据
        from sqlalchemy import delete
        from backend.app.database.user_db import User
        await session.execute(delete(User).where(User.username == username))
        await session.commit()
        await session.close()
        
        print("\n🎉 所有认证中间件功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_auth_middleware())
    exit(0 if success else 1)