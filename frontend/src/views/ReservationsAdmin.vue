<template>
  <div class="reservations-admin-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card waiting">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">等待中</div>
              <div class="stat-value">{{ statistics.waiting_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card available">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">可借阅</div>
              <div class="stat-value">{{ statistics.available_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card completed">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">已完成</div>
              <div class="stat-value">{{ statistics.completed_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card expired">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">已过期</div>
              <div class="stat-value">{{ statistics.expired_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-form :inline="true" class="search-form">
        <el-form-item label="读者">
          <el-select
            v-model="searchReaderId"
            placeholder="选择读者"
            filterable
            clearable
            style="width: 200px;"
          >
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.first_name}${reader.last_name} (${reader.username})`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图书">
          <el-select
            v-model="searchBookId"
            placeholder="选择图书"
            filterable
            clearable
            style="width: 250px;"
          >
            <el-option
              v-for="book in books"
              :key="book.id"
              :label="`${book.title} (${book.isbn})`"
              :value="book.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchStatus"
            placeholder="选择状态"
            clearable
            style="width: 150px;"
          >
            <el-option label="等待中" value="waiting" />
            <el-option label="可借阅" value="available" />
            <el-option label="已完成" value="completed" />
            <el-option label="已过期" value="expired" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        :data="reservations"
        style="width: 100%; margin-top: 20px;"
        v-loading="loading"
        empty-text=""
      >
        <template #empty>
          <el-empty description="暂无预约记录" />
        </template>
        <el-table-column label="读者" width="150">
          <template #default="{ row }">
            {{ row.reader_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="图书" min-width="200">
          <template #default="{ row }">
            {{ row.book_title || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="queue_position" label="排队位置" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'waiting'" type="primary">
              第 {{ row.queue_position }} 位
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reservation_date" label="预约日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.reservation_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="available_notify_date" label="可借通知日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.available_notify_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="expiry_date" label="过期日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.expiry_date) }}
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
        @size-change="fetchReservations"
        @current-change="fetchReservations"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const reservations = ref([])
const readers = ref([])
const books = ref([])
const loading = ref(false)
const searchReaderId = ref('')
const searchBookId = ref('')
const searchStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statistics = reactive({
  waiting_count: 0,
  available_count: 0,
  completed_count: 0,
  expired_count: 0
})

const getStatusType = (status) => {
  const types = {
    'waiting': 'primary',
    'available': 'success',
    'completed': 'info',
    'expired': 'danger',
    'cancelled': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'waiting': '等待中',
    'available': '可借阅',
    'completed': '已完成',
    'expired': '已过期',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const fetchReaders = async () => {
  try {
    const res = await axios.get('/users/', { params: { role: 'reader', page_size: 1000 } })
    readers.value = res.data.results || res.data
  } catch (e) {
    console.error('获取读者列表失败', e)
  }
}

const fetchBooks = async () => {
  try {
    const res = await axios.get('/books/', { params: { page_size: 1000 } })
    books.value = res.data.results || res.data
  } catch (e) {
    console.error('获取图书列表失败', e)
  }
}

const fetchReservations = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchReaderId.value) params.reader_id = searchReaderId.value
    if (searchBookId.value) params.book_id = searchBookId.value
    if (searchStatus.value) params.status = searchStatus.value
    
    const res = await axios.get('/api/reservations/', { params })
    reservations.value = res.data.results || res.data
    total.value = res.data.count || reservations.value.length
    
    if (res.data.statistics) {
      Object.assign(statistics, res.data.statistics)
    } else {
      updateStatistics()
    }
  } catch (e) {
    ElMessage.error('获取预约记录失败')
  } finally {
    loading.value = false
  }
}

const updateStatistics = () => {
  statistics.waiting_count = reservations.value.filter(r => r.status === 'waiting').length
  statistics.available_count = reservations.value.filter(r => r.status === 'available').length
  statistics.completed_count = reservations.value.filter(r => r.status === 'completed').length
  statistics.expired_count = reservations.value.filter(r => r.status === 'expired').length
}

const handleSearch = () => {
  currentPage.value = 1
  fetchReservations()
}

const handleReset = () => {
  searchReaderId.value = ''
  searchBookId.value = ''
  searchStatus.value = ''
  currentPage.value = 1
  fetchReservations()
}

onMounted(() => {
  fetchReaders()
  fetchBooks()
  fetchReservations()
})
</script>

<style scoped>
.stat-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-card.waiting {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.available {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-card.completed {
  background: linear-gradient(135deg, #8e9eab 0%, #eef2f3 100%);
}

.stat-card.expired {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info .stat-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-bottom: 8px;
  text-align: center;
}

.stat-info .stat-value {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
  text-align: center;
}

.stat-card.completed .stat-info .stat-label {
  color: rgba(0, 0, 0, 0.6);
}

.stat-card.completed .stat-info .stat-value {
  color: #303133;
}

.search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.reservations-admin-page :deep(.el-pagination) {
  display: flex;
}

.stat-card.waiting :deep(.el-card__body),
.stat-card.available :deep(.el-card__body),
.stat-card.completed :deep(.el-card__body),
.stat-card.expired :deep(.el-card__body) {
  background: transparent;
}
</style>
