# TikTok账号管理系统 - 后端

基于FastAPI开发的后端服务，提供RESTful API接口。

## 技术栈

- **框架**: FastAPI 0.104.1
- **Web服务器**: Uvicorn
- **数据库ORM**: SQLAlchemy 2.0
- **数据库驱动**: PyMySQL
- **缓存**: Redis
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt
- **数据验证**: Pydantic

## 项目结构

```
backend/
├── app/
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库连接
│   │   └── security.py    # 安全相关（JWT、密码加密）
│   ├── models/            # 数据库模型
│   │   └── user.py        # 用户、角色、权限模型
│   ├── routers/           # API路由
│   │   └── auth.py        # 认证路由
│   ├── schemas/           # Pydantic模式
│   │   └── user.py        # 用户相关模式
│   ├── utils/             # 工具函数
│   │   └── dependencies.py # 依赖注入
│   └── main.py            # 应用入口
├── scripts/               # 脚本文件
│   ├── init_db.sql        # 数据库初始化SQL
│   └── create_admin.py    # 创建管理员脚本
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
└── README.md
```

## 安装和运行

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等信息
```

### 4. 初始化数据库

```bash
# 使用MySQL客户端执行初始化脚本
mysql -u root -p < scripts/init_db.sql

# 或在MySQL中直接执行
mysql -u root -p
source scripts/init_db.sql
```

### 5. 创建管理员账号

```bash
python scripts/create_admin.py
```

### 6. 运行应用

```bash
# 方式1：直接运行
python -m app.main

# 方式2：使用uvicorn（推荐）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动应用后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 数据库模型

### User（用户表）

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | Integer | 主键 |
| username | String(50) | 用户名，唯一 |
| email | String(100) | 邮箱，唯一 |
| hashed_password | String(255) | 加密密码 |
| full_name | String(100) | 全名 |
| is_active | Boolean | 是否激活 |
| is_superuser | Boolean | 是否超级管理员 |
| avatar | String(255) | 头像URL |
| phone | String(20) | 手机号 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| last_login | DateTime | 最后登录时间 |

### Role（角色表）

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | Integer | 主键 |
| name | String(50) | 角色名称 |
| code | String(50) | 角色代码 |
| description | String(255) | 角色描述 |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Permission（权限表）

| 字段 | 类型 | 说明 |
|-----|------|-----|
| id | Integer | 主键 |
| name | String(50) | 权限名称 |
| code | String(50) | 权限代码 |
| description | String(255) | 权限描述 |
| resource | String(50) | 资源类型 |
| action | String(50) | 操作类型 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## API端点

### 认证接口

#### 用户注册
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "测试用户"
}
```

#### 用户登录
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

#### 刷新令牌
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your_refresh_token"
}
```

#### 获取当前用户信息
```
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

#### 用户登出
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

## 认证机制

系统使用JWT（JSON Web Token）进行身份认证：

1. **访问令牌（Access Token）**: 有效期30分钟，用于API请求认证
2. **刷新令牌（Refresh Token）**: 有效期7天，用于获取新的访问令牌

### 令牌使用流程

1. 用户登录成功后获得访问令牌和刷新令牌
2. 客户端在每个API请求的Header中携带访问令牌
3. 访问令牌过期后，使用刷新令牌获取新的令牌对
4. 刷新令牌过期后，需要重新登录

## 密码策略

- 最小长度：6位
- 必须包含字母和数字
- 使用bcrypt算法加密存储

## 开发指南

### 添加新的API路由

1. 在 `app/routers/` 目录创建新的路由文件
2. 定义路由处理函数
3. 在 `app/main.py` 中注册路由

```python
# app/routers/example.py
from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["示例"])

@router.get("/")
async def get_example():
    return {"message": "示例接口"}

# app/main.py
from app.routers import example_router
app.include_router(example_router, prefix="/api/v1")
```

### 添加新的数据库模型

1. 在 `app/models/` 目录创建模型文件
2. 定义SQLAlchemy模型类
3. 在 `app/core/database.py` 的 `init_db()` 函数中导入模型

```python
# app/models/example.py
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

### 添加Pydantic模式

在 `app/schemas/` 目录创建对应的Pydantic模式用于请求验证和响应序列化。

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | TikTok账号管理系统 |
| DEBUG | 调试模式 | True |
| MYSQL_HOST | MySQL主机 | localhost |
| MYSQL_PORT | MySQL端口 | 3306 |
| MYSQL_USER | MySQL用户 | root |
| MYSQL_PASSWORD | MySQL密码 | - |
| MYSQL_DATABASE | 数据库名 | tiktok_manager |
| REDIS_HOST | Redis主机 | localhost |
| REDIS_PORT | Redis端口 | 6379 |
| SECRET_KEY | JWT密钥 | - |
| ACCESS_TOKEN_EXPIRE_MINUTES | 访问令牌过期时间（分钟） | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | 刷新令牌过期时间（天） | 7 |

## 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest
```

## 生产部署建议

1. 设置 `DEBUG=False`
2. 使用强随机的 `SECRET_KEY`
3. 配置反向代理（如Nginx）
4. 使用HTTPS
5. 配置日志记录
6. 设置数据库连接池
7. 启用Redis持久化
8. 配置防火墙规则

## 许可证

MIT License
