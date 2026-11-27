"""
素材管理路由
处理视频和图片的上传、查询、删除
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path

from app.core import get_db
from app.models import User, MediaType, MediaStatus
from app.schemas import MediaUploadResponse, MediaListItem, MediaListResponse
from app.services.media_service import MediaService
from app.utils import get_current_user

router = APIRouter(prefix="/media", tags=["素材管理"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(..., description="上传的文件"),
    title: Optional[str] = Form(None, description="标题"),
    description: Optional[str] = Form(None, description="描述"),
    category: Optional[str] = Form(None, description="分类"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传素材文件
    
    支持视频和图片上传
    """
    media_service = MediaService(db)
    
    try:
        media = await media_service.upload_media(
            user_id=current_user.id,
            file=file,
            title=title,
            description=description,
            category=category
        )
        
        return media
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败: {str(e)}"
        )


@router.get("/", response_model=MediaListResponse)
async def list_media(
    media_type: Optional[MediaType] = Query(None, description="媒体类型过滤"),
    status_filter: Optional[MediaStatus] = Query(None, alias="status", description="状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材列表
    
    支持分页、筛选和搜索
    """
    media_service = MediaService(db)
    
    total, items = media_service.list_media(
        user_id=current_user.id,
        media_type=media_type,
        status=status_filter,
        search=search,
        page=page,
        page_size=page_size
    )
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{media_id}", response_model=MediaListItem)
async def get_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材详情
    """
    media_service = MediaService(db)
    media = media_service.get_media(media_id, current_user.id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    
    return media


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除素材
    """
    media_service = MediaService(db)
    
    if not media_service.delete_media(media_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    
    return {"message": "素材已删除"}


@router.get("/{media_id}/download")
async def download_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载素材文件
    """
    media_service = MediaService(db)
    media = media_service.get_media(media_id, current_user.id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    
    file_path = Path(media.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=media.original_filename,
        media_type=media.mime_type
    )


@router.get("/{media_id}/thumbnail")
async def get_thumbnail(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取素材缩略图
    """
    media_service = MediaService(db)
    media = media_service.get_media(media_id, current_user.id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    
    if not media.thumbnail_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="缩略图不存在"
        )
    
    thumbnail_path = Path(media.thumbnail_path)
    if not thumbnail_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="缩略图文件不存在"
        )
    
    return FileResponse(
        path=str(thumbnail_path),
        media_type="image/jpeg"
    )
