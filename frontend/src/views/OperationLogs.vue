<template>
  <div class="operation-logs-page">
    <el-card>
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="操作人">
            <el-input
              v-model="searchForm.operator_name"
              placeholder="请输入操作人姓名"
              clearable
              style="width: 200px;"
            />
          </el-form-item>
          <el-form-item label="操作类型">
            <el-select
              v-model="searchForm.operation_type"
              placeholder="请选择操作类型"
              clearable
              style="width: 160px;"
            >
              <el-option
                v-for="type in operationTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="目标模型">
            <el-select
              v-model="searchForm.target_model"
              placeholder="请选择目标模型"
              clearable
              style="width: 160px;"
            >
              <el-option
                v-for="model in targetModels"
                :key="model.value"
                :label="model.label"
                :value="model.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="操作时间">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 280px;"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        :data="logs"
        style="width: 100%; margin-top: 20px;"
        v-loading="loading"
        empty-text="暂无数据"
      >
        <el-table-column prop="operator_name" label="操作人" width="120" />
        <el-table-column prop="operation_type" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getOperationTypeColor(row.operation_type)">
              {{ getOperationTypeText(row.operation_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_model" label="目标模型" width="120">
          <template #default="{ row }">
            {{ getTargetModelText(row.target_model) }}
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="目标名称" min-width="150" />
        <el-table-column prop="description" label="操作描述" min-width="250" />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="!loading && logs.length === 0"
        description="暂无操作日志"
        style="margin-top: 40px;"
      />

      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const logs = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dateRange = ref([])

const searchForm = reactive({
  operator_id: '',
  operation_type: '',
  target_model: '',
  start_date: '',
  end_date: ''
})

const operationTypes = [
  { value: 'create', label: '创建' },
  { value: 'update', label: '更新' },
  { value: 'delete', label: '删除' },
  { value: 'login', label: '登录' },
  { value: 'logout', label: '登出' },
  { value: 'borrow', label: '借阅' },
  { value: 'return', label: '归还' },
  { value: 'reserve', label: '预约' },
  { value: 'cancel_reserve', label: '取消预约' },
  { value: 'renew', label: '续借' },
  { value: 'pay_fine', label: '缴纳罚款' }
]

const targetModels = [
  { value: 'book', label: '图书' },
  { value: 'category', label: '分类' },
  { value: 'reader', label: '读者' },
  { value: 'user', label: '用户' },
  { value: 'borrow_record', label: '借阅记录' },
  { value: 'reservation', label: '预约记录' },
  { value: 'fine', label: '罚款记录' },
  { value: 'system_config', label: '系统配置' }
]

const getOperationTypeColor = (type) => {
  const colors = {
    'create': 'success',
    'update': 'primary',
    'delete': 'danger',
    'login': 'success',
    'logout': 'info',
    'borrow': 'warning',
    'return': 'success',
    'reserve': 'primary',
    'cancel_reserve': 'info',
    'renew': 'warning',
    'pay_fine': 'success'
  }
  return colors[type] || 'info'
}

const getOperationTypeText = (type) => {
  const texts = {
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'login': '登录',
    'logout': '登出',
    'borrow': '借阅',
    'return': '归还',
    'reserve': '预约',
    'cancel_reserve': '取消预约',
    'renew': '续借',
    'pay_fine': '缴纳罚款'
  }
  return texts[type] || type
}

const getTargetModelText = (model) => {
  const texts = {
    'book': '图书',
    'category': '分类',
    'reader': '读者',
    'user': '用户',
    'borrow_record': '借阅记录',
    'reservation': '预约记录',
    'fine': '罚款记录',
    'system_config': '系统配置'
  }
  return texts[model] || model
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const fetchLogs = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchForm.operator_id) params.operator_id = searchForm.operator_id
    if (searchForm.operation_type) params.operation_type = searchForm.operation_type
    if (searchForm.target_model) params.target_model = searchForm.target_model
    if (searchForm.start_date) params.start_date = searchForm.start_date
    if (searchForm.end_date) params.end_date = searchForm.end_date

    const res = await axios.get('/api/operation-logs/', { params })
    logs.value = res.data.results || res.data
    total.value = res.data.count || logs.value.length
  } catch (e) {
    ElMessage.error('获取操作日志失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (dateRange.value && dateRange.value.length === 2) {
    searchForm.start_date = dateRange.value[0]
    searchForm.end_date = dateRange.value[1]
  } else {
    searchForm.start_date = ''
    searchForm.end_date = ''
  }
  currentPage.value = 1
  fetchLogs()
}

const handleReset = () => {
  searchForm.operator_id = ''
  searchForm.operation_type = ''
  searchForm.target_model = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  dateRange.value = []
  currentPage.value = 1
  fetchLogs()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchLogs()
}

const handleCurrentChange = () => {
  fetchLogs()
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
}

.operation-logs-page :deep(.el-pagination) {
  display: flex;
}

.operation-logs-page :deep(.el-form--inline .el-form-item) {
  margin-right: 0;
}
</style>
