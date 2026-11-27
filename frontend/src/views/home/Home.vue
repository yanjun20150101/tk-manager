<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎使用TikTok账号管理系统</span>
            </div>
          </template>
          <div class="welcome-content">
            <p>您好，{{ userInfo?.full_name || userInfo?.username }}！</p>
            <p>这是您的控制面板，您可以在这里管理您的TikTok账号。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <el-icon class="stats-icon" :size="40" color="#409EFF">
              <Avatar />
            </el-icon>
            <div class="stats-info">
              <div class="stats-value">0</div>
              <div class="stats-label">授权账号</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <el-icon class="stats-icon" :size="40" color="#67C23A">
              <Picture />
            </el-icon>
            <div class="stats-info">
              <div class="stats-value">0</div>
              <div class="stats-label">素材文件</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <el-icon class="stats-icon" :size="40" color="#E6A23C">
              <Promotion />
            </el-icon>
            <div class="stats-info">
              <div class="stats-value">0</div>
              <div class="stats-label">已发布内容</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <el-icon class="stats-icon" :size="40" color="#F56C6C">
              <ChatDotSquare />
            </el-icon>
            <div class="stats-info">
              <div class="stats-value">0</div>
              <div class="stats-label">未读消息</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速开始</span>
            </div>
          </template>
          <el-empty description="功能开发中，敬请期待..." />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar, Picture, Promotion, ChatDotSquare } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)
</script>

<style scoped>
.home {
  width: 100%;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.welcome-content {
  padding: 10px 0;
}

.welcome-content p {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stats-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stats-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stats-icon {
  margin-right: 20px;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}
</style>
