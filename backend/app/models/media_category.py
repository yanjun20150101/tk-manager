"""
素材分类模型
存储素材分类信息
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MediaCategory(Base):
    """素材分类模型"""
    __tablename__ = "media_categories"
    
    id = Column(Integer, primary_key=True, index=True, comment="分类ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="创建用户ID")
    
    # 分类信息
    name = Column(String(100), nullable=False, comment="分类名称")
    description = Column(Text, comment="分类描述")
    color = Column(String(20), comment="分类颜色标识")
    icon = Column(String(50), comment="分类图标")
    
    # 父分类（支持二级分类）
    parent_id = Column(Integer, ForeignKey('media_categories.id', ondelete='CASCADE'), comment="父分类ID")
    
    # 排序和状态
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", backref="media_categories")
    parent = relationship("MediaCategory", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<MediaCategory(id={self.id}, name='{self.name}')>"
