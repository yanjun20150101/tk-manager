"""
定时任务相关的Pydantic模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.scheduled_task import TaskStatus, TaskType


class TaskCreate(BaseModel):
    """创建任务请求"""
    task_type: TaskType = Field(..., description="任务类型")
    task_name: Optional[str] = Field(None, max_length=200, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    scheduled_time: datetime = Field(..., description="计划执行时间")
    task_params: Dict[str, Any] = Field(..., description="任务参数")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")


class TaskUpdate(BaseModel):
    """更新任务请求"""
    task_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    task_params: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    user_id: int
    task_type: str
    task_name: Optional[str]
    description: Optional[str]
    scheduled_time: datetime
    executed_time: Optional[datetime]
    status: str
    task_params: Optional[Dict[str, Any]]
    result_message: Optional[str]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    publish_record_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    color: Optional[str] = Field(None, max_length=20, description="颜色标识")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(default=0, description="排序顺序")


class CategoryUpdate(BaseModel):
    """更新分类请求"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=20)
    icon: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """分类响应"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    parent_id: Optional[int]
    sort_order: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
