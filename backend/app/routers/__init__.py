"""路由模块初始化"""
from .auth import router as auth_router
from .tiktok import router as tiktok_router
from .media import router as media_router
from .publish import router as publish_router
from .tasks import router as tasks_router
from .categories import router as categories_router

__all__ = [
    "auth_router",
    "tiktok_router",
    "media_router",
    "publish_router",
    "tasks_router",
    "categories_router",
]
