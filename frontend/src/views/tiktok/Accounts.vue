<template>
  <div class="tiktok-accounts">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>TikTok账号管理</span>
          <el-button type="primary" @click="handleAuth">
            <el-icon><Plus /></el-icon>
            授权新账号
          </el-button>
        </div>
      </template>

      <el-empty v-if="!loading && accounts.length === 0" description="暂无授权账号">
        <el-button type="primary" @click="handleAuth">立即授权</el-button>
      </el-empty>

      <el-table v-else v-loading="loading" :data="accounts" style="width: 100%">
        <el-table-column prop="open_id" label="OpenID" width="200" />
        <el-table-column prop="display_name" label="昵称" width="150" />
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar_url" v-if="row.avatar_url">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
            <el-avatar v-else>
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="scope" label="授权范围" />
        <el-table-column label="令牌过期时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.expires_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleRefreshToken(row.id)">
              刷新令牌
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UserFilled } from '@element-plus/icons-vue'
import {
  getTikTokAccounts,
  initiateTikTokAuth,
  deleteTikTokAccount,
  refreshTikTokToken
} from '@/api/tiktok'

const loading = ref(false)
const accounts = ref([])

// 加载账号列表
const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await getTikTokAccounts()
  } catch (error) {
    ElMessage.error('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

// 发起授权
const handleAuth = async () => {
  try {
    const result = await initiateTikTokAuth()
    
    // 打开授权URL
    if (result.auth_url) {
      window.open(result.auth_url, '_blank')
      ElMessage.info('请在新窗口中完成授权')
    }
  } catch (error) {
    ElMessage.error('发起授权失败')
  }
}

// 刷新令牌
const handleRefreshToken = async (accountId) => {
  try {
    await refreshTikTokToken(accountId)
    ElMessage.success('令牌刷新成功')
    await loadAccounts()
  } catch (error) {
    ElMessage.error('令牌刷新失败')
  }
}

// 删除账号
const handleDelete = async (accountId) => {
  try {
    await ElMessageBox.confirm('确定要删除此账号吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteTikTokAccount(accountId)
    ElMessage.success('账号已删除')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除账号失败')
    }
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.tiktok-accounts {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}
</style>
