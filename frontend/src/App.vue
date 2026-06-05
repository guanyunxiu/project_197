<template>
  <div class="app-container">
    <el-container v-if="isLoggedIn" class="main-container">
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <span>图书借阅管理</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-sub-menu v-if="isAdminRole" index="admin">
            <template #title>系统管理</template>
            <el-menu-item index="/dashboard">系统首页</el-menu-item>
            <el-menu-item index="/statistics">数据统计</el-menu-item>
            <el-menu-item index="/operation-logs">操作日志</el-menu-item>
            <el-menu-item v-if="isSuperAdmin" index="/system-config">系统配置</el-menu-item>
          </el-sub-menu>

          <el-sub-menu v-if="isAdminRole" index="book-manage">
            <template #title>图书管理</template>
            <el-menu-item index="/books">图书列表</el-menu-item>
            <el-menu-item index="/categories">图书分类</el-menu-item>
          </el-sub-menu>

          <el-sub-menu v-if="isAdminRole" index="borrow-manage">
            <template #title>借阅管理</template>
            <el-menu-item index="/borrow">借阅记录</el-menu-item>
            <el-menu-item index="/renewals">续借审核</el-menu-item>
            <el-menu-item index="/reservations-admin">预约管理</el-menu-item>
            <el-menu-item index="/fines">罚金管理</el-menu-item>
          </el-sub-menu>

          <el-menu-item v-if="isAdminRole" index="/readers">读者管理</el-menu-item>

          <el-menu-item v-if="!isAdminRole" index="/books">
            <span>图书列表</span>
          </el-menu-item>

          <el-sub-menu v-if="!isAdminRole" index="reader-center">
            <template #title>我的借阅</template>
            <el-menu-item index="/my-borrow">当前借阅</el-menu-item>
            <el-menu-item index="/my-reservations">我的预约</el-menu-item>
            <el-menu-item index="/my-fines">我的罚金</el-menu-item>
            <el-menu-item index="/my-history">借阅历史</el-menu-item>
            <el-menu-item index="/my-stats">个人统计</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/profile">
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <span class="page-title">{{ pageTitle }}</span>
            <el-badge
              v-if="pendingCount > 0"
              :value="pendingCount"
              :max="99"
              class="pending-badge"
              type="danger"
            />
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <span class="username">{{ currentUser.first_name }}{{ currentUser.last_name }}</span>
                <el-tag :type="roleTagType" size="small">
                  {{ roleText }}
                </el-tag>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
    <router-view v-else />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const currentUser = ref({})
const isLoggedInRef = ref(!!localStorage.getItem('token'))
const pendingCount = ref(0)

const isLoggedIn = computed(() => isLoggedInRef.value)
const isAdminRole = computed(() => ['super_admin', 'admin'].includes(currentUser.value.role))
const isSuperAdmin = computed(() => currentUser.value.role === 'super_admin')

const roleText = computed(() => {
  const roles = {
    'super_admin': '超级管理员',
    'admin': '普通管理员',
    'reader': '读者'
  }
  return roles[currentUser.value.role] || currentUser.value.role
})

const roleTagType = computed(() => {
  const types = {
    'super_admin': 'danger',
    'admin': 'warning',
    'reader': 'success'
  }
  return types[currentUser.value.role] || 'info'
})

const updateAuthState = () => {
  isLoggedInRef.value = !!localStorage.getItem('token')
  if (isLoggedInRef.value) {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      currentUser.value = JSON.parse(savedUser)
    }
  } else {
    currentUser.value = {}
  }
}

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/my-')) return 'reader-center'
  if (['/dashboard', '/statistics', '/operation-logs', '/system-config'].includes(path)) return 'admin'
  if (['/books', '/categories'].includes(path)) return 'book-manage'
  if (['/borrow', '/renewals', '/reservations-admin', '/fines'].includes(path)) return 'borrow-manage'
  return path
})

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '系统首页',
    '/statistics': '数据统计',
    '/operation-logs': '操作日志',
    '/system-config': '系统配置',
    '/books': '图书列表',
    '/categories': '图书分类',
    '/readers': '读者管理',
    '/borrow': '借阅记录',
    '/renewals': '续借审核',
    '/reservations-admin': '预约管理',
    '/fines': '罚金管理',
    '/my-borrow': '当前借阅',
    '/my-reservations': '我的预约',
    '/my-fines': '我的罚金',
    '/my-history': '借阅历史',
    '/my-stats': '个人统计',
    '/profile': '个人中心'
  }
  return titles[route.path] || ''
})

const fetchUserInfo = async () => {
  try {
    const res = await axios.get('/auth/me/')
    currentUser.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    fetchPendingCount()
  } catch (e) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}

const fetchPendingCount = async () => {
  if (!isAdminRole.value) return
  try {
    const res = await axios.get('/dashboard/stats/')
    pendingCount.value = res.data.pending_renewal_count || 0
  } catch (e) {}
}

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
        try {
          await axios.post('/auth/logout/', {
            refresh: localStorage.getItem('refresh_token')
          })
        } catch (e) {}
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        updateAuthState()
        router.push('/login')
        ElMessage.success('退出成功')
      }).catch(() => {})
  }
}

onMounted(() => {
  updateAuthState()
  if (isLoggedIn.value) {
    fetchUserInfo()
  }
})

watch(() => route.path, () => {
  if (isAdminRole.value) {
    fetchPendingCount()
  }
})

window.__updateAuthState = updateAuthState
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.main-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow-y: auto;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  background-color: #2b2f3a;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-sub-menu__title),
.sidebar-menu :deep(.el-menu-item) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #263445;
  color: #fff;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.pending-badge {
  margin-left: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

#app {
  height: 100vh;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
