"""
TikTok相关路由
处理TikTok OAuth授权和账号管理
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import secrets
from typing import List

from app.core import get_db
from app.models import User
from app.schemas import TikTokAccountResponse, TikTokAuthCallback
from app.services.tiktok_auth_service import TikTokAuthService
from app.utils import get_current_user

router = APIRouter(prefix="/tiktok", tags=["TikTok授权"])


@router.get("/auth")
async def initiate_auth(request: Request):
    """
    发起TikTok授权
    
    生成授权URL并重定向用户到TikTok授权页面
    """
    # 生成CSRF保护令牌
    state = secrets.token_urlsafe(32)
    
    # 存储state到session（生产环境应使用Redis）
    # 这里简化处理，实际应用中需要正确配置session
    request.session['tiktok_auth_state'] = state
    
    # 生成授权URL
    db = next(get_db())
    auth_service = TikTokAuthService(db)
    auth_url = auth_service.generate_auth_url(state)
    
    return {
        "auth_url": auth_url,
        "message": "请访问auth_url完成授权"
    }


@router.get("/callback")
async def auth_callback(
    code: str,
    state: str,
    scopes: str = None,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    处理TikTok授权回调
    
    接收授权码并交换访问令牌
    """
    # 验证state（CSRF保护）
    # 生产环境需要从session或Redis中验证
    # stored_state = request.session.get('tiktok_auth_state')
    # if not stored_state or state != stored_state:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Invalid state parameter"
    #     )
    
    auth_service = TikTokAuthService(db)
    
    try:
        # 用授权码交换访问令牌
        token_data = await auth_service.exchange_code_for_token(code)
        
        # 获取用户信息
        access_token = token_data.get('access_token')
        user_info = await auth_service.get_user_info(access_token)
        
        # 保存账号信息
        account = await auth_service.save_tiktok_account(
            user_id=current_user.id,
            token_data=token_data,
            user_info=user_info
        )
        
        return {
            "message": "授权成功",
            "account_id": account.id,
            "open_id": account.open_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"授权失败: {str(e)}"
        )


@router.get("/accounts", response_model=List[TikTokAccountResponse])
async def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有TikTok账号
    """
    auth_service = TikTokAuthService(db)
    accounts = auth_service.get_user_accounts(current_user.id)
    return accounts


@router.get("/accounts/{account_id}", response_model=TikTokAccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定TikTok账号信息
    """
    auth_service = TikTokAuthService(db)
    account = auth_service.get_account(account_id)
    
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )
    
    return account


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除TikTok账号授权
    """
    auth_service = TikTokAuthService(db)
    account = auth_service.get_account(account_id)
    
    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="账号不存在"
        )
    
    # 标记为不活跃
    account.is_active = False
    db.commit()
    
    return {"message": "账号已删除"}


@router.post("/accounts/{account_id}/refresh")
async def refresh_token(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    手动刷新TikTok访问令牌
    """
    auth_service = TikTokAuthService(db)
    
    try:
        # 获取有效的访问令牌（会自动刷新）
        access_token = await auth_service.get_valid_access_token(account_id)
        
        return {
            "message": "令牌刷新成功",
            "account_id": account_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}"
        )
