"""
发布管理路由
处理视频发布到TikTok
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core import get_db
from app.models import User, PublishStatus
from app.schemas import (
    PublishVideoRequest,
    PublishRecordResponse,
    PublishStatusResponse
)
from app.services.publish_service import PublishService
from app.utils import get_current_user

router = APIRouter(prefix="/publish", tags=["内容发布"])


@router.post("/video", response_model=PublishRecordResponse, status_code=status.HTTP_201_CREATED)
async def publish_video(
    request: PublishVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发布视频到TikTok
    
    需要提供TikTok账号ID和素材ID
    """
    publish_service = PublishService(db)
    
    try:
        record = await publish_service.publish_video(
            user_id=current_user.id,
            tiktok_account_id=request.tiktok_account_id,
            media_id=request.media_id,
            title=request.title,
            description=request.description,
            privacy_level=request.privacy_level,
            disable_comment=request.disable_comment,
            disable_duet=request.disable_duet,
            disable_stitch=request.disable_stitch,
            video_cover_timestamp_ms=request.video_cover_timestamp_ms
        )
        
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发布失败: {str(e)}"
        )


@router.get("/records", response_model=List[PublishRecordResponse])
async def list_publish_records(
    tiktok_account_id: Optional[int] = Query(None, description="TikTok账号ID过滤"),
    status_filter: Optional[PublishStatus] = Query(None, alias="status", description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取发布记录列表
    
    支持分页和筛选
    """
    publish_service = PublishService(db)
    
    total, items = publish_service.list_publish_records(
        user_id=current_user.id,
        tiktok_account_id=tiktok_account_id,
        status=status_filter,
        page=page,
        page_size=page_size
    )
    
    return items


@router.get("/records/{record_id}", response_model=PublishRecordResponse)
async def get_publish_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取发布记录详情
    """
    publish_service = PublishService(db)
    record = publish_service.get_publish_record(record_id, current_user.id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发布记录不存在"
        )
    
    return record


@router.post("/records/{record_id}/check-status", response_model=PublishRecordResponse)
async def check_publish_status(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    检查发布状态
    
    查询TikTok API获取最新的发布状态
    """
    publish_service = PublishService(db)
    
    try:
        record = await publish_service.check_publish_status(record_id, current_user.id)
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询状态失败: {str(e)}"
        )
