# 更新日志

## [第二阶段] - 2026-11-27

### 新增功能

#### 后端

1. **TikTok OAuth 2.0授权**
   - 实现TikTok OAuth授权流程
   - 实现授权码交换访问令牌
   - 实现令牌加密存储
   - 实现自动令牌刷新机制
   - 新增TikTok账号管理接口

2. **素材管理**
   - 实现视频和图片上传功能
   - 实现视频元数据提取（使用ffprobe）
   - 实现视频缩略图生成（使用ffmpeg）
   - 实现素材列表查询（支持分页、筛选、搜索）
   - 实现素材预览和下载接口
   - 新增文件加密存储

3. **视频发布**
   - 实现TikTok视频发布API调用
   - 实现发布状态追踪
   - 实现发布记录管理
   - 支持隐私设置和互动设置

4. **数据库模型**
   - 新增TikTok账号表（tiktok_accounts）
   - 新增素材表（media）
   - 新增发布记录表（publish_records）

5. **安全增强**
   - 实现AES-GCM令牌加密存储
   - 实现文件哈希验证
   - 实现CSRF保护

#### 前端

1. **TikTok账号管理页面**
   - 发起OAuth授权
   - 显示授权账号列表
   - 刷新令牌功能
   - 删除账号功能

2. **素材管理页面**
   - 拖拽上传素材
   - 网格视图展示
   - 素材筛选和搜索
   - 视频预览功能
   - 显示缩略图
   - 分页功能

3. **视频发布页面**
   - 选择TikTok账号
   - 选择素材
   - 配置发布参数
   - 查看发布记录
   - 发布状态监控

4. **UI改进**
   - 更新导航菜单
   - 添加新的路由
   - 优化响应式布局

### 技术栈

- **后端新增**:
  - cryptography (AES-GCM加密)
  - python-magic (文件类型检测)
  - Pillow (图片处理)
  - 需要ffmpeg和ffprobe（视频处理）

- **前端**:
  - 保持Vue 3 + Element Plus架构
  - 新增文件上传组件

### 数据库变更

运行以下SQL脚本更新数据库：
```bash
mysql -u root -p < backend/scripts/update_db_phase2.sql
```

### 配置更新

1. 更新环境变量（.env文件）：
   - `TIKTOK_CLIENT_KEY`: TikTok应用Client Key
   - `TIKTOK_CLIENT_SECRET`: TikTok应用Client Secret
   - `TIKTOK_REDIRECT_URI`: OAuth回调地址
   - `MEDIA_STORAGE_PATH`: 素材存储路径

2. 安装系统依赖：
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

### 注意事项

1. TikTok API需要申请开发者权限并创建应用
2. 视频发布需要提供可公开访问的视频URL（生产环境建议使用OSS）
3. 确保有足够的磁盘空间存储上传的素材
4. 定期清理过期的令牌和临时文件

### API限制

- TikTok API速率限制：10 QPS / 600 QPM（Basic级别）
- 视频发布限制：6个/分钟，15个/天
- 文件大小限制：最大4GB

---

## [第一阶段] - 2026-11-27

### 初始版本

- 实现用户注册登录
- 实现JWT认证
- 搭建前后端基础架构
