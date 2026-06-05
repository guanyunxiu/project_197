<template>
  <div class="readers-page">
    <el-card>
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名、姓名、邮箱"
          style="width: 300px; margin-right: 10px;"
          clearable
          @keyup.enter="fetchReaders"
        />
        <el-button type="primary" @click="fetchReaders">搜索</el-button>
        <el-button type="primary" style="margin-left: auto;" @click="handleAdd">
          新增读者
        </el-button>
      </div>

      <el-table :data="readers" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column label="姓名" width="120">
          <template #default="{ row }">
            {{ row.first_name }}{{ row.last_name }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="date_joined" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="fetchReaders"
        @current-change="fetchReaders"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="readerFormRef" :model="readerForm" :rules="readerRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="readerForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="readerForm.email" />
        </el-form-item>
        <el-form-item label="姓" prop="first_name">
          <el-input v-model="readerForm.first_name" />
        </el-form-item>
        <el-form-item label="名" prop="last_name">
          <el-input v-model="readerForm.last_name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="readerForm.phone" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="readerForm.address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="readerForm.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const readers = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const readerFormRef = ref()

const readerForm = reactive({
  id: null,
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  address: '',
  password: ''
})

const readerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  first_name: [{ required: true, message: '请输入姓', trigger: 'blur' }],
  last_name: [{ required: true, message: '请输入名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchReaders = async () => {
  try {
    loading.value = true
    const params = {
      role: 'reader',
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await axios.get('/users/', { params })
    readers.value = res.data.results || res.data
    total.value = res.data.count || readers.value.length
  } catch (e) {
    ElMessage.error('获取读者列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增读者'
  Object.assign(readerForm, {
    id: null,
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    password: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑读者'
  Object.assign(readerForm, { ...row })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除读者「${row.first_name}${row.last_name}」吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/users/${row.id}/`)
      ElMessage.success('删除成功')
      fetchReaders()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    if (isEdit.value) {
      const data = { ...readerForm }
      delete data.password
      await axios.put(`/users/${readerForm.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      const data = { ...readerForm, role: 'reader' }
      await axios.post('/users/', data)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchReaders()
  } catch (e) {
    const errors = e.response?.data
    if (errors) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchReaders()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
}

.readers-page :deep(.el-pagination) {
  display: flex;
}
</style>
