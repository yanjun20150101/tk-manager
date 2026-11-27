-- TikTok账号管理系统 - 第三阶段数据库更新脚本

USE tiktok_manager;

-- 创建定时任务表
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
    user_id INT NOT NULL COMMENT '创建用户ID',
    
    -- 任务信息
    task_type ENUM('publish_video', 'refresh_token', 'check_status') NOT NULL COMMENT '任务类型',
    task_name VARCHAR(200) COMMENT '任务名称',
    description TEXT COMMENT '任务描述',
    
    -- 执行时间
    scheduled_time TIMESTAMP NOT NULL COMMENT '计划执行时间',
    executed_time TIMESTAMP NULL COMMENT '实际执行时间',
    
    -- 任务状态
    status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending' COMMENT '任务状态',
    
    -- 任务参数（JSON格式）
    task_params JSON COMMENT '任务参数',
    
    -- 执行结果
    result_message TEXT COMMENT '执行结果消息',
    error_message TEXT COMMENT '错误信息',
    
    -- 重试配置
    retry_count INT DEFAULT 0 COMMENT '已重试次数',
    max_retries INT DEFAULT 3 COMMENT '最大重试次数',
    
    -- 关联发布记录
    publish_record_id INT COMMENT '关联的发布记录ID',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_task_type (task_type),
    INDEX idx_status (status),
    INDEX idx_scheduled_time (scheduled_time),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (publish_record_id) REFERENCES publish_records(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时任务表';

-- 创建素材分类表
CREATE TABLE IF NOT EXISTS media_categories (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '分类ID',
    user_id INT NOT NULL COMMENT '创建用户ID',
    
    -- 分类信息
    name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description TEXT COMMENT '分类描述',
    color VARCHAR(20) COMMENT '分类颜色标识',
    icon VARCHAR(50) COMMENT '分类图标',
    
    -- 父分类（支持二级分类）
    parent_id INT COMMENT '父分类ID',
    
    -- 排序和状态
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES media_categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='素材分类表';

-- 更新素材表，添加分类ID字段
ALTER TABLE media 
ADD COLUMN category_id INT COMMENT '分类ID' AFTER tags,
ADD INDEX idx_category_id (category_id),
ADD FOREIGN KEY (category_id) REFERENCES media_categories(id) ON DELETE SET NULL;

-- 完成
SELECT '第三阶段数据库更新完成！' AS message;
