<template>
  <div class="profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="100" :src="userInfo?.avatar">
            <el-icon :size="50"><UserFilled /></el-icon>
          </el-avatar>
        </div>

        <el-descriptions :column="1" border class="user-info">
          <el-descriptions-item label="用户名">
            {{ userInfo?.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">
            {{ userInfo?.email || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ userInfo?.full_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="手机号">
            {{ userInfo?.phone || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="账号状态">
            <el-tag :type="userInfo?.is_active ? 'success' : 'danger'">
              {{ userInfo?.is_active ? '正常' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDate(userInfo?.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后登录">
            {{ formatDate(userInfo?.last_login) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.profile {
  width: 100%;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.profile-content {
  padding: 20px;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.user-info {
  margin-top: 20px;
}
</style>
