/**
 * Axios请求封装
 * 统一处理请求和响应
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加访问令牌
    const userStore = useUserStore()
    if (userStore.accessToken) {
      config.headers.Authorization = `Bearer ${userStore.accessToken}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 直接返回数据
    return response.data
  },
  async error => {
    const userStore = useUserStore()

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 未授权，尝试刷新令牌
          if (data.detail === '无效的认证凭证' && userStore.refreshTokenValue) {
            try {
              // 刷新令牌
              const result = await userStore.refreshAccessToken()
              if (result.success) {
                // 重试原请求
                return request(error.config)
              }
            } catch (refreshError) {
              console.error('刷新令牌失败:', refreshError)
            }
          }
          
          // 刷新失败或无刷新令牌，跳转到登录页
          userStore.clearTokens()
          ElMessage.error('登录已过期，请重新登录')
          router.push({ name: 'Login' })
          break

        case 403:
          ElMessage.error('没有权限访问该资源')
          break

        case 404:
          ElMessage.error('请求的资源不存在')
          break

        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break

        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      // 请求配置出错
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default request
