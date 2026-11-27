"""
发布记录模型
存储内容发布到TikTok的记录
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PublishStatus(str, enum.Enum):
    """发布状态枚举"""
    PENDING = "pending"          # 待发布
    UPLOADING = "uploading"      # 上传中
    PROCESSING = "processing"    # 处理中
    PUBLISHED = "published"      # 已发布
    FAILED = "failed"           # 失败
    SCHEDULED = "scheduled"      # 已定时


class PrivacyLevel(str, enum.Enum):
    """隐私级别枚举"""
    PUBLIC = "PUBLIC_TO_EVERYONE"           # 所有人可见
    FRIENDS = "MUTUAL_FOLLOW_FRIENDS"       # 好友可见
    SELF = "SELF_ONLY"                      # 仅自己可见


class PublishRecord(Base):
    """发布记录模型"""
    __tablename__ = "publish_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="发布记录ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="发布用户ID")
    tiktok_account_id = Column(Integer, ForeignKey('tiktok_accounts.id', ondelete='CASCADE'), nullable=False, comment="TikTok账号ID")
    media_id = Column(Integer, ForeignKey('media.id', ondelete='SET NULL'), comment="素材ID")
    
    # 发布内容
    title = Column(String(500), comment="标题")
    description = Column(Text, comment="描述")
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PUBLIC, comment="隐私级别")
    
    # 发布设置
    disable_comment = Column(Boolean, default=False, comment="是否禁用评论")
    disable_duet = Column(Boolean, default=False, comment="是否禁用合拍")
    disable_stitch = Column(Boolean, default=False, comment="是否禁用拼接")
    video_cover_timestamp_ms = Column(Integer, comment="视频封面时间戳（毫秒）")
    
    # TikTok响应信息
    publish_id = Column(String(100), unique=True, index=True, comment="TikTok发布ID")
    share_url = Column(String(500), comment="分享链接")
    embed_html = Column(Text, comment="嵌入HTML")
    embed_link = Column(String(500), comment="嵌入链接")
    
    # 状态信息
    status = Column(Enum(PublishStatus), default=PublishStatus.PENDING, comment="发布状态")
    error_code = Column(String(50), comment="错误代码")
    error_message = Column(Text, comment="错误信息")
    
    # 定时发布
    scheduled_time = Column(DateTime(timezone=True), comment="定时发布时间")
    published_at = Column(DateTime(timezone=True), comment="实际发布时间")
    
    # 额外数据
    metadata = Column(JSON, comment="额外元数据")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", backref="publish_records")
    tiktok_account = relationship("TikTokAccount", backref="publish_records")
    media = relationship("Media", backref="publish_records")
    
    def __repr__(self):
        return f"<PublishRecord(id={self.id}, publish_id='{self.publish_id}', status='{self.status}')>"
