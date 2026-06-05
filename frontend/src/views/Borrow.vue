<template>
  <div class="borrow-page">
    <el-card>
      <div class="toolbar">
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="借阅管理" name="records">
            <div class="tab-toolbar">
              <el-select v-model="searchStatus" placeholder="选择状态" style="width: 150px; margin-right: 10px;" clearable>
                <el-option label="借阅中" value="borrowed" />
                <el-option label="已归还" value="returned" />
                <el-option label="已逾期" value="overdue" />
                <el-option label="已遗失" value="lost" />
              </el-select>
              <el-button type="primary" @click="fetchRecords">查询</el-button>
              <el-button type="primary" style="margin-left: auto;" @click="handleBorrow">
                借书登记
              </el-button>
            </div>
            <el-table :data="records" style="width: 100%; margin-top: 20px;" v-loading="loading">
              <el-table-column prop="reader_name" label="读者" width="120" />
              <el-table-column prop="book_title" label="图书" min-width="200" />
              <el-table-column prop="book_isbn" label="ISBN" width="150" />
              <el-table-column prop="borrow_date" label="借阅日期" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.borrow_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="due_date" label="应还日期" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.due_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="return_date" label="归还日期" width="180">
                <template #default="{ row }">
                  {{ row.return_date ? formatDateTime(row.return_date) : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="fine_amount" label="罚款" width="100">
                <template #default="{ row }">
                  <span v-if="row.fine_amount > 0">¥{{ row.fine_amount }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'borrowed' || row.status === 'overdue'"
                    size="small"
                    type="success"
                    @click="handleReturn(row)"
                  >
                    还书
                  </el-button>
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
              @size-change="fetchRecords"
              @current-change="fetchRecords"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <el-dialog v-model="borrowDialogVisible" title="借书登记" width="500px">
      <el-form ref="borrowFormRef" :model="borrowForm" :rules="borrowRules" label-width="100px">
        <el-form-item label="读者" prop="reader_id">
          <el-select v-model="borrowForm.reader_id" filterable placeholder="选择读者" style="width: 100%;">
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.first_name}${reader.last_name} (${reader.username})`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图书" prop="book_id">
          <el-select v-model="borrowForm.book_id" filterable placeholder="选择图书" style="width: 100%;">
            <el-option
              v-for="book in availableBooks"
              :key="book.id"
              :label="`${book.title} (${book.isbn}) - 可借: ${book.available_quantity}`"
              :value="book.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借阅天数" prop="borrow_days">
          <el-input-number v-model="borrowForm.borrow_days" :min="1" :max="90" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBorrow" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const activeTab = ref('records')
const records = ref([])
const readers = ref([])
const availableBooks = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const borrowDialogVisible = ref(false)
const borrowFormRef = ref()

const borrowForm = reactive({
  reader_id: '',
  book_id: '',
  borrow_days: 30
})

const borrowRules = {
  reader_id: [{ required: true, message: '请选择读者', trigger: 'change' }],
  book_id: [{ required: true, message: '请选择图书', trigger: 'change' }]
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'borrowed': 'primary',
    'returned': 'success',
    'overdue': 'danger',
    'lost': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'borrowed': '借阅中',
    'returned': '已归还',
    'overdue': '已逾期',
    'lost': '已遗失'
  }
  return texts[status] || status
}

const fetchRecords = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchStatus.value) params.status = searchStatus.value
    const res = await axios.get('/borrow-records/', { params })
    records.value = res.data.results || res.data
    total.value = res.data.count || records.value.length
  } catch (e) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loading.value = false
  }
}

const fetchReaders = async () => {
  try {
    const res = await axios.get('/users/', { params: { role: 'reader' } })
    readers.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchAvailableBooks = async () => {
  try {
    const res = await axios.get('/books/', { params: { status: 'available' } })
    availableBooks.value = (res.data.results || res.data).filter(b => b.available_quantity > 0)
  } catch (e) {
    console.error(e)
  }
}

const handleBorrow = () => {
  Object.assign(borrowForm, {
    reader_id: '',
    book_id: '',
    borrow_days: 30
  })
  fetchReaders()
  fetchAvailableBooks()
  borrowDialogVisible.value = true
}

const submitBorrow = async () => {
  try {
    submitting.value = true
    await axios.post('/borrow-records/borrow/', borrowForm)
    ElMessage.success('借书登记成功')
    borrowDialogVisible.value = false
    fetchRecords()
  } catch (e) {
    const errors = e.response?.data
    if (errors) {
      const firstError = Object.values(errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error('登记失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleReturn = (row) => {
  ElMessageBox.confirm(`确定要归还图书《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.post('/borrow-records/return_book/', { record_id: row.id })
      ElMessage.success('还书成功')
      fetchRecords()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '还书失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.toolbar {
  padding: 0;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.borrow-page :deep(.el-pagination) {
  display: flex;
}
</style>
