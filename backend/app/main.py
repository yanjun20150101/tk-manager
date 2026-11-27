"""
FastAPI主应用入口
配置应用、中间件、路由等
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import settings, init_db, close_db
from app.routers import auth_router, tiktok_router, media_router, publish_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    print("正在初始化数据库...")
    init_db()
    print("应用启动完成！")
    
    yield
    
    # 关闭时执行
    print("正在关闭数据库连接...")
    close_db()
    print("应用已关闭！")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="TikTok账号管理系统 - 后端API",
    docs_url="/api/docs",  # Swagger文档
    redoc_url="/api/redoc",  # ReDoc文档
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 允许的源
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tiktok_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(publish_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "欢迎使用TikTok账号管理系统API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    # 运行应用
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # 开发模式下启用热重载
    )
