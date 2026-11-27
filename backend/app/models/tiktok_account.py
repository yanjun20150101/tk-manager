"""
TikTok账号模型
存储授权的TikTok账号信息和令牌
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TikTokAccount(Base):
    """TikTok账号模型"""
    __tablename__ = "tiktok_accounts"
    
    id = Column(Integer, primary_key=True, index=True, comment="账号ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="关联用户ID")
    
    # TikTok账号信息
    open_id = Column(String(100), unique=True, nullable=False, index=True, comment="TikTok OpenID")
    username = Column(String(100), comment="TikTok用户名")
    display_name = Column(String(100), comment="显示名称")
    avatar_url = Column(String(255), comment="头像URL")
    
    # 加密存储的访问令牌
    access_token_encrypted = Column(Text, nullable=False, comment="加密的访问令牌")
    access_token_iv = Column(String(32), nullable=False, comment="访问令牌加密IV")
    access_token_auth_tag = Column(String(32), nullable=False, comment="访问令牌认证标签")
    
    # 加密存储的刷新令牌
    refresh_token_encrypted = Column(Text, nullable=False, comment="加密的刷新令牌")
    refresh_token_iv = Column(String(32), nullable=False, comment="刷新令牌加密IV")
    refresh_token_auth_tag = Column(String(32), nullable=False, comment="刷新令牌认证标签")
    
    # 令牌信息
    token_type = Column(String(20), default="bearer", comment="令牌类型")
    scope = Column(String(255), comment="授权范围")
    expires_at = Column(DateTime(timezone=True), comment="访问令牌过期时间")
    refresh_expires_at = Column(DateTime(timezone=True), comment="刷新令牌过期时间")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否激活")
    last_refresh_at = Column(DateTime(timezone=True), comment="最后刷新时间")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", backref="tiktok_accounts")
    
    def __repr__(self):
        return f"<TikTokAccount(id={self.id}, open_id='{self.open_id}', username='{self.username}')>"
