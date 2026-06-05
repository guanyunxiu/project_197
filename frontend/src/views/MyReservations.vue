<template>
  <div class="my-reservations-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">等待中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.available }}</div>
              <div class="stat-label">可借阅</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon gray">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div class="filter-bar">
        <span class="filter-label">状态筛选：</span>
        <el-select v-model="statusFilter" placeholder="全部状态" style="width: 150px; margin-right: 10px;" clearable @change="handleFilterChange">
          <el-option label="等待中" value="pending" />
          <el-option label="可借阅" value="available" />
          <el-option label="已完成" value="completed" />
          <el-option label="已过期" value="expired" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <el-alert
        v-if="stats.available > 0"
        :title="`您有 ${stats.available} 本图书可以借阅，请尽快前往图书馆办理借阅手续！`"
        type="success"
        show-icon
        style="margin: 15px 0;"
      />

      <el-table :data="reservations" style="width: 100%; margin-top: 20px;" v-loading="loading" :row-class-name="tableRowClassName">
        <el-table-column prop="book_title" label="图书" min-width="200">
          <template #default="{ row }">
            <div class="book-info">
              <span class="book-title">{{ row.book_title }}</span>
              <el-tag v-if="row.status === 'available'" type="success" effect="dark" style="margin-left: 8px;">
                可借阅
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="book_isbn" label="ISBN" width="150" />
        <el-table-column prop="queue_position" label="排队位置" width="100">
          <template #default="{ row }">
            <span v-if="row.status === 'pending'" class="queue-position">
              第 {{ row.queue_position }} 位
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reservation_date" label="预约日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.reservation_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="available_date" label="可借通知日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.available_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="expiry_date" label="过期日期" width="180">
          <template #default="{ row }">
            <span :style="{ color: getExpiryColor(row) }">
              {{ formatDateTime(row.expiry_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending' || row.status === 'available'"
              size="small"
              type="danger"
              @click="handleCancel(row)"
            >
              取消预约
            </el-button>
            <span v-else class="no-action">-</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && reservations.length === 0" description="暂无预约记录" />

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="fetchReservations"
        @current-change="fetchReservations"
      />
    </el-card>

    <el-dialog v-model="cancelDialogVisible" title="取消预约" width="400px">
      <p>确定要取消《{{ currentReservation?.book_title }}》的预约吗？</p>
      <p v-if="currentReservation?.status === 'pending'" style="color: #e6a23c; margin-top: 10px;">
        <el-icon><Warning /></el-icon>
        取消后您将失去当前排队位置
      </p>
      <p v-if="currentReservation?.status === 'available'" style="color: #f56c6c; margin-top: 10px;">
        <el-icon><Warning /></el-icon>
        该图书当前可借阅，取消后可能需要重新预约
      </p>
      <template #footer>
        <el-button @click="cancelDialogVisible = false">返回</el-button>
        <el-button type="danger" @click="confirmCancel" :loading="cancelling">确认取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, CircleCheck, Check, Refresh, Warning } from '@element-plus/icons-vue'
import axios from 'axios'

const reservations = ref([])
const loading = ref(false)
const cancelling = ref(false)
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const cancelDialogVisible = ref(false)
const currentReservation = ref(null)

const stats = reactive({
  pending: 0,
  available: 0,
  completed: 0
})

const getStatusType = (status) => {
  const types = {
    'pending': 'primary',
    'available': 'success',
    'completed': 'info',
    'expired': 'danger',
    'cancelled': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'pending': '等待中',
    'available': '可借阅',
    'completed': '已完成',
    'expired': '已过期',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getExpiryColor = (row) => {
  if (row.status !== 'available' && row.status !== 'pending') return ''
  const now = new Date()
  const expiry = new Date(row.expiry_date)
  const diff = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))
  if (diff <= 0) return '#f56c6c'
  if (diff <= 2) return '#e6a23c'
  return ''
}

const tableRowClassName = ({ row }) => {
  if (row.status === 'available') {
    return 'highlight-row'
  }
  return ''
}

const fetchReservations = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await axios.get('/reservations/my_reservations/', { params })
    reservations.value = res.data.results || res.data
    total.value = res.data.count || reservations.value.length
    calculateStats()
  } catch (e) {
    ElMessage.error('获取预约记录失败')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.pending = reservations.value.filter(r => r.status === 'pending').length
  stats.available = reservations.value.filter(r => r.status === 'available').length
  stats.completed = reservations.value.filter(r => r.status === 'completed').length
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchReservations()
}

const handleRefresh = () => {
  fetchReservations()
}

const handleCancel = (row) => {
  currentReservation.value = row
  cancelDialogVisible.value = true
}

const confirmCancel = async () => {
  if (!currentReservation.value) return
  try {
    cancelling.value = true
    await axios.post(`/reservations/${currentReservation.value.id}/cancel/`)
    ElMessage.success('取消预约成功')
    cancelDialogVisible.value = false
    fetchReservations()
  } catch (e) {
    ElMessage.error('取消预约失败')
  } finally {
    cancelling.value = false
  }
}

onMounted(() => {
  fetchReservations()
})
</script>

<style scoped>
.my-reservations-page {
  padding: 0;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.green {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-icon.gray {
  background: linear-gradient(135deg, #636e72 0%, #b2bec3 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-label {
  color: #606266;
  font-size: 14px;
}

.book-info {
  display: flex;
  align-items: center;
}

.book-title {
  font-weight: 500;
}

.queue-position {
  color: #409eff;
  font-weight: 500;
}

.no-action {
  color: #c0c4cc;
}

.my-reservations-page :deep(.el-pagination) {
  display: flex;
}

.my-reservations-page :deep(.highlight-row) {
  background-color: #f0f9eb !important;
}

.my-reservations-page :deep(.highlight-row:hover) {
  background-color: #e1f3d8 !important;
}
</style>
