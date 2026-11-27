-- TikTok账号管理系统 - 第二阶段数据库更新脚本

USE tiktok_manager;

-- 创建TikTok账号表
CREATE TABLE IF NOT EXISTS tiktok_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'TikTok账号ID',
    user_id INT NOT NULL COMMENT '关联用户ID',
    
    -- TikTok账号信息
    open_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'TikTok OpenID',
    username VARCHAR(100) COMMENT 'TikTok用户名',
    display_name VARCHAR(100) COMMENT '显示名称',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    
    -- 加密存储的访问令牌
    access_token_encrypted TEXT NOT NULL COMMENT '加密的访问令牌',
    access_token_iv VARCHAR(32) NOT NULL COMMENT '访问令牌加密IV',
    access_token_auth_tag VARCHAR(32) NOT NULL COMMENT '访问令牌认证标签',
    
    -- 加密存储的刷新令牌
    refresh_token_encrypted TEXT NOT NULL COMMENT '加密的刷新令牌',
    refresh_token_iv VARCHAR(32) NOT NULL COMMENT '刷新令牌加密IV',
    refresh_token_auth_tag VARCHAR(32) NOT NULL COMMENT '刷新令牌认证标签',
    
    -- 令牌信息
    token_type VARCHAR(20) DEFAULT 'bearer' COMMENT '令牌类型',
    scope VARCHAR(255) COMMENT '授权范围',
    expires_at TIMESTAMP NULL COMMENT '访问令牌过期时间',
    refresh_expires_at TIMESTAMP NULL COMMENT '刷新令牌过期时间',
    
    -- 状态信息
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    last_refresh_at TIMESTAMP NULL COMMENT '最后刷新时间',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_open_id (open_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='TikTok账号表';

-- 创建素材表
CREATE TABLE IF NOT EXISTS media (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '素材ID',
    user_id INT NOT NULL COMMENT '上传用户ID',
    
    -- 基本信息
    title VARCHAR(200) COMMENT '素材标题',
    description TEXT COMMENT '素材描述',
    media_type ENUM('video', 'image') NOT NULL COMMENT '素材类型',
    status ENUM('uploading', 'processing', 'completed', 'failed') DEFAULT 'uploading' COMMENT '素材状态',
    
    -- 文件信息
    original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size BIGINT COMMENT '文件大小（字节）',
    mime_type VARCHAR(100) COMMENT 'MIME类型',
    file_hash VARCHAR(64) COMMENT '文件MD5哈希',
    
    -- 视频专用字段
    duration INT COMMENT '视频时长（秒）',
    width INT COMMENT '视频宽度',
    height INT COMMENT '视频高度',
    frame_rate VARCHAR(20) COMMENT '帧率',
    bitrate INT COMMENT '比特率',
    codec VARCHAR(50) COMMENT '编码格式',
    
    -- 缩略图
    thumbnail_path VARCHAR(500) COMMENT '缩略图路径',
    
    -- 分类和标签
    category VARCHAR(50) COMMENT '分类',
    tags TEXT COMMENT '标签（JSON数组）',
    
    -- 状态信息
    error_message TEXT COMMENT '错误信息',
    process_progress INT DEFAULT 0 COMMENT '处理进度（0-100）',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_media_type (media_type),
    INDEX idx_status (status),
    INDEX idx_file_hash (file_hash),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材表';

-- 创建发布记录表
CREATE TABLE IF NOT EXISTS publish_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '发布记录ID',
    user_id INT NOT NULL COMMENT '发布用户ID',
    tiktok_account_id INT NOT NULL COMMENT 'TikTok账号ID',
    media_id INT COMMENT '素材ID',
    
    -- 发布内容
    title VARCHAR(500) COMMENT '标题',
    description TEXT COMMENT '描述',
    privacy_level ENUM('PUBLIC_TO_EVERYONE', 'MUTUAL_FOLLOW_FRIENDS', 'SELF_ONLY') DEFAULT 'PUBLIC_TO_EVERYONE' COMMENT '隐私级别',
    
    -- 发布设置
    disable_comment BOOLEAN DEFAULT FALSE COMMENT '是否禁用评论',
    disable_duet BOOLEAN DEFAULT FALSE COMMENT '是否禁用合拍',
    disable_stitch BOOLEAN DEFAULT FALSE COMMENT '是否禁用拼接',
    video_cover_timestamp_ms INT COMMENT '视频封面时间戳（毫秒）',
    
    -- TikTok响应信息
    publish_id VARCHAR(100) UNIQUE COMMENT 'TikTok发布ID',
    share_url VARCHAR(500) COMMENT '分享链接',
    embed_html TEXT COMMENT '嵌入HTML',
    embed_link VARCHAR(500) COMMENT '嵌入链接',
    
    -- 状态信息
    status ENUM('pending', 'uploading', 'processing', 'published', 'failed', 'scheduled') DEFAULT 'pending' COMMENT '发布状态',
    error_code VARCHAR(50) COMMENT '错误代码',
    error_message TEXT COMMENT '错误信息',
    
    -- 定时发布
    scheduled_time TIMESTAMP NULL COMMENT '定时发布时间',
    published_at TIMESTAMP NULL COMMENT '实际发布时间',
    
    -- 额外数据
    metadata JSON COMMENT '额外元数据',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_tiktok_account_id (tiktok_account_id),
    INDEX idx_media_id (media_id),
    INDEX idx_publish_id (publish_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tiktok_account_id) REFERENCES tiktok_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (media_id) REFERENCES media(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='发布记录表';

-- 完成
SELECT '第二阶段数据库更新完成！' AS message;
