"""
定时任务管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core import get_db
from app.models import User, TaskStatus, TaskType
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.utils import get_current_user

router = APIRouter(prefix="/tasks", tags=["定时任务"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建定时任务
    """
    task_service = TaskService(db)
    
    try:
        task = task_service.create_task(
            user_id=current_user.id,
            task_type=request.task_type,
            scheduled_time=request.scheduled_time,
            task_params=request.task_params,
            task_name=request.task_name,
            description=request.description,
            max_retries=request.max_retries
        )
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: {str(e)}"
        )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    task_type: Optional[TaskType] = Query(None, description="任务类型过滤"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务列表
    """
    task_service = TaskService(db)
    
    total, items = task_service.list_tasks(
        user_id=current_user.id,
        task_type=task_type,
        status_filter=status_filter,
        page=page,
        page_size=page_size
    )
    
    return items


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取任务详情
    """
    task_service = TaskService(db)
    task = task_service.get_task(task_id, current_user.id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新任务
    """
    task_service = TaskService(db)
    
    try:
        task = task_service.update_task(
            task_id=task_id,
            user_id=current_user.id,
            scheduled_time=request.scheduled_time,
            task_params=request.task_params,
            task_name=request.task_name,
            description=request.description
        )
        
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新任务失败: {str(e)}"
        )


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消任务
    """
    task_service = TaskService(db)
    
    try:
        success = task_service.cancel_task(task_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        return {"message": "任务已取消"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消任务失败: {str(e)}"
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除任务
    """
    task_service = TaskService(db)
    
    if not task_service.delete_task(task_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    return {"message": "任务已删除"}
