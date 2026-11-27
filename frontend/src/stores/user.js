/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, logout, getCurrentUser, refreshToken } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshTokenValue = ref(localStorage.getItem('refresh_token') || '')

  // 计算属性
  const isAuthenticated = computed(() => !!accessToken.value)
  const userInfo = computed(() => user.value)

  // 设置令牌
  const setTokens = (access, refresh) => {
    accessToken.value = access
    refreshTokenValue.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  // 清除令牌
  const clearTokens = () => {
    accessToken.value = ''
    refreshTokenValue.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 用户登录
  const userLogin = async (credentials) => {
    try {
      const response = await login(credentials)
      setTokens(response.access_token, response.refresh_token)
      await fetchUserInfo()
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '登录失败' 
      }
    }
  }

  // 用户注册
  const userRegister = async (userData) => {
    try {
      await register(userData)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '注册失败' 
      }
    }
  }

  // 用户登出
  const userLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearTokens()
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await getCurrentUser()
      user.value = response
      return { success: true }
    } catch (error) {
      clearTokens()
      return { success: false }
    }
  }

  // 刷新令牌
  const refreshAccessToken = async () => {
    try {
      const response = await refreshToken(refreshTokenValue.value)
      setTokens(response.access_token, response.refresh_token)
      return { success: true }
    } catch (error) {
      clearTokens()
      return { success: false }
    }
  }

  // 初始化用户信息（如果有令牌）
  if (accessToken.value) {
    fetchUserInfo().catch(() => {
      clearTokens()
    })
  }

  return {
    user,
    accessToken,
    refreshTokenValue,
    isAuthenticated,
    userInfo,
    setTokens,
    clearTokens,
    userLogin,
    userRegister,
    userLogout,
    fetchUserInfo,
    refreshAccessToken
  }
})
