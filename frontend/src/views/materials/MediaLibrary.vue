<template>
  <div class="media-library">
    <!-- 工具栏 -->
    <el-card class="toolbar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filterType" placeholder="媒体类型" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="视频" value="video" />
            <el-option label="图片" value="image" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索素材"
            clearable
            @clear="handleFilter"
          >
            <template #append>
              <el-button :icon="Search" @click="handleFilter" />
            </template>
          </el-input>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-button type="primary" @click="showUploadDialog">
            <el-icon><Upload /></el-icon>
            上传素材
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 素材列表 -->
    <el-card class="media-list">
      <el-empty v-if="!loading && mediaList.length === 0" description="暂无素材">
        <el-button type="primary" @click="showUploadDialog">上传第一个素材</el-button>
      </el-empty>

      <div v-else v-loading="loading" class="media-grid">
        <div
          v-for="item in mediaList"
          :key="item.id"
          class="media-item"
          @click="handlePreview(item)"
        >
          <!-- 缩略图 -->
          <div class="media-thumbnail">
            <el-image
              v-if="item.thumbnail_path"
              :src="getThumbnailUrl(item.id)"
              fit="cover"
              lazy
            >
              <template #error>
                <div class="image-slot">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div v-else class="image-slot">
              <el-icon><Picture /></el-icon>
            </div>
            
            <!-- 视频时长标签 -->
            <div v-if="item.media_type === 'video' && item.duration" class="duration-tag">
              {{ formatDuration(item.duration) }}
            </div>
            
            <!-- 类型标签 -->
            <div class="type-tag">
              <el-tag :type="item.media_type === 'video' ? 'primary' : 'success'" size="small">
                {{ item.media_type === 'video' ? '视频' : '图片' }}
              </el-tag>
            </div>
          </div>

          <!-- 信息 -->
          <div class="media-info">
            <div class="media-title">{{ item.title || '无标题' }}</div>
            <div class="media-meta">
              <span v-if="item.width && item.height">
                {{ item.width }}x{{ item.height }}
              </span>
              <span v-if="item.file_size">
                {{ formatFileSize(item.file_size) }}
              </span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="media-actions" @click.stop>
            <el-button size="small" @click="handleDelete(item.id)">
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 40, 60, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handlePageChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传素材"
      width="600px"
    >
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="uploadForm.title" placeholder="请输入标题（可选）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述（可选）"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="uploadForm.category" placeholder="请输入分类（可选）" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload
            ref="uploadRef"
            :action="uploadAction"
            :headers="uploadHeaders"
            :data="uploadData"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :on-progress="handleUploadProgress"
            :before-upload="beforeUpload"
            :limit="1"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持视频：MP4, MOV, AVI等格式，最大4GB<br/>
                支持图片：JPG, PNG, WebP等格式
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="uploadProgress > 0 && uploadProgress < 100">
          <el-progress :percentage="uploadProgress" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewMedia?.title || '素材预览'"
      width="800px"
    >
      <div v-if="previewMedia" class="preview-content">
        <!-- 视频预览 -->
        <video
          v-if="previewMedia.media_type === 'video'"
          :src="getMediaUrl(previewMedia.id)"
          controls
          style="width: 100%; max-height: 500px;"
        />
        
        <!-- 图片预览 -->
        <el-image
          v-else
          :src="getMediaUrl(previewMedia.id)"
          fit="contain"
          style="width: 100%;"
        />

        <!-- 详细信息 -->
        <el-descriptions :column="2" border style="margin-top: 20px;">
          <el-descriptions-item label="标题">{{ previewMedia.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            {{ previewMedia.media_type === 'video' ? '视频' : '图片' }}
          </el-descriptions-item>
          <el-descriptions-item label="文件名">{{ previewMedia.original_filename }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(previewMedia.file_size) }}</el-descriptions-item>
          <el-descriptions-item v-if="previewMedia.duration" label="时长">
            {{ formatDuration(previewMedia.duration) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="previewMedia.width" label="分辨率">
            {{ previewMedia.width }}x{{ previewMedia.height }}
          </el-descriptions-item>
          <el-descriptions-item label="上传时间" :span="2">
            {{ formatDate(previewMedia.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="previewMedia.description" label="描述" :span="2">
            {{ previewMedia.description }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, UploadFilled, Picture } from '@element-plus/icons-vue'
import { getMediaList, deleteMedia, getThumbnailUrl as getThumbUrl } from '@/api/media'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 筛选和搜索
const filterType = ref('')
const searchKeyword = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 素材列表
const loading = ref(false)
const mediaList = ref([])

// 上传对话框
const uploadDialogVisible = ref(false)
const uploadRef = ref(null)
const uploadProgress = ref(0)
const uploadForm = ref({
  title: '',
  description: '',
  category: ''
})

// 上传配置
const uploadAction = computed(() => {
  return import.meta.env.VITE_API_BASE_URL + '/media/upload'
})
const uploadHeaders = computed(() => {
  return {
    'Authorization': `Bearer ${userStore.accessToken}`
  }
})
const uploadData = computed(() => {
  return {
    title: uploadForm.value.title,
    description: uploadForm.value.description,
    category: uploadForm.value.category
  }
})

// 预览对话框
const previewDialogVisible = ref(false)
const previewMedia = ref(null)

// 加载素材列表
const loadMediaList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filterType.value) {
      params.media_type = filterType.value
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const result = await getMediaList(params)
    mediaList.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error('加载素材列表失败')
  } finally {
    loading.value = false
  }
}

// 处理筛选
const handleFilter = () => {
  currentPage.value = 1
  loadMediaList()
}

// 处理分页变化
const handlePageChange = () => {
  loadMediaList()
}

// 显示上传对话框
const showUploadDialog = () => {
  uploadForm.value = {
    title: '',
    description: '',
    category: ''
  }
  uploadProgress.value = 0
  uploadDialogVisible.value = true
}

// 上传前验证
const beforeUpload = (file) => {
  const isValidSize = file.size < 4 * 1024 * 1024 * 1024 // 4GB
  if (!isValidSize) {
    ElMessage.error('文件大小不能超过4GB')
    return false
  }
  return true
}

// 上传进度
const handleUploadProgress = (event) => {
  uploadProgress.value = Math.round(event.percent)
}

// 上传成功
const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  uploadDialogVisible.value = false
  loadMediaList()
}

// 上传失败
const handleUploadError = () => {
  ElMessage.error('上传失败')
}

// 删除素材
const handleDelete = async (mediaId) => {
  try {
    await ElMessageBox.confirm('确定要删除此素材吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMedia(mediaId)
    ElMessage.success('素材已删除')
    loadMediaList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 预览素材
const handlePreview = (media) => {
  previewMedia.value = media
  previewDialogVisible.value = true
}

// 获取缩略图URL
const getThumbnailUrl = (mediaId) => {
  return import.meta.env.VITE_API_BASE_URL + `/media/${mediaId}/thumbnail`
}

// 获取媒体URL
const getMediaUrl = (mediaId) => {
  return import.meta.env.VITE_API_BASE_URL + `/media/${mediaId}/download`
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '-'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${m}:${String(s).padStart(2, '0')}`
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadMediaList()
})
</script>

<style scoped>
.media-library {
  width: 100%;
}

.toolbar {
  margin-bottom: 20px;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.media-item {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.media-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.media-thumbnail {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f5f7fa;
}

.media-thumbnail .el-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 48px;
}

.duration-tag {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.type-tag {
  position: absolute;
  top: 8px;
  left: 8px;
}

.media-info {
  padding: 12px;
}

.media-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 10px;
}

.media-actions {
  padding: 0 12px 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
