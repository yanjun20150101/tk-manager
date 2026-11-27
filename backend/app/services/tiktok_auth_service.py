"""
TikTok授权服务
处理OAuth 2.0授权流程和令牌管理
"""
import httpx
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models import TikTokAccount, User
from app.core.config import settings
from app.utils.encryption import encrypt_token, decrypt_token
from fastapi import HTTPException, status


class TikTokAuthService:
    """TikTok授权服务类"""
    
    # TikTok API端点
    AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_auth_url(self, state: str, scope: Optional[str] = None) -> str:
        """
        生成TikTok授权URL
        
        Args:
            state: CSRF保护令牌
            scope: 授权范围，默认为基本权限
        
        Returns:
            授权URL
        """
        if scope is None:
            # 默认请求的权限范围
            scope = "user.info.basic,video.publish,video.upload"
        
        params = {
            'client_key': settings.TIKTOK_CLIENT_KEY,
            'scope': scope,
            'redirect_uri': settings.TIKTOK_REDIRECT_URI,
            'state': state,
            'response_type': 'code'
        }
        
        # 构建URL
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{param_str}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        用授权码交换访问令牌
        
        Args:
            code: 授权码
        
        Returns:
            令牌信息字典
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        'client_key': settings.TIKTOK_CLIENT_KEY,
                        'client_secret': settings.TIKTOK_CLIENT_SECRET,
                        'code': code,
                        'grant_type': 'authorization_code',
                        'redirect_uri': settings.TIKTOK_REDIRECT_URI
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"令牌交换失败: {str(e)}"
                )
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
        
        Returns:
            新的令牌信息字典
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        'client_key': settings.TIKTOK_CLIENT_KEY,
                        'client_secret': settings.TIKTOK_CLIENT_SECRET,
                        'grant_type': 'refresh_token',
                        'refresh_token': refresh_token
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"令牌刷新失败: {str(e)}"
                )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取TikTok用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            用户信息字典
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_INFO_URL,
                    params={'fields': 'open_id,union_id,avatar_url,display_name'},
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"获取用户信息失败: {str(e)}"
                )
    
    async def save_tiktok_account(
        self,
        user_id: int,
        token_data: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None
    ) -> TikTokAccount:
        """
        保存或更新TikTok账号信息
        
        Args:
            user_id: 用户ID
            token_data: 令牌数据
            user_info: 用户信息（可选）
        
        Returns:
            TikTokAccount对象
        """
        open_id = token_data.get('open_id')
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 86400)  # 默认24小时
        scope = token_data.get('scope', '')
        
        # 加密令牌
        access_encrypted = encrypt_token(access_token)
        refresh_encrypted = encrypt_token(refresh_token)
        
        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        refresh_expires_at = datetime.utcnow() + timedelta(days=365)  # 刷新令牌有效期1年
        
        # 查找是否已存在该账号
        account = self.db.query(TikTokAccount).filter(
            TikTokAccount.open_id == open_id
        ).first()
        
        if account:
            # 更新现有账号
            account.user_id = user_id
            account.access_token_encrypted = access_encrypted['encrypted']
            account.access_token_iv = access_encrypted['iv']
            account.access_token_auth_tag = access_encrypted['auth_tag']
            account.refresh_token_encrypted = refresh_encrypted['encrypted']
            account.refresh_token_iv = refresh_encrypted['iv']
            account.refresh_token_auth_tag = refresh_encrypted['auth_tag']
            account.scope = scope
            account.expires_at = expires_at
            account.refresh_expires_at = refresh_expires_at
            account.last_refresh_at = datetime.utcnow()
            account.is_active = True
            
            # 更新用户信息
            if user_info:
                data = user_info.get('data', {}).get('user', {})
                account.username = data.get('union_id', '')
                account.display_name = data.get('display_name', '')
                account.avatar_url = data.get('avatar_url', '')
        else:
            # 创建新账号
            account = TikTokAccount(
                user_id=user_id,
                open_id=open_id,
                access_token_encrypted=access_encrypted['encrypted'],
                access_token_iv=access_encrypted['iv'],
                access_token_auth_tag=access_encrypted['auth_tag'],
                refresh_token_encrypted=refresh_encrypted['encrypted'],
                refresh_token_iv=refresh_encrypted['iv'],
                refresh_token_auth_tag=refresh_encrypted['auth_tag'],
                scope=scope,
                expires_at=expires_at,
                refresh_expires_at=refresh_expires_at,
                is_active=True
            )
            
            # 设置用户信息
            if user_info:
                data = user_info.get('data', {}).get('user', {})
                account.username = data.get('union_id', '')
                account.display_name = data.get('display_name', '')
                account.avatar_url = data.get('avatar_url', '')
            
            self.db.add(account)
        
        self.db.commit()
        self.db.refresh(account)
        
        return account
    
    def get_account(self, account_id: int) -> Optional[TikTokAccount]:
        """
        获取TikTok账号
        
        Args:
            account_id: 账号ID
        
        Returns:
            TikTokAccount对象或None
        """
        return self.db.query(TikTokAccount).filter(
            TikTokAccount.id == account_id,
            TikTokAccount.is_active == True
        ).first()
    
    def get_user_accounts(self, user_id: int) -> list:
        """
        获取用户的所有TikTok账号
        
        Args:
            user_id: 用户ID
        
        Returns:
            TikTokAccount列表
        """
        return self.db.query(TikTokAccount).filter(
            TikTokAccount.user_id == user_id,
            TikTokAccount.is_active == True
        ).all()
    
    async def get_valid_access_token(self, account_id: int) -> str:
        """
        获取有效的访问令牌（如果过期则自动刷新）
        
        Args:
            account_id: 账号ID
        
        Returns:
            有效的访问令牌
        """
        account = self.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TikTok账号不存在"
            )
        
        # 检查令牌是否即将过期（提前5分钟刷新）
        now = datetime.utcnow()
        if account.expires_at and account.expires_at - now < timedelta(minutes=5):
            # 令牌已过期或即将过期，需要刷新
            refresh_token = decrypt_token(
                account.refresh_token_encrypted,
                account.refresh_token_iv,
                account.refresh_token_auth_tag
            )
            
            # 刷新令牌
            token_data = await self.refresh_access_token(refresh_token)
            
            # 更新账号信息
            await self.save_tiktok_account(account.user_id, token_data)
            
            # 重新获取账号
            self.db.refresh(account)
        
        # 解密并返回访问令牌
        return decrypt_token(
            account.access_token_encrypted,
            account.access_token_iv,
            account.access_token_auth_tag
        )
