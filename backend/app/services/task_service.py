"""
任务管理服务
处理定时任务的CRUD操作
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import ScheduledTask, TaskStatus, TaskType
from app.services.scheduler_service import SchedulerService


class TaskService:
    """任务管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scheduler_service = SchedulerService()
    
    def create_task(
        self,
        user_id: int,
        task_type: TaskType,
        scheduled_time: datetime,
        task_params: dict,
        task_name: Optional[str] = None,
        description: Optional[str] = None,
        max_retries: int = 3
    ) -> ScheduledTask:
        """
        创建定时任务
        
        Args:
            user_id: 用户ID
            task_type: 任务类型
            scheduled_time: 计划执行时间
            task_params: 任务参数
            task_name: 任务名称
            description: 任务描述
            max_retries: 最大重试次数
        
        Returns:
            ScheduledTask对象
        """
        # 检查时间是否在未来
        if scheduled_time <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划执行时间必须在未来"
            )
        
        # 创建任务
        task = ScheduledTask(
            user_id=user_id,
            task_type=task_type,
            task_name=task_name,
            description=description,
            scheduled_time=scheduled_time,
            task_params=task_params,
            max_retries=max_retries
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        # 添加到调度器
        try:
            self.scheduler_service.schedule_task(task)
        except Exception as e:
            # 如果调度失败，删除任务
            self.db.delete(task)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"任务调度失败: {str(e)}"
            )
        
        return task
    
    def get_task(self, task_id: int, user_id: int) -> Optional[ScheduledTask]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            ScheduledTask对象或None
        """
        return self.db.query(ScheduledTask).filter(
            ScheduledTask.id == task_id,
            ScheduledTask.user_id == user_id
        ).first()
    
    def list_tasks(
        self,
        user_id: int,
        task_type: Optional[TaskType] = None,
        status_filter: Optional[TaskStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple:
        """
        获取任务列表
        
        Args:
            user_id: 用户ID
            task_type: 任务类型过滤
            status_filter: 状态过滤
            page: 页码
            page_size: 每页数量
        
        Returns:
            (总数, 任务列表)元组
        """
        query = self.db.query(ScheduledTask).filter(ScheduledTask.user_id == user_id)
        
        # 应用过滤条件
        if task_type:
            query = query.filter(ScheduledTask.task_type == task_type)
        
        if status_filter:
            query = query.filter(ScheduledTask.status == status_filter)
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        items = query.order_by(ScheduledTask.scheduled_time.desc()).offset(offset).limit(page_size).all()
        
        return total, items
    
    def cancel_task(self, task_id: int, user_id: int) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        task = self.get_task(task_id, user_id)
        
        if not task:
            return False
        
        # 只能取消待执行的任务
        if task.status != TaskStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能取消待执行的任务"
            )
        
        # 从调度器中移除
        self.scheduler_service.cancel_task(task_id)
        
        # 更新任务状态
        task.status = TaskStatus.CANCELLED
        self.db.commit()
        
        return True
    
    def update_task(
        self,
        task_id: int,
        user_id: int,
        scheduled_time: Optional[datetime] = None,
        task_params: Optional[dict] = None,
        task_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> ScheduledTask:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
            scheduled_time: 新的计划执行时间
            task_params: 新的任务参数
            task_name: 新的任务名称
            description: 新的描述
        
        Returns:
            更新后的ScheduledTask对象
        """
        task = self.get_task(task_id, user_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        # 只能更新待执行的任务
        if task.status != TaskStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能更新待执行的任务"
            )
        
        # 更新字段
        if task_name is not None:
            task.task_name = task_name
        
        if description is not None:
            task.description = description
        
        if task_params is not None:
            task.task_params = task_params
        
        # 如果更新了执行时间，需要重新调度
        if scheduled_time is not None:
            if scheduled_time <= datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="计划执行时间必须在未来"
                )
            
            task.scheduled_time = scheduled_time
            
            # 取消旧的调度
            self.scheduler_service.cancel_task(task_id)
            
            # 重新调度
            self.scheduler_service.schedule_task(task)
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        task = self.get_task(task_id, user_id)
        
        if not task:
            return False
        
        # 如果任务还在待执行状态，先取消调度
        if task.status == TaskStatus.PENDING:
            self.scheduler_service.cancel_task(task_id)
        
        # 删除任务
        self.db.delete(task)
        self.db.commit()
        
        return True
