"""
定时任务模型
存储定时发布任务信息
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 待执行
    RUNNING = "running"          # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"      # 已取消


class TaskType(str, enum.Enum):
    """任务类型枚举"""
    PUBLISH_VIDEO = "publish_video"      # 发布视频
    REFRESH_TOKEN = "refresh_token"      # 刷新令牌
    CHECK_STATUS = "check_status"        # 检查发布状态


class ScheduledTask(Base):
    """定时任务模型"""
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment="创建用户ID")
    
    # 任务信息
    task_type = Column(Enum(TaskType), nullable=False, comment="任务类型")
    task_name = Column(String(200), comment="任务名称")
    description = Column(Text, comment="任务描述")
    
    # 执行时间
    scheduled_time = Column(DateTime(timezone=True), nullable=False, comment="计划执行时间")
    executed_time = Column(DateTime(timezone=True), comment="实际执行时间")
    
    # 任务状态
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, comment="任务状态")
    
    # 任务参数（JSON格式存储具体参数）
    task_params = Column(JSON, comment="任务参数")
    
    # 执行结果
    result_message = Column(Text, comment="执行结果消息")
    error_message = Column(Text, comment="错误信息")
    
    # 重试配置
    retry_count = Column(Integer, default=0, comment="已重试次数")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    
    # 关联发布记录（用于发布任务）
    publish_record_id = Column(Integer, ForeignKey('publish_records.id', ondelete='SET NULL'), comment="关联的发布记录ID")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", backref="scheduled_tasks")
    publish_record = relationship("PublishRecord", backref="scheduled_tasks")
    
    def __repr__(self):
        return f"<ScheduledTask(id={self.id}, type='{self.task_type}', status='{self.status}')>"
