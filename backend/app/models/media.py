"""
素材模型
存储视频和图片素材信息
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class MediaType(str, enum.Enum):
    """素材类型枚举"""
    VIDEO = "video"
    IMAGE = "image"


class MediaStatus(str, enum.Enum):
    """素材状态枚举"""
    UPLOADING = "uploading"      # 上传中
    PROCESSING = "processing"    # 处理中（转码、生成缩略图等）
    COMPLETED = "completed"      # 完成
    FAILED = "failed"           # 失败


class Media(Base):
    """素材模型"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True, comment="素材ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="上传用户ID")
    
    # 基本信息
    title = Column(String(200), comment="素材标题")
    description = Column(Text, comment="素材描述")
    media_type = Column(Enum(MediaType), nullable=False, comment="素材类型")
    status = Column(Enum(MediaStatus), default=MediaStatus.UPLOADING, comment="素材状态")
    
    # 文件信息
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(BigInteger, comment="文件大小（字节）")
    mime_type = Column(String(100), comment="MIME类型")
    file_hash = Column(String(64), index=True, comment="文件MD5哈希")
    
    # 视频专用字段
    duration = Column(Integer, comment="视频时长（秒）")
    width = Column(Integer, comment="视频宽度")
    height = Column(Integer, comment="视频高度")
    frame_rate = Column(String(20), comment="帧率")
    bitrate = Column(Integer, comment="比特率")
    codec = Column(String(50), comment="编码格式")
    
    # 缩略图
    thumbnail_path = Column(String(500), comment="缩略图路径")
    
    # 分类和标签
    category_id = Column(Integer, ForeignKey('media_categories.id', ondelete='SET NULL'), comment="分类ID")
    category = Column(String(50), comment="分类名称（冗余字段）")
    tags = Column(Text, comment="标签（JSON数组）")
    
    # 状态信息
    error_message = Column(Text, comment="错误信息")
    process_progress = Column(Integer, default=0, comment="处理进度（0-100）")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", backref="media")
    media_category = relationship("MediaCategory", backref="media")
    
    def __repr__(self):
        return f"<Media(id={self.id}, title='{self.title}', type='{self.media_type}')>"
