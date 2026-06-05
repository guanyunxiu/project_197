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
          <el-menu-item v-if="isAdmin" index="/dashboard">
            <span>系统首页</span>
          </el-menu-item>
          <el-menu-item index="/books">
            <span>图书列表</span>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/categories">
            <span>图书分类</span>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/readers">
            <span>读者管理</span>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/borrow">
            <span>借阅管理</span>
          </el-menu-item>
          <el-menu-item v-if="!isAdmin" index="/my-borrow">
            <span>我的借阅</span>
          </el-menu-item>
          <el-menu-item v-if="!isAdmin" index="/my-history">
            <span>借阅历史</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <span class="username">{{ currentUser.first_name }}{{ currentUser.last_name }}</span>
                <el-tag :type="isAdmin ? 'danger' : 'success'" size="small">
                  {{ isAdmin ? '管理员' : '读者' }}
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const currentUser = ref({})
const isLoggedInRef = ref(!!localStorage.getItem('token'))

const isLoggedIn = computed(() => isLoggedInRef.value)
const isAdmin = computed(() => currentUser.value.role === 'admin')

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

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '系统首页',
    '/books': '图书列表',
    '/categories': '图书分类',
    '/readers': '读者管理',
    '/borrow': '借阅管理',
    '/my-borrow': '我的借阅',
    '/my-history': '借阅历史',
    '/profile': '个人中心'
  }
  return titles[route.path] || ''
})

const fetchUserInfo = async () => {
  try {
    const res = await axios.get('/auth/me/')
    currentUser.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
  } catch (e) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
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
  overflow: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #2b2f3a;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
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
</style>
