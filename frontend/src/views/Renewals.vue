<template>
  <div class="renewals-page">
    <el-row :gutter="20" class="mb20">
      <el-col :span="8">
        <el-card class="stat-card pending-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">待审核</div>
              <div class="stat-value">{{ stats.pending_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card approved-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">已通过</div>
              <div class="stat-value">{{ stats.approved_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card rejected-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">已拒绝</div>
              <div class="stat-value">{{ stats.rejected_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchReader"
          placeholder="搜索读者"
          style="width: 200px; margin-right: 10px;"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-input
          v-model="searchBook"
          placeholder="搜索图书"
          style="width: 200px; margin-right: 10px;"
          clearable
          @keyup.enter="handleSearch"
        />
        <el-select v-model="searchStatus" placeholder="选择状态" style="width: 150px; margin-right: 10px;" clearable>
          <el-option label="待审核" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="records" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="reader_name" label="读者" width="120" />
        <el-table-column prop="book_title" label="图书" min-width="200" />
        <el-table-column prop="request_date" label="申请日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.request_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="renew_days" label="续借天数" width="100" />
        <el-table-column prop="original_due_date" label="原应还日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.original_due_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="审核人" width="100">
          <template #default="{ row }">
            {{ row.reviewer_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="review_date" label="审核日期" width="180">
          <template #default="{ row }">
            {{ row.review_date ? formatDateTime(row.review_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="review_remark" label="审核备注" min-width="150">
          <template #default="{ row }">
            {{ row.review_remark || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              @click="handleApprove(row)"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="danger"
              @click="handleReject(row)"
            >
              拒绝
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
    </el-card>

    <el-dialog v-model="rejectDialogVisible" title="拒绝续借申请" width="500px">
      <el-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules" label-width="80px">
        <el-form-item label="备注" prop="remark">
          <el-input v-model="rejectForm.remark" type="textarea" :rows="4" placeholder="请输入拒绝原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReject" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const records = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchReader = ref('')
const searchBook = ref('')
const searchStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const stats = ref({
  pending_count: 0,
  approved_count: 0,
  rejected_count: 0
})

const rejectDialogVisible = ref(false)
const rejectFormRef = ref()
const currentRecord = ref(null)

const rejectForm = reactive({
  remark: ''
})

const rejectRules = {
  remark: [{ required: true, message: '请输入拒绝原因', trigger: 'blur' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return texts[status] || status
}

const fetchStats = async () => {
  try {
    const [pendingRes, approvedRes, rejectedRes] = await Promise.all([
      axios.get('/renew-records/', { params: { status: 'pending', page_size: 1 } }),
      axios.get('/renew-records/', { params: { status: 'approved', page_size: 1 } }),
      axios.get('/renew-records/', { params: { status: 'rejected', page_size: 1 } })
    ])
    stats.value = {
      pending_count: pendingRes.data.count || 0,
      approved_count: approvedRes.data.count || 0,
      rejected_count: rejectedRes.data.count || 0
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchRecords = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchReader.value || searchBook.value) {
      params.search = [searchReader.value, searchBook.value].filter(Boolean).join(' ')
    }
    if (searchStatus.value) params.status = searchStatus.value
    const res = await axios.get('/renew-records/', { params })
    records.value = res.data.results || res.data
    total.value = res.data.count || records.value.length
  } catch (e) {
    ElMessage.error('获取续借申请列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchRecords()
}

const handleReset = () => {
  searchReader.value = ''
  searchBook.value = ''
  searchStatus.value = ''
  currentPage.value = 1
  fetchRecords()
}

const handleApprove = (row) => {
  ElMessageBox.confirm(`确定要通过《${row.book_title}》的续借申请吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      submitting.value = true
      await axios.post('/renew-records/review/', {
        renew_id: row.id,
        approved: true,
        review_remark: ''
      })
      ElMessage.success('审核通过')
      fetchRecords()
      fetchStats()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '审核失败')
    } finally {
      submitting.value = false
    }
  }).catch(() => {})
}

const handleReject = (row) => {
  currentRecord.value = row
  rejectForm.remark = ''
  rejectDialogVisible.value = true
}

const submitReject = async () => {
  try {
    await rejectFormRef.validate()
    submitting.value = true
    await axios.post('/renew-records/review/', {
      renew_id: currentRecord.value.id,
      approved: false,
      review_remark: rejectForm.remark
    })
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    fetchRecords()
    fetchStats()
  } catch (e) {
    if (e !== false) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchRecords()
})
</script>

<style scoped>
.renewals-page {
  padding: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.stat-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.pending-card {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.approved-card {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.rejected-card {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.pending-card :deep(.el-card__body),
.approved-card :deep(.el-card__body),
.rejected-card :deep(.el-card__body) {
  background: transparent;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info .stat-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-info .stat-value {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
}

.mb20 {
  margin-bottom: 20px;
}

.renewals-page :deep(.el-pagination) {
  display: flex;
}
</style>
