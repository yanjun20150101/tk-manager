"""
TikTok相关的Pydantic模式
用于请求验证和响应序列化
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.publish import PrivacyLevel, PublishStatus


class TikTokAccountBase(BaseModel):
    """TikTok账号基础模式"""
    open_id: str = Field(..., description="TikTok OpenID")
    username: Optional[str] = Field(None, description="TikTok用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")


class TikTokAccountResponse(TikTokAccountBase):
    """TikTok账号响应模式"""
    id: int
    user_id: int
    is_active: bool
    scope: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TikTokAuthCallback(BaseModel):
    """TikTok授权回调参数"""
    code: str = Field(..., description="授权码")
    state: str = Field(..., description="状态码")
    scopes: Optional[str] = Field(None, description="授权范围")


class MediaUploadResponse(BaseModel):
    """素材上传响应"""
    id: int
    title: Optional[str]
    media_type: str
    status: str
    file_path: str
    file_size: Optional[int]
    thumbnail_path: Optional[str]
    created_at: datetime


class MediaListItem(BaseModel):
    """素材列表项"""
    id: int
    title: Optional[str]
    description: Optional[str]
    media_type: str
    status: str
    original_filename: str
    file_size: Optional[int]
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    thumbnail_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """素材列表响应"""
    total: int
    page: int
    page_size: int
    items: List[MediaListItem]


class PublishVideoRequest(BaseModel):
    """发布视频请求"""
    tiktok_account_id: int = Field(..., description="TikTok账号ID")
    media_id: int = Field(..., description="素材ID")
    title: Optional[str] = Field(None, max_length=500, description="标题")
    description: Optional[str] = Field(None, description="描述")
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PUBLIC, description="隐私级别")
    disable_comment: bool = Field(default=False, description="禁用评论")
    disable_duet: bool = Field(default=False, description="禁用合拍")
    disable_stitch: bool = Field(default=False, description="禁用拼接")
    video_cover_timestamp_ms: Optional[int] = Field(None, description="封面时间戳（毫秒）")


class PublishRecordResponse(BaseModel):
    """发布记录响应"""
    id: int
    tiktok_account_id: int
    media_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    privacy_level: str
    status: str
    publish_id: Optional[str]
    share_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PublishStatusResponse(BaseModel):
    """发布状态响应"""
    publish_id: str
    status: PublishStatus
    share_url: Optional[str]
    error_message: Optional[str]
