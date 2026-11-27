<template>
  <el-container class="main-layout">
    <!-- 顶部导航栏 -->
    <el-header class="main-header">
      <div class="header-left">
        <h2>TikTok账号管理系统</h2>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="35" :src="userInfo?.avatar">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>
            <span class="username">{{ userInfo?.username || '用户' }}</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人信息
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 左侧菜单 -->
      <el-aside width="200px" class="main-aside">
        <el-menu
          :default-active="activeMenu"
          class="main-menu"
          router
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/materials" disabled>
            <el-icon><Picture /></el-icon>
            <span>素材管理</span>
          </el-menu-item>
          
          <el-menu-item index="/publish" disabled>
            <el-icon><Promotion /></el-icon>
            <span>内容发布</span>
          </el-menu-item>
          
          <el-menu-item index="/messages" disabled>
            <el-icon><ChatDotSquare /></el-icon>
            <span>私信管理</span>
          </el-menu-item>
          
          <el-menu-item index="/accounts" disabled>
            <el-icon><Avatar /></el-icon>
            <span>账号管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  UserFilled,
  ArrowDown,
  User,
  SwitchButton,
  HomeFilled,
  Picture,
  Promotion,
  ChatDotSquare,
  Avatar
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 当前用户信息
const userInfo = computed(() => userStore.userInfo)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 处理下拉菜单命令
const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      
      await userStore.userLogout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      // 用户取消操作
    }
  }
}
</script>

<style scoped>
.main-layout {
  width: 100%;
  height: 100vh;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #333;
}

.arrow-icon {
  font-size: 12px;
  color: #909399;
}

.main-container {
  height: calc(100vh - 60px);
}

.main-aside {
  background: #fff;
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
}

.main-menu {
  border-right: none;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
