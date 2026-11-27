"""
素材管理服务
处理视频和图片的上传、存储、处理
"""
import os
import hashlib
import shutil
from pathlib import Path
from typing import Optional, BinaryIO, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import UploadFile, HTTPException, status
from app.models import Media, MediaType, MediaStatus
from app.core.config import settings
import subprocess
import json


class MediaService:
    """素材管理服务类"""
    
    # 支持的视频格式
    VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv'}
    # 支持的图片格式
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    
    # 最大文件大小（4GB，TikTok限制）
    MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024
    
    def __init__(self, db: Session):
        self.db = db
        # 存储根目录
        self.storage_root = Path(settings.MEDIA_STORAGE_PATH)
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            MD5哈希字符串
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _detect_media_type(self, filename: str) -> MediaType:
        """
        根据文件扩展名检测媒体类型
        
        Args:
            filename: 文件名
        
        Returns:
            MediaType枚举值
        """
        ext = Path(filename).suffix.lower()
        if ext in self.VIDEO_EXTENSIONS:
            return MediaType.VIDEO
        elif ext in self.IMAGE_EXTENSIONS:
            return MediaType.IMAGE
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def _get_storage_path(self, user_id: int, media_type: MediaType, filename: str) -> Path:
        """
        生成文件存储路径
        
        Args:
            user_id: 用户ID
            media_type: 媒体类型
            filename: 文件名
        
        Returns:
            存储路径
        """
        # 按用户和类型组织目录
        user_dir = self.storage_root / str(user_id) / media_type.value
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名（时间戳 + 原文件名）
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = Path(filename).stem
        ext = Path(filename).suffix
        new_filename = f"{timestamp}_{name}{ext}"
        
        return user_dir / new_filename
    
    def _extract_video_metadata(self, file_path: Path) -> dict:
        """
        使用ffprobe提取视频元数据
        
        Args:
            file_path: 视频文件路径
        
        Returns:
            包含视频信息的字典
        """
        try:
            # 使用ffprobe获取视频信息
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {}
            
            data = json.loads(result.stdout)
            
            # 提取视频流信息
            video_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                None
            )
            
            if not video_stream:
                return {}
            
            format_info = data.get('format', {})
            
            return {
                'duration': int(float(format_info.get('duration', 0))),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'codec': video_stream.get('codec_name'),
                'frame_rate': video_stream.get('r_frame_rate', ''),
                'bitrate': int(format_info.get('bit_rate', 0))
            }
        except Exception as e:
            print(f"提取视频元数据失败: {e}")
            return {}
    
    def _generate_video_thumbnail(self, video_path: Path, thumbnail_path: Path) -> bool:
        """
        生成视频缩略图
        
        Args:
            video_path: 视频文件路径
            thumbnail_path: 缩略图保存路径
        
        Returns:
            是否成功
        """
        try:
            # 使用ffmpeg在第1秒位置截取缩略图
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-ss', '00:00:01',
                '-vframes', '1',
                '-vf', 'scale=320:-1',
                '-y',
                str(thumbnail_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return False
    
    async def upload_media(
        self,
        user_id: int,
        file: UploadFile,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> Media:
        """
        上传素材文件
        
        Args:
            user_id: 用户ID
            file: 上传的文件
            title: 标题
            description: 描述
            category: 分类
        
        Returns:
            Media对象
        """
        # 检测媒体类型
        try:
            media_type = self._detect_media_type(file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # 生成存储路径
        storage_path = self._get_storage_path(user_id, media_type, file.filename)
        
        # 创建数据库记录
        media = Media(
            user_id=user_id,
            title=title or Path(file.filename).stem,
            description=description,
            media_type=media_type,
            status=MediaStatus.UPLOADING,
            original_filename=file.filename,
            file_path=str(storage_path),
            mime_type=file.content_type,
            category=category
        )
        
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        
        try:
            # 保存文件
            with open(storage_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 计算文件大小和哈希
            file_size = storage_path.stat().st_size
            file_hash = self._get_file_hash(storage_path)
            
            # 更新文件信息
            media.file_size = file_size
            media.file_hash = file_hash
            
            # 处理视频
            if media_type == MediaType.VIDEO:
                media.status = MediaStatus.PROCESSING
                self.db.commit()
                
                # 提取视频元数据
                metadata = self._extract_video_metadata(storage_path)
                if metadata:
                    media.duration = metadata.get('duration')
                    media.width = metadata.get('width')
                    media.height = metadata.get('height')
                    media.codec = metadata.get('codec')
                    media.frame_rate = metadata.get('frame_rate')
                    media.bitrate = metadata.get('bitrate')
                
                # 生成缩略图
                thumbnail_path = storage_path.with_suffix('.jpg')
                if self._generate_video_thumbnail(storage_path, thumbnail_path):
                    media.thumbnail_path = str(thumbnail_path)
            
            # 更新状态为完成
            media.status = MediaStatus.COMPLETED
            media.process_progress = 100
            self.db.commit()
            self.db.refresh(media)
            
            return media
            
        except Exception as e:
            # 上传失败，更新状态
            media.status = MediaStatus.FAILED
            media.error_message = str(e)
            self.db.commit()
            
            # 删除已上传的文件
            if storage_path.exists():
                storage_path.unlink()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件上传失败: {str(e)}"
            )
    
    def get_media(self, media_id: int, user_id: int) -> Optional[Media]:
        """
        获取素材信息
        
        Args:
            media_id: 素材ID
            user_id: 用户ID
        
        Returns:
            Media对象或None
        """
        return self.db.query(Media).filter(
            Media.id == media_id,
            Media.user_id == user_id
        ).first()
    
    def list_media(
        self,
        user_id: int,
        media_type: Optional[MediaType] = None,
        status: Optional[MediaStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple:
        """
        获取素材列表
        
        Args:
            user_id: 用户ID
            media_type: 媒体类型过滤
            status: 状态过滤
            search: 搜索关键词
            page: 页码
            page_size: 每页数量
        
        Returns:
            (总数, 素材列表)元组
        """
        query = self.db.query(Media).filter(Media.user_id == user_id)
        
        # 应用过滤条件
        if media_type:
            query = query.filter(Media.media_type == media_type)
        
        if status:
            query = query.filter(Media.status == status)
        
        if search:
            query = query.filter(
                or_(
                    Media.title.contains(search),
                    Media.description.contains(search),
                    Media.original_filename.contains(search)
                )
            )
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        items = query.order_by(Media.created_at.desc()).offset(offset).limit(page_size).all()
        
        return total, items
    
    def delete_media(self, media_id: int, user_id: int) -> bool:
        """
        删除素材
        
        Args:
            media_id: 素材ID
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        media = self.get_media(media_id, user_id)
        if not media:
            return False
        
        # 删除文件
        try:
            file_path = Path(media.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # 删除缩略图
            if media.thumbnail_path:
                thumbnail_path = Path(media.thumbnail_path)
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
        except Exception as e:
            print(f"删除文件失败: {e}")
        
        # 删除数据库记录
        self.db.delete(media)
        self.db.commit()
        
        return True
