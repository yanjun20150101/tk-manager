"""
用户相关的Pydantic模式
用于请求验证和响应序列化
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名只包含字母、数字和下划线"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少为6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v


class UserUpdate(BaseModel):
    """用户更新模式"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    is_active: bool
    is_superuser: bool
    avatar: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True  # 允许从ORM模型创建


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌响应模式"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class TokenRefresh(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str = Field(..., description="刷新令牌")


class RoleBase(BaseModel):
    """角色基础模式"""
    name: str = Field(..., max_length=50, description="角色名称")
    code: str = Field(..., max_length=50, description="角色代码")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")


class RoleResponse(RoleBase):
    """角色响应模式"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础模式"""
    name: str = Field(..., max_length=50, description="权限名称")
    code: str = Field(..., max_length=50, description="权限代码")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    resource: Optional[str] = Field(None, max_length=50, description="资源类型")
    action: Optional[str] = Field(None, max_length=50, description="操作类型")


class PermissionResponse(PermissionBase):
    """权限响应模式"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
