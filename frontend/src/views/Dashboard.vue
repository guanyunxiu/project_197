<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card total-books">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">图书总数</div>
              <div class="stat-value">{{ stats.total_books }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card available-books">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">可借图书</div>
              <div class="stat-value">{{ stats.available_books }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card total-readers">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">读者总数</div>
              <div class="stat-value">{{ stats.total_readers }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card borrowed-books">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-label">借出图书</div>
              <div class="stat-value">{{ stats.borrowed_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header">最新借阅记录</span>
          </template>
          <el-table :data="recentRecords" style="width: 100%">
            <el-table-column prop="reader_name" label="读者" />
            <el-table-column prop="book_title" label="图书" />
            <el-table-column prop="borrow_date" label="借阅日期">
              <template #default="{ row }">
                {{ formatDate(row.borrow_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header">逾期提醒</span>
          </template>
          <el-alert
            v-if="stats.overdue_count > 0"
            :title="`有 ${stats.overdue_count} 本图书已逾期，请及时处理`"
            type="warning"
            show-icon
            class="mb20"
          />
          <el-table :data="overdueRecords" style="width: 100%">
            <el-table-column prop="reader_name" label="读者" />
            <el-table-column prop="book_title" label="图书" />
            <el-table-column prop="due_date" label="应还日期">
              <template #default="{ row }">
                {{ formatDate(row.due_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="fine_amount" label="罚款金额">
              <template #default="{ row }">
                ¥{{ row.fine_amount }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({
  total_books: 0,
  available_books: 0,
  total_readers: 0,
  borrowed_count: 0,
  overdue_count: 0
})

const recentRecords = ref([])
const overdueRecords = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
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

const fetchStats = async () => {
  try {
    const res = await axios.get('/dashboard/stats/')
    stats.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchRecentRecords = async () => {
  try {
    const res = await axios.get('/borrow-records/', { params: { page_size: 5 } })
    recentRecords.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchOverdueRecords = async () => {
  try {
    const res = await axios.get('/borrow-records/', { params: { status: 'overdue', page_size: 5 } })
    overdueRecords.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchStats()
  fetchRecentRecords()
  fetchOverdueRecords()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.total-books {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.available-books {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.total-readers {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.borrowed-books {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info .stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-info .stat-value {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
}

.mt20 {
  margin-top: 20px;
}

.mb20 {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.total-books :deep(.el-card__body),
.available-books :deep(.el-card__body),
.total-readers :deep(.el-card__body),
.borrowed-books :deep(.el-card__body) {
  background: transparent;
}
</style>
