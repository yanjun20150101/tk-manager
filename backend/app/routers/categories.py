"""
分类管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core import get_db
from app.models import User
from app.schemas.task import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from app.utils import get_current_user

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建分类
    """
    category_service = CategoryService(db)
    
    try:
        category = category_service.create_category(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
            parent_id=request.parent_id,
            sort_order=request.sort_order
        )
        
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分类失败: {str(e)}"
        )


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    parent_id: int = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类列表
    """
    category_service = CategoryService(db)
    categories = category_service.list_categories(
        user_id=current_user.id,
        parent_id=parent_id,
        include_inactive=include_inactive
    )
    
    return categories


@router.get("/tree")
async def get_category_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类树
    """
    category_service = CategoryService(db)
    return category_service.get_category_tree(current_user.id)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取分类详情
    """
    category_service = CategoryService(db)
    category = category_service.get_category(category_id, current_user.id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新分类
    """
    category_service = CategoryService(db)
    
    try:
        category = category_service.update_category(
            category_id=category_id,
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
            sort_order=request.sort_order,
            is_active=request.is_active
        )
        
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分类失败: {str(e)}"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除分类
    """
    category_service = CategoryService(db)
    
    try:
        if not category_service.delete_category(category_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        return {"message": "分类已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分类失败: {str(e)}"
        )
