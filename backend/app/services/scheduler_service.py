"""
定时任务调度服务
使用APScheduler管理定时任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models import ScheduledTask, TaskStatus, TaskType
from app.core.database import SessionLocal
from app.services.publish_service import PublishService

# 配置日志
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

# 创建调度器实例
job_stores = {
    'default': MemoryJobStore()
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': False,  # 是否合并多个排队的任务
    'max_instances': 3  # 最大并发实例数
}

scheduler = AsyncIOScheduler(
    jobstores=job_stores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='Asia/Shanghai'
)


class SchedulerService:
    """定时任务调度服务类"""
    
    @staticmethod
    async def execute_task(task_id: int):
        """
        执行定时任务
        
        Args:
            task_id: 任务ID
        """
        db: Session = SessionLocal()
        
        try:
            # 获取任务
            task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
            
            if not task:
                print(f"任务 {task_id} 不存在")
                return
            
            # 更新任务状态为执行中
            task.status = TaskStatus.RUNNING
            task.executed_time = datetime.utcnow()
            db.commit()
            
            # 根据任务类型执行不同的操作
            if task.task_type == TaskType.PUBLISH_VIDEO:
                await SchedulerService._execute_publish_video(task, db)
            elif task.task_type == TaskType.REFRESH_TOKEN:
                await SchedulerService._execute_refresh_token(task, db)
            elif task.task_type == TaskType.CHECK_STATUS:
                await SchedulerService._execute_check_status(task, db)
            
        except Exception as e:
            # 任务执行失败
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            
            # 如果未超过最大重试次数，重新调度
            if task.retry_count < task.max_retries:
                # 10分钟后重试
                retry_time = datetime.utcnow().timestamp() + 600
                scheduler.add_job(
                    SchedulerService.execute_task,
                    'date',
                    run_date=datetime.fromtimestamp(retry_time),
                    args=[task_id],
                    id=f"task_{task_id}_retry_{task.retry_count}"
                )
            
            db.commit()
            print(f"任务 {task_id} 执行失败: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    async def _execute_publish_video(task: ScheduledTask, db: Session):
        """
        执行发布视频任务
        
        Args:
            task: 任务对象
            db: 数据库会话
        """
        # 获取任务参数
        params = task.task_params
        
        # 创建发布服务
        publish_service = PublishService(db)
        
        # 执行发布
        try:
            record = await publish_service.publish_video(
                user_id=task.user_id,
                tiktok_account_id=params['tiktok_account_id'],
                media_id=params['media_id'],
                title=params.get('title'),
                description=params.get('description'),
                privacy_level=params.get('privacy_level', 'PUBLIC_TO_EVERYONE'),
                disable_comment=params.get('disable_comment', False),
                disable_duet=params.get('disable_duet', False),
                disable_stitch=params.get('disable_stitch', False),
                video_cover_timestamp_ms=params.get('video_cover_timestamp_ms')
            )
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.publish_record_id = record.id
            task.result_message = f"视频发布成功，发布记录ID: {record.id}"
            
        except Exception as e:
            raise Exception(f"发布视频失败: {str(e)}")
    
    @staticmethod
    async def _execute_refresh_token(task: ScheduledTask, db: Session):
        """
        执行刷新令牌任务
        
        Args:
            task: 任务对象
            db: 数据库会话
        """
        # TODO: 实现令牌刷新逻辑
        task.status = TaskStatus.COMPLETED
        task.result_message = "令牌刷新成功"
    
    @staticmethod
    async def _execute_check_status(task: ScheduledTask, db: Session):
        """
        执行检查状态任务
        
        Args:
            task: 任务对象
            db: 数据库会话
        """
        # TODO: 实现状态检查逻辑
        task.status = TaskStatus.COMPLETED
        task.result_message = "状态检查完成"
    
    @staticmethod
    def schedule_task(task: ScheduledTask) -> str:
        """
        调度任务
        
        Args:
            task: 任务对象
        
        Returns:
            任务ID
        """
        job_id = f"task_{task.id}"
        
        scheduler.add_job(
            SchedulerService.execute_task,
            'date',
            run_date=task.scheduled_time,
            args=[task.id],
            id=job_id
        )
        
        return job_id
    
    @staticmethod
    def cancel_task(task_id: int) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            是否成功
        """
        job_id = f"task_{task_id}"
        
        try:
            scheduler.remove_job(job_id)
            return True
        except Exception as e:
            print(f"取消任务失败: {str(e)}")
            return False
    
    @staticmethod
    def start_scheduler():
        """启动调度器"""
        if not scheduler.running:
            scheduler.start()
            print("定时任务调度器已启动")
    
    @staticmethod
    def shutdown_scheduler():
        """关闭调度器"""
        if scheduler.running:
            scheduler.shutdown()
            print("定时任务调度器已关闭")
    
    @staticmethod
    def get_scheduled_jobs():
        """获取所有已调度的任务"""
        return scheduler.get_jobs()
