"""
数据库连接模块
管理MySQL和Redis的连接
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
from typing import Generator
from .config import settings

# 创建SQLAlchemy引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间（1小时）
    echo=settings.DEBUG  # 调试模式下打印SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
Base = declarative_base()

# Redis连接实例
redis_client: Redis = None


def get_redis() -> Redis:
    """获取Redis客户端实例"""
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True  # 自动解码响应为字符串
        )
    return redis_client


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    使用依赖注入，自动管理会话生命周期
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    # 导入所有模型以确保它们被注册
    from app.models import user  # noqa: F401
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功！")


def close_db():
    """关闭数据库连接"""
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None
    engine.dispose()
    print("数据库连接已关闭！")
