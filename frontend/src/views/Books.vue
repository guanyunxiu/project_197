<template>
  <div class="books-page">
    <el-card>
      <div class="search-bar">
        <el-select v-model="searchType" placeholder="搜索类型" style="width: 140px;">
          <el-option label="模糊搜索" value="" />
          <el-option label="书名" value="title" />
          <el-option label="作者" value="author" />
          <el-option label="ISBN" value="isbn" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="请输入搜索内容"
          style="width: 250px;"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select v-model="selectedCategory" placeholder="选择分类" style="width: 160px;" clearable>
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-select v-model="selectedStatus" placeholder="选择状态" style="width: 140px;" clearable>
          <el-option label="可借" value="available" />
          <el-option label="借出" value="borrowed" />
          <el-option label="已预约" value="reserved" />
          <el-option label="整理中" value="organizing" />
          <el-option label="已丢失" value="lost" />
        </el-select>
        <el-select v-model="ordering" placeholder="排序方式" style="width: 180px;" clearable>
          <el-option label="默认" value="" />
          <el-option label="借阅次数（降序）" value="-borrow_count" />
          <el-option label="出版日期（降序）" value="-publish_date" />
          <el-option label="库存（降序）" value="-stock" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <div class="action-buttons" style="margin-left: auto;">
          <el-upload
            v-if="isAdmin"
            :action="importUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :before-upload="beforeImportUpload"
            :on-success="handleImportSuccess"
            :on-error="handleImportError"
            accept=".xlsx,.xls"
          >
            <el-button type="success">
              <el-icon><Upload></Upload></el-icon>
              批量导入Excel
            </el-button>
          </el-upload>
          <el-button v-if="isAdmin" type="primary" @click="handleAdd">
            <el-icon><Plus></Plus></el-icon>
            新增图书
          </el-button>
        </div>
      </div>

      <div class="book-grid" v-loading="loading">
        <el-card
          v-for="book in books"
          :key="book.id"
          class="book-card"
          shadow="hover"
        >
          <div class="book-cover">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" />
            <div v-else class="cover-placeholder">
              <el-icon size="48"><Reading></Reading></el-icon>
              <span>暂无封面</span>
            </div>
            <div class="status-tags">
              <el-tag v-if="book.can_borrow" type="success" size="small">可借</el-tag>
              <el-tag v-else type="info" size="small">不可借</el-tag>
              <el-tag v-if="book.can_reserve" type="warning" size="small">可预约</el-tag>
            </div>
          </div>
          <div class="book-info">
            <h3 class="book-title" :title="book.title">{{ book.title }}</h3>
            <div class="book-meta">
              <div class="meta-item">
                <span class="meta-label">ISBN:</span>
                <span class="meta-value">{{ book.isbn }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">作者:</span>
                <span class="meta-value">{{ book.author }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">分类:</span>
                <span class="meta-value">{{ book.category_name }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">库存:</span>
                <span class="meta-value">{{ book.available_quantity }} / {{ book.total_quantity }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">借阅次数:</span>
                <span class="meta-value">{{ book.borrow_count || 0 }}</span>
              </div>
            </div>
            <div class="book-actions">
              <el-button size="small" @click="handleView(book)">查看</el-button>
              <el-button
                size="small"
                type="primary"
                @click="handleBorrow(book)"
                :disabled="!book.can_borrow"
              >
                借阅
              </el-button>
              <el-button
                v-if="!isAdmin"
                size="small"
                type="warning"
                @click="handleReserve(book)"
                :disabled="!book.can_reserve"
              >
                预约
              </el-button>
              <el-button v-if="isAdmin" size="small" @click="handleEdit(book)">编辑</el-button>
              <el-button v-if="isAdmin" size="small" type="danger" @click="handleDelete(book)">删除</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <el-empty v-if="!loading && books.length === 0" description="暂无图书数据" style="margin-top: 60px;" />

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48, 96]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="fetchBooks"
        @current-change="fetchBooks"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form ref="bookFormRef" :model="bookForm" :rules="bookRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="封面">
              <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                :show-file-list="false"
                :before-upload="beforeCoverUpload"
                :on-success="handleCoverSuccess"
                accept="image/*"
                class="cover-uploader"
              >
                <div v-if="bookForm.cover" class="cover-preview">
                  <img :src="bookForm.cover" alt="封面" />
                </div>
                <div v-else class="cover-upload-placeholder">
                  <el-icon size="28"><Plus></Plus></el-icon>
                  <div style="margin-top: 8px;">上传封面</div>
                </div>
              </el-upload>
            </el-form-item>
          </el-col>
          <el-col :span="16">
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
              <el-date-picker v-model="bookForm.publish_date" type="date" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="分类" prop="category">
              <el-select v-model="bookForm.category" style="width: 100%;">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="内容简介" prop="description">
          <el-input v-model="bookForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="馆藏位置" prop="location">
          <el-input v-model="bookForm.location" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总数量" prop="total_quantity">
              <el-input-number v-model="bookForm.total_quantity" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可借数量" prop="available_quantity">
              <el-input-number v-model="bookForm.available_quantity" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="图书详情" width="700px">
      <div class="detail-content">
        <div class="detail-cover">
          <img v-if="currentBook.cover" :src="currentBook.cover" :alt="currentBook.title" />
          <div v-else class="cover-placeholder large">
            <el-icon size="64"><Reading></Reading></el-icon>
            <span>暂无封面</span>
          </div>
        </div>
        <el-descriptions :column="2" border class="detail-desc">
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
          <el-descriptions-item label="借阅次数">{{ currentBook.borrow_count || 0 }}</el-descriptions-item>
          <el-descriptions-item label="可借">
            <el-tag :type="currentBook.can_borrow ? 'success' : 'info'">
              {{ currentBook.can_borrow ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="可预约">
            <el-tag :type="currentBook.can_reserve ? 'warning' : 'info'">
              {{ currentBook.can_reserve ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentBook.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="内容简介" :span="2">{{ currentBook.description }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button
          type="primary"
          @click="handleBorrow(currentBook)"
          :disabled="!currentBook.can_borrow"
        >
          借阅
        </el-button>
        <el-button
          v-if="!isAdmin"
          type="warning"
          @click="handleReserve(currentBook)"
          :disabled="!currentBook.can_reserve"
        >
          预约
        </el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="borrowDialogVisible" title="借阅图书" width="500px">
      <el-form ref="borrowFormRef" :model="borrowForm" :rules="borrowRules" label-width="100px">
        <el-form-item label="图书">
          <span>{{ borrowBook?.title }}</span>
        </el-form-item>
        <el-form-item label="读者" prop="reader">
          <el-select v-model="borrowForm.reader" placeholder="请选择读者" style="width: 100%;" filterable>
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.username} - ${reader.first_name}${reader.last_name}`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借阅天数" prop="days">
          <el-input-number v-model="borrowForm.days" :min="1" :max="60" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBorrowSubmit" :loading="borrowing">确定借阅</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus, Reading } from '@element-plus/icons-vue'
import axios from 'axios'

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = computed(() => ['super_admin', 'admin'].includes(user.role))

const books = ref([])
const categories = ref([])
const readers = ref([])
const loading = ref(false)
const submitting = ref(false)
const borrowing = ref(false)

const searchType = ref('')
const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const ordering = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const detailVisible = ref(false)
const currentBook = ref({})
const bookFormRef = ref()

const borrowDialogVisible = ref(false)
const borrowBook = ref(null)
const borrowFormRef = ref()

const uploadUrl = '/api/books/upload_cover/'
const importUrl = '/api/books/import_excel/'

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}))

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
  available_quantity: 1,
  cover: ''
})

const borrowForm = reactive({
  reader: '',
  days: 30
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

const borrowRules = {
  reader: [{ required: true, message: '请选择读者', trigger: 'change' }],
  days: [{ required: true, message: '请输入借阅天数', trigger: 'blur' }]
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
    'organizing': 'info',
    'lost': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'available': '可借阅',
    'borrowed': '已借出',
    'reserved': '已预约',
    'organizing': '整理中',
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

const fetchReaders = async () => {
  if (!isAdmin.value) return
  try {
    const res = await axios.get('/readers/', { params: { page_size: 1000 } })
    readers.value = res.data.results || res.data
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
    if (searchKeyword.value) {
      params.search = searchKeyword.value
      if (searchType.value) params.search_type = searchType.value
    }
    if (selectedCategory.value) params.category = selectedCategory.value
    if (selectedStatus.value) params.status = selectedStatus.value
    if (ordering.value) params.ordering = ordering.value
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
  searchType.value = ''
  searchKeyword.value = ''
  selectedCategory.value = ''
  selectedStatus.value = ''
  ordering.value = ''
  currentPage.value = 1
  fetchBooks()
}

const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleCoverSuccess = (response) => {
  bookForm.cover = response.url || response.data?.url
  ElMessage.success('封面上传成功')
}

const beforeImportUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel' ||
                  file.name.endsWith('.xlsx') ||
                  file.name.endsWith('.xls')
  if (!isExcel) {
    ElMessage.error('只能上传Excel文件!')
    return false
  }
  return true
}

const handleImportSuccess = (response) => {
  ElMessage.success(`导入成功，共导入 ${response.count || 0} 条数据`)
  fetchBooks()
}

const handleImportError = (error) => {
  const msg = error.response?.data?.detail || '导入失败'
  ElMessage.error(msg)
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
    available_quantity: 1,
    cover: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑图书'
  Object.assign(bookForm, { ...row, category: row.category || row.category_id })
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

const handleBorrow = async (book) => {
  if (!book.can_borrow) {
    ElMessage.warning('该图书不可借阅')
    return
  }
  if (isAdmin.value) {
    borrowBook.value = book
    borrowForm.reader = ''
    borrowForm.days = 30
    borrowDialogVisible.value = true
  } else {
    try {
      await ElMessageBox.confirm(`确定要借阅图书《${book.title}》吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'primary'
      })
      borrowing.value = true
      await axios.post(`/books/${book.id}/borrow/`, {
        days: 30
      })
      ElMessage.success('借阅成功')
      detailVisible.value = false
      fetchBooks()
    } catch (e) {
      if (e !== 'cancel') {
        const errors = e.response?.data
        if (errors) {
          const firstError = Object.values(errors)[0]
          ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
        } else {
          ElMessage.error('借阅失败')
        }
      }
    } finally {
      borrowing.value = false
    }
  }
}

const handleBorrowSubmit = async () => {
  try {
    await borrowFormRef.value.validate()
    borrowing.value = true
    await axios.post(`/books/${borrowBook.value.id}/borrow/`, {
      reader_id: borrowForm.reader,
      days: borrowForm.days
    })
    ElMessage.success('借阅成功')
    borrowDialogVisible.value = false
    detailVisible.value = false
    fetchBooks()
  } catch (e) {
    const errors = e.response?.data
    if (errors) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('借阅失败')
    }
  } finally {
    borrowing.value = false
  }
}

const handleReserve = async (book) => {
  if (!book.can_reserve) {
    ElMessage.warning('该图书不可预约')
    return
  }
  try {
    await ElMessageBox.confirm(`确定要预约图书《${book.title}》吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await axios.post(`/books/${book.id}/reserve/`)
    ElMessage.success('预约成功')
    detailVisible.value = false
    fetchBooks()
  } catch (e) {
    if (e !== 'cancel') {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('预约失败')
      }
    }
  }
}

const handleSubmit = async () => {
  try {
    await bookFormRef.value.validate()
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
    if (e !== false) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('操作失败')
      }
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchReaders()
  fetchBooks()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.book-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.book-card:hover {
  transform: translateY(-4px);
}

.book-cover {
  position: relative;
  height: 180px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 12px;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  gap: 8px;
}

.cover-placeholder.large {
  height: 200px;
  font-size: 14px;
}

.status-tags {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  gap: 6px;
}

.book-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.book-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.meta-item {
  display: flex;
  gap: 6px;
}

.meta-label {
  color: #909399;
  flex-shrink: 0;
}

.meta-value {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.books-page :deep(.el-pagination) {
  display: flex;
}

.cover-uploader {
  width: 120px;
  height: 160px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-preview,
.cover-upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  font-size: 12px;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-content {
  display: flex;
  gap: 20px;
}

.detail-cover {
  width: 150px;
  flex-shrink: 0;
}

.detail-cover img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.detail-desc {
  flex: 1;
}
</style>
