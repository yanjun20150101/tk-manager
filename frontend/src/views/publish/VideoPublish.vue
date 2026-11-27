<template>
  <div class="video-publish">
    <el-card>
      <template #header>
        <span>发布视频到TikTok</span>
      </template>

      <el-form
        ref="formRef"
        :model="publishForm"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="TikTok账号" prop="tiktok_account_id">
          <el-select
            v-model="publishForm.tiktok_account_id"
            placeholder="请选择TikTok账号"
            style="width: 100%"
          >
            <el-option
              v-for="account in accounts"
              :key="account.id"
              :label="account.display_name || account.open_id"
              :value="account.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="选择素材" prop="media_id">
          <el-select
            v-model="publishForm.media_id"
            placeholder="请选择视频素材"
            style="width: 100%"
            @change="handleMediaChange"
          >
            <el-option
              v-for="media in videoList"
              :key="media.id"
              :label="media.title || media.original_filename"
              :value="media.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input
            v-model="publishForm.title"
            placeholder="请输入标题"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="publishForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入描述"
          />
        </el-form-item>

        <el-form-item label="隐私设置">
          <el-radio-group v-model="publishForm.privacy_level">
            <el-radio value="PUBLIC_TO_EVERYONE">所有人可见</el-radio>
            <el-radio value="MUTUAL_FOLLOW_FRIENDS">好友可见</el-radio>
            <el-radio value="SELF_ONLY">仅自己可见</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="互动设置">
          <el-checkbox v-model="publishForm.disable_comment">禁用评论</el-checkbox>
          <el-checkbox v-model="publishForm.disable_duet">禁用合拍</el-checkbox>
          <el-checkbox v-model="publishForm.disable_stitch">禁用拼接</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="publishing" @click="handlePublish">
            发布视频
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 发布记录 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>发布记录</span>
      </template>

      <el-table v-loading="recordsLoading" :data="publishRecords">
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="share_url" label="分享链接">
          <template #default="{ row }">
            <a v-if="row.share_url" :href="row.share_url" target="_blank">
              {{ row.share_url }}
            </a>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'processing' || row.status === 'uploading'"
              size="small"
              @click="handleCheckStatus(row.id)"
            >
              刷新状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTikTokAccounts } from '@/api/tiktok'
import { getMediaList } from '@/api/media'
import { publishVideo, getPublishRecords, checkPublishStatus } from '@/api/publish'

const formRef = ref(null)
const publishing = ref(false)
const recordsLoading = ref(false)

// 账号列表
const accounts = ref([])

// 视频列表
const videoList = ref([])

// 发布表单
const publishForm = ref({
  tiktok_account_id: null,
  media_id: null,
  title: '',
  description: '',
  privacy_level: 'PUBLIC_TO_EVERYONE',
  disable_comment: false,
  disable_duet: false,
  disable_stitch: false
})

// 表单验证规则
const rules = {
  tiktok_account_id: [
    { required: true, message: '请选择TikTok账号', trigger: 'change' }
  ],
  media_id: [
    { required: true, message: '请选择视频素材', trigger: 'change' }
  ]
}

// 发布记录
const publishRecords = ref([])

// 加载TikTok账号
const loadAccounts = async () => {
  try {
    accounts.value = await getTikTokAccounts()
  } catch (error) {
    ElMessage.error('加载TikTok账号失败')
  }
}

// 加载视频列表
const loadVideos = async () => {
  try {
    const result = await getMediaList({
      media_type: 'video',
      status: 'completed',
      page: 1,
      page_size: 100
    })
    videoList.value = result.items
  } catch (error) {
    ElMessage.error('加载视频列表失败')
  }
}

// 加载发布记录
const loadPublishRecords = async () => {
  recordsLoading.value = true
  try {
    publishRecords.value = await getPublishRecords({
      page: 1,
      page_size: 20
    })
  } catch (error) {
    ElMessage.error('加载发布记录失败')
  } finally {
    recordsLoading.value = false
  }
}

// 素材改变时填充标题
const handleMediaChange = (mediaId) => {
  const media = videoList.value.find(m => m.id === mediaId)
  if (media && !publishForm.value.title) {
    publishForm.value.title = media.title || media.original_filename
  }
}

// 发布视频
const handlePublish = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    publishing.value = true
    await publishVideo(publishForm.value)
    
    ElMessage.success('视频发布成功')
    resetForm()
    loadPublishRecords()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}

// 检查发布状态
const handleCheckStatus = async (recordId) => {
  try {
    await checkPublishStatus(recordId)
    ElMessage.success('状态已更新')
    loadPublishRecords()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  publishForm.value = {
    tiktok_account_id: null,
    media_id: null,
    title: '',
    description: '',
    privacy_level: 'PUBLIC_TO_EVERYONE',
    disable_comment: false,
    disable_duet: false,
    disable_stitch: false
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    uploading: 'warning',
    processing: 'warning',
    published: 'success',
    failed: 'danger',
    scheduled: 'primary'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    pending: '待发布',
    uploading: '上传中',
    processing: '处理中',
    published: '已发布',
    failed: '失败',
    scheduled: '已定时'
  }
  return textMap[status] || status
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadAccounts()
  loadVideos()
  loadPublishRecords()
})
</script>

<style scoped>
.video-publish {
  width: 100%;
}
</style>
