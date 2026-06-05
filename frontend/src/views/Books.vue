<template>
  <div class="books-page">
    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索书名、作者、ISBN、出版社"
          style="width: 300px; margin-right: 10px;"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select v-model="selectedCategory" placeholder="选择分类" style="width: 200px; margin-right: 10px;" clearable>
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button v-if="isAdmin" type="primary" style="margin-left: auto;" @click="handleAdd">
          新增图书
        </el-button>
      </div>

      <el-table :data="books" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="title" label="书名" min-width="200" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="publisher" label="出版社" width="150" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="available_quantity" label="可借数量" width="100">
          <template #default="{ row }">
            <el-tag :type="row.available_quantity > 0 ? 'success' : 'danger'">
              {{ row.available_quantity }} / {{ row.total_quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="isAdmin" size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="isAdmin" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        @size-change="fetchBooks"
        @current-change="fetchBooks"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="bookFormRef" :model="bookForm" :rules="bookRules" label-width="100px">
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="bookForm.isbn" />
        </el-form-item>
        <el-form-item label="书名" prop="title">
          <el-input v-model="bookForm.title" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="bookForm.author" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="bookForm.publisher" />
        </el-form-item>
        <el-form-item label="出版日期" prop="publish_date">
          <el-date-picker v-model="bookForm.publish_date" type="date" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="bookForm.category" style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容简介" prop="description">
          <el-input v-model="bookForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="馆藏位置" prop="location">
          <el-input v-model="bookForm.location" />
        </el-form-item>
        <el-form-item label="总数量" prop="total_quantity">
          <el-input-number v-model="bookForm.total_quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="可借数量" prop="available_quantity">
          <el-input-number v-model="bookForm.available_quantity" :min="0" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="图书详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ISBN">{{ currentBook.isbn }}</el-descriptions-item>
        <el-descriptions-item label="书名">{{ currentBook.title }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentBook.author }}</el-descriptions-item>
        <el-descriptions-item label="出版社">{{ currentBook.publisher }}</el-descriptions-item>
        <el-descriptions-item label="出版日期">{{ formatDate(currentBook.publish_date) }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ currentBook.category_name }}</el-descriptions-item>
        <el-descriptions-item label="馆藏位置">{{ currentBook.location }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentBook.status)">{{ getStatusText(currentBook.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="库存">
          {{ currentBook.available_quantity }} / {{ currentBook.total_quantity }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentBook.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="内容简介" :span="2">{{ currentBook.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = computed(() => user.role === 'admin')

const books = ref([])
const categories = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const detailVisible = ref(false)
const currentBook = ref({})
const bookFormRef = ref()

const bookForm = reactive({
  id: null,
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  publish_date: '',
  category: '',
  description: '',
  location: '',
  total_quantity: 1,
  available_quantity: 1
})

const bookRules = {
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入出版社', trigger: 'blur' }],
  publish_date: [{ required: true, message: '请选择出版日期', trigger: 'change' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  description: [{ required: true, message: '请输入内容简介', trigger: 'blur' }],
  location: [{ required: true, message: '请输入馆藏位置', trigger: 'blur' }],
  total_quantity: [{ required: true, message: '请输入总数量', trigger: 'blur' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'available': 'success',
    'borrowed': 'warning',
    'reserved': 'primary',
    'lost': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'available': '可借阅',
    'borrowed': '已借出',
    'reserved': '已预约',
    'lost': '已遗失'
  }
  return texts[status] || status
}

const fetchCategories = async () => {
  try {
    const res = await axios.get('/categories/')
    categories.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchBooks = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (selectedCategory.value) params.category = selectedCategory.value
    const res = await axios.get('/books/', { params })
    books.value = res.data.results || res.data
    total.value = res.data.count || books.value.length
  } catch (e) {
    ElMessage.error('获取图书列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchBooks()
}

const handleReset = () => {
  searchKeyword.value = ''
  selectedCategory.value = ''
  currentPage.value = 1
  fetchBooks()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增图书'
  Object.assign(bookForm, {
    id: null,
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publish_date: '',
    category: '',
    description: '',
    location: '',
    total_quantity: 1,
    available_quantity: 1
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑图书'
  Object.assign(bookForm, { ...row })
  dialogVisible.value = true
}

const handleView = (row) => {
  currentBook.value = row
  detailVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除图书《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/books/${row.id}/`)
      ElMessage.success('删除成功')
      fetchBooks()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    if (isEdit.value) {
      await axios.put(`/books/${bookForm.id}/`, bookForm)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/books/', bookForm)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchBooks()
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
  fetchCategories()
  fetchBooks()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.books-page :deep(.el-pagination) {
  display: flex;
}
</style>
