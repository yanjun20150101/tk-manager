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

# 执行初始化脚本（第一阶段）
source backend/scripts/init_db.sql

# 执行第二阶段更新脚本
source backend/scripts/update_db_phase2.sql

# 或者直接导入
mysql -u root -p < backend/scripts/init_db.sql
mysql -u root -p < backend/scripts/update_db_phase2.sql
```

### 2. 安装视频处理工具

**系统要求**: ffmpeg和ffprobe（用于视频元数据提取和缩略图生成）

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**验证安装:**
```bash
ffmpeg -version
ffprobe -version
```

### 3. 后端配置和运行

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

# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，配置以下关键项：
# 1. MYSQL_PASSWORD - 你的MySQL密码
# 2. SECRET_KEY - 建议使用强随机字符串（可用命令生成: python -c "import secrets; print(secrets.token_urlsafe(32))"）
# 3. TIKTOK_CLIENT_KEY - TikTok应用Client Key
# 4. TIKTOK_CLIENT_SECRET - TikTok应用Client Secret

# 创建管理员账号（可选）
python scripts/create_admin.py

# 运行应用
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**环境变量配置说明:**

`.env` 文件包含所有配置项，主要配置如下：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| MYSQL_PASSWORD | MySQL数据库密码 | your_password |
| SECRET_KEY | JWT密钥（生产环境必须修改） | 使用随机字符串 |
| TIKTOK_CLIENT_KEY | TikTok应用Client Key | 从TikTok开发者平台获取 |
| TIKTOK_CLIENT_SECRET | TikTok应用Client Secret | 从TikTok开发者平台获取 |
| TIKTOK_REDIRECT_URI | OAuth回调地址 | http://localhost:8000/api/v1/tiktok/callback |
| MEDIA_STORAGE_PATH | 素材存储路径 | ./storage/media |

**TikTok开发者账号申请:**
1. 访问 https://developers.tiktok.com/
2. 创建应用并获取 Client Key 和 Client Secret
3. 配置 OAuth 回调地址（与 TIKTOK_REDIRECT_URI 一致）
4. 申请所需的权限范围（scope）：
   - `user.info.basic` - 获取用户基本信息
   - `video.upload` - 上传视频
   - `video.publish` - 发布视频

后端服务将在 http://localhost:8000 启动

API文档地址：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 4. 前端配置和运行

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选）
# .env 文件已包含默认配置，通常不需要修改
# 如需修改API地址，编辑 .env 文件中的 VITE_API_BASE_URL

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

## 完整启动流程

### 首次启动（从零开始）

```bash
# 1. 确保MySQL和Redis已启动
sudo systemctl start mysql
sudo systemctl start redis

# 2. 创建数据库
mysql -u root -p < backend/scripts/init_db.sql
mysql -u root -p < backend/scripts/update_db_phase2.sql

# 3. 安装ffmpeg（如果未安装）
sudo apt-get install ffmpeg  # Ubuntu/Debian
# 或
brew install ffmpeg  # macOS

# 4. 配置后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件配置密码和TikTok API密钥
python scripts/create_admin.py

# 5. 启动后端（在backend目录）
python -m app.main
# 后端运行在 http://localhost:8000

# 6. 配置并启动前端（新终端）
cd frontend
npm install
npm run dev
# 前端运行在 http://localhost:5173
```

### 日常启动

```bash
# 终端1 - 启动后端
cd backend
source venv/bin/activate
python -m app.main

# 终端2 - 启动前端
cd frontend
npm run dev
```

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

后端配置文件位于 `backend/.env`，请从 `.env.example` 复制并修改：

```bash
cd backend
cp .env.example .env
# 然后编辑 .env 文件
```

**关键配置项说明:**

```env
# 数据库密码（必须修改）
MYSQL_PASSWORD=your_mysql_password

# JWT密钥（生产环境必须修改为强随机字符串）
# 生成方法: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-change-this-in-production

# TikTok API配置（从TikTok开发者平台获取）
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret

# OAuth回调地址（需与TikTok开发者平台配置一致）
TIKTOK_REDIRECT_URI=http://localhost:8000/api/v1/tiktok/callback

# 素材存储路径
MEDIA_STORAGE_PATH=./storage/media
```

**完整配置模板参见** `backend/.env.example` 文件，包含详细的配置说明。

### 前端 (.env)

前端配置文件位于 `frontend/.env`，默认配置通常无需修改：

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

### 开发环境

1. **不要将 `.env` 文件提交到Git**
   - `.env` 文件已在 `.gitignore` 中
   - 只提交 `.env.example` 模板文件

2. **使用测试账号**
   - 开发环境使用测试TikTok账号
   - 不要使用真实用户数据

### 生产环境

1. **应用配置**
   - 修改 `SECRET_KEY` 为强随机字符串（使用 `python -c "import secrets; print(secrets.token_urlsafe(32))"` 生成）
   - 设置 `DEBUG=False`
   - 使用HTTPS协议
   - 配置防火墙规则

2. **数据库安全**
   - 使用强密码（建议16位以上，包含大小写字母、数字、特殊字符）
   - 限制数据库访问权限（只允许应用服务器IP访问）
   - 定期备份数据
   - 启用MySQL慢查询日志

3. **TikTok API密钥**
   - 妥善保管Client Secret
   - 定期更新密钥
   - 监控API调用量
   - 配置回调URL白名单

4. **文件存储**
   - 配置文件上传大小限制
   - 使用OSS（对象存储服务）存储素材
   - 定期清理过期文件
   - 设置文件访问权限

5. **密码策略**
   - 密码至少8位，包含字母、数字和特殊字符
   - 启用密码复杂度验证
   - 定期提醒用户更换密码

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。

---

**开发状态**: 第一阶段完成 ✅  
**最后更新**: 2026-11-27
