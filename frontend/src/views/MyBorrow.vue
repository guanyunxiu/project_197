<template>
  <div class="my-borrow-page">
    <el-card>
      <el-table :data="records" style="width: 100%;" v-loading="loading">
        <el-table-column prop="book_title" label="图书名称" min-width="200" />
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
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fine_amount" label="预计罚款" width="120">
          <template #default="{ row }">
            <span v-if="row.status === 'overdue' && row.fine_amount > 0" style="color: #f56c6c;">
              ¥{{ row.fine_amount }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="剩余天数" width="120">
          <template #default="{ row }">
            <span :style="{ color: getDaysColor(row) }">
              {{ getRemainingDays(row) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && records.length === 0" description="暂无在借图书" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const records = ref([])
const loading = ref(false)

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'borrowed': 'primary',
    'overdue': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'borrowed': '借阅中',
    'overdue': '已逾期'
  }
  return texts[status] || status
}

const getRemainingDays = (row) => {
  const now = new Date()
  const due = new Date(row.due_date)
  const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24))
  if (diff > 0) return `还剩 ${diff} 天`
  if (diff === 0) return '今日到期'
  return `逾期 ${Math.abs(diff)} 天`
}

const getDaysColor = (row) => {
  const now = new Date()
  const due = new Date(row.due_date)
  const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24))
  if (diff < 0) return '#f56c6c'
  if (diff <= 3) return '#e6a23c'
  return '#67c23a'
}

const fetchRecords = async () => {
  try {
    loading.value = true
    const res = await axios.get('/borrow-records/my_borrowing/')
    records.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取借阅信息失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.my-borrow-page {
  padding: 0;
}
</style>
