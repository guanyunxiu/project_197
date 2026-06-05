<template>
  <div class="my-history-page">
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
        <el-table-column prop="return_date" label="归还日期" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.return_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success">已归还</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fine_amount" label="罚款金额" width="120">
          <template #default="{ row }">
            <span v-if="row.fine_amount > 0" style="color: #f56c6c;">¥{{ row.fine_amount }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && records.length === 0" description="暂无借阅历史" />
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

const fetchRecords = async () => {
  try {
    loading.value = true
    const res = await axios.get('/borrow-records/my_history/')
    records.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取借阅历史失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.my-history-page {
  padding: 0;
}
</style>
