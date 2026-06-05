<template>
  <div class="profile-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header">个人信息</span>
          </template>
          <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="角色">
              <el-tag :type="profileForm.role === 'admin' ? 'danger' : 'success'">
                {{ profileForm.role === 'admin' ? '管理员' : '读者' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            <el-form-item label="姓" prop="first_name">
              <el-input v-model="profileForm.first_name" />
            </el-form-item>
            <el-form-item label="名" prop="last_name">
              <el-input v-model="profileForm.last_name" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" />
            </el-form-item>
            <el-form-item label="地址" prop="address">
              <el-input v-model="profileForm.address" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="注册时间">
              <span>{{ formatDateTime(profileForm.date_joined) }}</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header">修改密码</span>
          </template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updatePassword" :loading="changingPwd">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const profileFormRef = ref()
const passwordFormRef = ref()

const profileForm = reactive({
  id: '',
  username: '',
  role: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  address: '',
  date_joined: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const profileRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  first_name: [{ required: true, message: '请输入姓', trigger: 'blur' }],
  last_name: [{ required: true, message: '请输入名', trigger: 'blur' }]
}

const validateConfirm = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const updating = ref(false)
const changingPwd = ref(false)

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchProfile = async () => {
  try {
    const res = await axios.get('/auth/me/')
    Object.assign(profileForm, res.data)
  } catch (e) {
    ElMessage.error('获取个人信息失败')
  }
}

const updateProfile = async () => {
  try {
    updating.value = true
    const data = { ...profileForm }
    delete data.role
    delete data.username
    delete data.date_joined
    await axios.put(`/users/${profileForm.id}/`, data)
    localStorage.setItem('user', JSON.stringify(profileForm))
    ElMessage.success('个人信息更新成功')
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const updatePassword = async () => {
  try {
    changingPwd.value = true
    await axios.post('/auth/change-password/', passwordForm)
    ElMessage.success('密码修改成功')
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
  } catch (e) {
    const errors = e.response?.data
    if (errors) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('密码修改失败')
    }
  } finally {
    changingPwd.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.card-header {
  font-weight: bold;
  font-size: 16px;
}
</style>
