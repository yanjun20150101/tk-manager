# TikTok账号管理系统

一个基于FastAPI和Vue 3的TikTok账号管理系统，支持素材管理、内容发布、私信管理和账号授权等功能。

## 项目结构

```
tk-manager/
├── backend/                # 后端项目（Python + FastAPI）
│   ├── app/               # 应用代码
│   │   ├── core/         # 核心模块（配置、数据库、安全）
│   │   ├── models/       # 数据库模型
│   │   ├── routers/      # API路由
│   │   ├── schemas/      # Pydantic模式
│   │   ├── utils/        # 工具函数
│   │   └── main.py       # 应用入口
│   ├── scripts/          # 脚本文件
│   │   ├── init_db.sql   # 数据库初始化脚本
│   │   └── create_admin.py  # 创建管理员脚本
│   ├── requirements.txt  # Python依赖
│   ├── .env.example      # 环境变量示例
│   └── .gitignore
│
└── frontend/              # 前端项目（Vue 3 + Element Plus）
    ├── src/
    │   ├── api/          # API接口
    │   ├── assets/       # 静态资源
    │   ├── components/   # 组件
    │   ├── router/       # 路由配置
    │   ├── stores/       # 状态管理
    │   ├── utils/        # 工具函数
    │   ├── views/        # 页面视图
    │   ├── App.vue       # 根组件
    │   └── main.js       # 应用入口
    ├── package.json      # Node依赖
    ├── vite.config.js    # Vite配置
    ├── .env              # 环境变量
    └── .gitignore
```

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: MySQL + Redis
- **ORM**: SQLAlchemy
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 环境要求

### 后端
- Python 3.9+
- MySQL 5.7+ 或 8.0+
- Redis 5.0+

### 前端
- Node.js 16+
- npm 或 yarn

## 快速开始

### 1. 数据库准备

#### 安装MySQL和Redis

**Ubuntu/Debian:**
```bash
# 安装MySQL
sudo apt update
sudo apt install mysql-server

# 安装Redis
sudo apt install redis-server

# 启动服务
sudo systemctl start mysql
sudo systemctl start redis
```

**macOS (使用Homebrew):**
```bash
# 安装MySQL
brew install mysql

# 安装Redis
brew install redis

# 启动服务
brew services start mysql
brew services start redis
```

#### 初始化数据库

```bash
# 登录MySQL
mysql -u root -p

# 执行初始化脚本
source backend/scripts/init_db.sql

# 或者直接导入
mysql -u root -p < backend/scripts/init_db.sql
```

### 2. 后端配置和运行

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件并配置
cp .env.example .env
# 编辑.env文件，配置数据库连接信息

# 创建管理员账号（可选）
python scripts/create_admin.py

# 运行应用
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 http://localhost:8000 启动

API文档地址：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 3. 前端配置和运行

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选）
# 编辑.env文件，配置API地址

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端服务将在 http://localhost:5173 启动

## 默认管理员账号

如果执行了创建管理员脚本，可以使用以下账号登录：

- **用户名**: admin
- **密码**: admin123

⚠️ **重要**: 首次登录后请立即修改默认密码！

## 功能模块（第一阶段）

### 已完成功能 ✅

1. **用户认证**
   - 用户注册
   - 用户登录
   - JWT令牌管理
   - 令牌自动刷新
   - 密码加密

2. **用户管理**
   - 用户信息查看
   - 个人信息页面
   - 用户权限控制

3. **前端界面**
   - 登录页面
   - 注册页面
   - 首页布局
   - 个人信息页面
   - 响应式设计

### 待开发功能 🚧

以下功能将在后续阶段开发：

- 素材管理（视频、图片上传和管理）
- 内容发布（发布到TikTok）
- 私信管理（查看和发送私信）
- 账号授权（OAuth 2.0授权TikTok账号）
- 数据统计和分析

## API端点

### 认证相关

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取当前用户信息

### 其他端点

- `GET /` - 根路径，返回API信息
- `GET /health` - 健康检查

## 开发指南

### 后端开发

1. **添加新模型**: 在 `app/models/` 中创建新的模型类
2. **添加新路由**: 在 `app/routers/` 中创建新的路由模块
3. **添加Pydantic模式**: 在 `app/schemas/` 中定义请求/响应模式
4. **数据库迁移**: 修改模型后，可以使用Alembic进行数据库迁移

### 前端开发

1. **添加新页面**: 在 `src/views/` 中创建Vue组件
2. **添加路由**: 在 `src/router/index.js` 中配置路由
3. **添加API接口**: 在 `src/api/` 中定义API调用函数
4. **状态管理**: 在 `src/stores/` 中使用Pinia管理状态

## 环境变量说明

### 后端 (.env)

```env
# 应用配置
APP_NAME=TikTok账号管理系统
APP_VERSION=1.0.0
DEBUG=True

# MySQL数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=tiktok_manager

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 前端 (.env)

```env
# API地址
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 常见问题

### 1. 数据库连接失败

- 检查MySQL服务是否启动
- 确认数据库配置信息是否正确
- 确认数据库已创建

### 2. Redis连接失败

- 检查Redis服务是否启动
- 确认Redis配置信息是否正确

### 3. 前端无法连接后端

- 确认后端服务已启动
- 检查前端的API地址配置是否正确
- 确认CORS配置是否包含前端地址

### 4. 令牌过期

- 系统会自动尝试刷新令牌
- 如果刷新失败，会自动跳转到登录页

## 安全建议

1. **生产环境**
   - 修改 `SECRET_KEY` 为强随机字符串
   - 设置 `DEBUG=False`
   - 使用HTTPS
   - 配置防火墙规则

2. **数据库**
   - 使用强密码
   - 限制数据库访问权限
   - 定期备份数据

3. **密码策略**
   - 密码至少6位，包含字母和数字
   - 建议用户使用更强的密码

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。

---

**开发状态**: 第一阶段完成 ✅  
**最后更新**: 2026-11-27
