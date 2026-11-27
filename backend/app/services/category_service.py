"""
分类管理服务
处理素材分类的CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status

from app.models import MediaCategory, Media


class CategoryService:
    """分类管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_category(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: int = 0
    ) -> MediaCategory:
        """
        创建分类
        
        Args:
            user_id: 用户ID
            name: 分类名称
            description: 分类描述
            color: 颜色标识
            icon: 图标
            parent_id: 父分类ID
            sort_order: 排序顺序
        
        Returns:
            MediaCategory对象
        """
        # 检查同名分类
        existing = self.db.query(MediaCategory).filter(
            MediaCategory.user_id == user_id,
            MediaCategory.name == name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在"
            )
        
        # 如果指定了父分类，验证父分类是否存在
        if parent_id:
            parent = self.get_category(parent_id, user_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="父分类不存在"
                )
            
            # 不支持三级分类
            if parent.parent_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不支持三级分类"
                )
        
        # 创建分类
        category = MediaCategory(
            user_id=user_id,
            name=name,
            description=description,
            color=color,
            icon=icon,
            parent_id=parent_id,
            sort_order=sort_order
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_category(self, category_id: int, user_id: int) -> Optional[MediaCategory]:
        """
        获取分类详情
        
        Args:
            category_id: 分类ID
            user_id: 用户ID
        
        Returns:
            MediaCategory对象或None
        """
        return self.db.query(MediaCategory).filter(
            MediaCategory.id == category_id,
            MediaCategory.user_id == user_id
        ).first()
    
    def list_categories(
        self,
        user_id: int,
        parent_id: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[MediaCategory]:
        """
        获取分类列表
        
        Args:
            user_id: 用户ID
            parent_id: 父分类ID（None表示获取顶级分类）
            include_inactive: 是否包含未激活的分类
        
        Returns:
            分类列表
        """
        query = self.db.query(MediaCategory).filter(MediaCategory.user_id == user_id)
        
        # 筛选父分类
        if parent_id is None:
            query = query.filter(MediaCategory.parent_id.is_(None))
        else:
            query = query.filter(MediaCategory.parent_id == parent_id)
        
        # 筛选激活状态
        if not include_inactive:
            query = query.filter(MediaCategory.is_active == True)
        
        # 按排序顺序和创建时间排序
        return query.order_by(MediaCategory.sort_order, MediaCategory.created_at).all()
    
    def update_category(
        self,
        category_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        sort_order: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> MediaCategory:
        """
        更新分类
        
        Args:
            category_id: 分类ID
            user_id: 用户ID
            name: 新的分类名称
            description: 新的描述
            color: 新的颜色
            icon: 新的图标
            sort_order: 新的排序
            is_active: 新的激活状态
        
        Returns:
            更新后的MediaCategory对象
        """
        category = self.get_category(category_id, user_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        
        # 更新字段
        if name is not None:
            # 检查新名称是否与其他分类重复
            existing = self.db.query(MediaCategory).filter(
                MediaCategory.user_id == user_id,
                MediaCategory.name == name,
                MediaCategory.id != category_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="分类名称已存在"
                )
            
            category.name = name
        
        if description is not None:
            category.description = description
        
        if color is not None:
            category.color = color
        
        if icon is not None:
            category.icon = icon
        
        if sort_order is not None:
            category.sort_order = sort_order
        
        if is_active is not None:
            category.is_active = is_active
        
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete_category(self, category_id: int, user_id: int) -> bool:
        """
        删除分类
        
        Args:
            category_id: 分类ID
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        category = self.get_category(category_id, user_id)
        
        if not category:
            return False
        
        # 检查是否有子分类
        children = self.db.query(MediaCategory).filter(
            MediaCategory.parent_id == category_id
        ).count()
        
        if children > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该分类下有子分类，无法删除"
            )
        
        # 检查是否有素材使用该分类
        media_count = self.db.query(Media).filter(
            Media.category_id == category_id
        ).count()
        
        if media_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有{media_count}个素材，无法删除"
            )
        
        # 删除分类
        self.db.delete(category)
        self.db.commit()
        
        return True
    
    def get_category_tree(self, user_id: int) -> List[dict]:
        """
        获取分类树（包含子分类）
        
        Args:
            user_id: 用户ID
        
        Returns:
            分类树列表
        """
        # 获取所有顶级分类
        top_categories = self.list_categories(user_id, parent_id=None)
        
        result = []
        for category in top_categories:
            # 获取子分类
            children = self.list_categories(user_id, parent_id=category.id)
            
            category_dict = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'color': category.color,
                'icon': category.icon,
                'sort_order': category.sort_order,
                'is_active': category.is_active,
                'created_at': category.created_at,
                'children': [
                    {
                        'id': child.id,
                        'name': child.name,
                        'description': child.description,
                        'color': child.color,
                        'icon': child.icon,
                        'sort_order': child.sort_order,
                        'is_active': child.is_active,
                        'created_at': child.created_at
                    }
                    for child in children
                ]
            }
            
            result.append(category_dict)
        
        return result
