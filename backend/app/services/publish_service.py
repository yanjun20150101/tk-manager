"""
视频发布服务
处理视频发布到TikTok的逻辑
"""
import httpx
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import PublishRecord, PublishStatus, PrivacyLevel, Media, TikTokAccount
from app.services.tiktok_auth_service import TikTokAuthService
from fastapi import HTTPException, status


class PublishService:
    """视频发布服务类"""
    
    # TikTok API端点
    PUBLISH_VIDEO_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    PUBLISH_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/{publish_id}/"
    
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = TikTokAuthService(db)
    
    async def publish_video(
        self,
        user_id: int,
        tiktok_account_id: int,
        media_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC,
        disable_comment: bool = False,
        disable_duet: bool = False,
        disable_stitch: bool = False,
        video_cover_timestamp_ms: Optional[int] = None
    ) -> PublishRecord:
        """
        发布视频到TikTok
        
        Args:
            user_id: 用户ID
            tiktok_account_id: TikTok账号ID
            media_id: 素材ID
            title: 标题
            description: 描述
            privacy_level: 隐私级别
            disable_comment: 禁用评论
            disable_duet: 禁用合拍
            disable_stitch: 禁用拼接
            video_cover_timestamp_ms: 封面时间戳
        
        Returns:
            PublishRecord对象
        """
        # 验证素材
        media = self.db.query(Media).filter(
            Media.id == media_id,
            Media.user_id == user_id
        ).first()
        
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="素材不存在"
            )
        
        if media.media_type.value != 'video':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能发布视频素材"
            )
        
        # 验证TikTok账号
        account = self.db.query(TikTokAccount).filter(
            TikTokAccount.id == tiktok_account_id,
            TikTokAccount.user_id == user_id,
            TikTokAccount.is_active == True
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TikTok账号不存在或未激活"
            )
        
        # 创建发布记录
        publish_record = PublishRecord(
            user_id=user_id,
            tiktok_account_id=tiktok_account_id,
            media_id=media_id,
            title=title,
            description=description,
            privacy_level=privacy_level,
            disable_comment=disable_comment,
            disable_duet=disable_duet,
            disable_stitch=disable_stitch,
            video_cover_timestamp_ms=video_cover_timestamp_ms,
            status=PublishStatus.UPLOADING
        )
        
        self.db.add(publish_record)
        self.db.commit()
        self.db.refresh(publish_record)
        
        try:
            # 获取有效的访问令牌
            access_token = await self.auth_service.get_valid_access_token(tiktok_account_id)
            
            # 准备发布数据
            post_info = {
                "title": title or media.title or "",
                "privacy_level": privacy_level.value,
                "disable_comment": disable_comment,
                "disable_duet": disable_duet,
                "disable_stitch": disable_stitch,
            }
            
            if description:
                post_info["description"] = description
            
            if video_cover_timestamp_ms is not None:
                post_info["video_cover_timestamp_ms"] = video_cover_timestamp_ms
            
            # 准备source_info（视频来源）
            # 注意：这里需要提供可公开访问的视频URL
            # 在实际部署时，需要配置文件存储服务（如OSS）返回公开URL
            source_info = {
                "source": "FILE_URL",
                "video_url": f"https://your-domain.com/media/{media.file_path}",  # TODO: 配置实际的文件URL
            }
            
            # 调用TikTok API发布视频
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.PUBLISH_VIDEO_URL,
                    json={
                        "post_info": post_info,
                        "source_info": source_info
                    },
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            # 解析响应
            if result.get('error'):
                error = result['error']
                publish_record.status = PublishStatus.FAILED
                publish_record.error_code = error.get('code')
                publish_record.error_message = error.get('message')
            else:
                data = result.get('data', {})
                publish_record.publish_id = data.get('publish_id')
                publish_record.status = PublishStatus.PROCESSING
            
            self.db.commit()
            self.db.refresh(publish_record)
            
            return publish_record
            
        except httpx.HTTPError as e:
            # 发布失败
            publish_record.status = PublishStatus.FAILED
            publish_record.error_message = f"发布请求失败: {str(e)}"
            self.db.commit()
            self.db.refresh(publish_record)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发布视频失败: {str(e)}"
            )
        except Exception as e:
            # 其他错误
            publish_record.status = PublishStatus.FAILED
            publish_record.error_message = str(e)
            self.db.commit()
            self.db.refresh(publish_record)
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发布视频失败: {str(e)}"
            )
    
    async def check_publish_status(
        self,
        publish_record_id: int,
        user_id: int
    ) -> PublishRecord:
        """
        检查发布状态
        
        Args:
            publish_record_id: 发布记录ID
            user_id: 用户ID
        
        Returns:
            更新后的PublishRecord对象
        """
        # 查询发布记录
        publish_record = self.db.query(PublishRecord).filter(
            PublishRecord.id == publish_record_id,
            PublishRecord.user_id == user_id
        ).first()
        
        if not publish_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="发布记录不存在"
            )
        
        if not publish_record.publish_id:
            return publish_record
        
        try:
            # 获取有效的访问令牌
            access_token = await self.auth_service.get_valid_access_token(
                publish_record.tiktok_account_id
            )
            
            # 查询发布状态
            url = self.PUBLISH_STATUS_URL.format(publish_id=publish_record.publish_id)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            # 解析响应
            if result.get('error'):
                error = result['error']
                publish_record.status = PublishStatus.FAILED
                publish_record.error_code = error.get('code')
                publish_record.error_message = error.get('message')
            else:
                data = result.get('data', {})
                status_value = data.get('status')
                
                # 更新状态
                if status_value == 'PUBLISH_COMPLETE':
                    publish_record.status = PublishStatus.PUBLISHED
                    publish_record.published_at = datetime.utcnow()
                    
                    # 更新分享链接
                    if 'share_url' in data:
                        publish_record.share_url = data['share_url']
                elif status_value == 'FAILED':
                    publish_record.status = PublishStatus.FAILED
                    publish_record.error_message = data.get('fail_reason', '发布失败')
                else:
                    # PROCESSING_UPLOAD, PROCESSING_DOWNLOAD, etc.
                    publish_record.status = PublishStatus.PROCESSING
            
            self.db.commit()
            self.db.refresh(publish_record)
            
            return publish_record
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询发布状态失败: {str(e)}"
            )
    
    def get_publish_record(self, record_id: int, user_id: int) -> Optional[PublishRecord]:
        """
        获取发布记录
        
        Args:
            record_id: 记录ID
            user_id: 用户ID
        
        Returns:
            PublishRecord对象或None
        """
        return self.db.query(PublishRecord).filter(
            PublishRecord.id == record_id,
            PublishRecord.user_id == user_id
        ).first()
    
    def list_publish_records(
        self,
        user_id: int,
        tiktok_account_id: Optional[int] = None,
        status: Optional[PublishStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple:
        """
        获取发布记录列表
        
        Args:
            user_id: 用户ID
            tiktok_account_id: TikTok账号ID过滤
            status: 状态过滤
            page: 页码
            page_size: 每页数量
        
        Returns:
            (总数, 记录列表)元组
        """
        query = self.db.query(PublishRecord).filter(PublishRecord.user_id == user_id)
        
        # 应用过滤条件
        if tiktok_account_id:
            query = query.filter(PublishRecord.tiktok_account_id == tiktok_account_id)
        
        if status:
            query = query.filter(PublishRecord.status == status)
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        items = query.order_by(PublishRecord.created_at.desc()).offset(offset).limit(page_size).all()
        
        return total, items
