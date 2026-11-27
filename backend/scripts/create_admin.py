"""
创建管理员用户脚本
用于初始化系统管理员账号
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import User, Role


def create_admin_user():
    """创建超级管理员用户"""
    db: Session = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        admin = db.query(User).filter(User.username == "admin").first()
        
        if admin:
            print("管理员用户已存在！")
            return
        
        # 获取超级管理员角色
        super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        
        # 如果角色存在，分配角色
        if super_admin_role:
            admin_user.roles.append(super_admin_role)
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("=" * 50)
        print("管理员账号创建成功！")
        print("=" * 50)
        print(f"用户名: {admin_user.username}")
        print(f"邮箱: {admin_user.email}")
        print("密码: admin123")
        print("=" * 50)
        print("⚠️  请立即登录并修改默认密码！")
        print("=" * 50)
        
    except Exception as e:
        print(f"创建管理员用户失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
