<template>
  <div class="my-fines-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">待缴总额</div>
            <div class="stat-value unpaid">¥{{ statistics.unpaid_total.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">待缴笔数</div>
            <div class="stat-value">{{ statistics.unpaid_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">已缴总额</div>
            <div class="stat-value paid">¥{{ statistics.paid_total.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="按状态筛选" style="width: 150px; margin-right: 10px;" clearable @change="handleFilter">
          <el-option label="未缴" value="unpaid" />
          <el-option label="已缴" value="paid" />
          <el-option label="已减免" value="waived" />
        </el-select>
        <el-button @click="handleReset">重置筛选</el-button>
      </div>

      <el-table :data="fineRecords" style="width: 100%; margin-top: 20px;" v-loading="loading" :row-class-name="getRowClassName">
        <el-table-column label="图书" min-width="200">
          <template #default="{ row }">
            {{ row.book_title || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="fine_type" label="罚金类型" width="120">
          <template #default="{ row }">
            {{ getFineTypeText(row.fine_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span :class="{ 'unpaid-amount': row.status === 'unpaid' }">
              ¥{{ row.amount.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="100">
          <template #default="{ row }">
            {{ row.overdue_days || 0 }}天
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" :effect="row.status === 'unpaid' ? 'dark' : 'light'">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ row.payment_method ? getPaymentMethodText(row.payment_method) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="缴纳日期" width="180">
          <template #default="{ row }">
            {{ row.paid_at ? formatDate(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.remark || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'unpaid'"
              size="small"
              type="primary"
              @click="handlePay(row)"
            >
              在线缴纳
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && fineRecords.length === 0" description="暂无罚金记录" />

      <el-pagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
        @size-change="fetchMyFines"
        @current-change="fetchMyFines"
      />
    </el-card>

    <el-dialog v-model="payDialogVisible" title="在线缴纳罚金" width="450px">
      <el-form ref="payFormRef" :model="payForm" :rules="payRules" label-width="100px">
        <el-form-item label="罚金信息">
          <span style="color: #606266;">《{{ payForm.book_title }}》</span>
        </el-form-item>
        <el-form-item label="罚金类型">
          <span>{{ getFineTypeText(payForm.fine_type) }}</span>
        </el-form-item>
        <el-form-item label="应缴金额">
          <span style="color: #f56c6c; font-size: 24px; font-weight: bold;">
            ¥{{ payForm.amount.toFixed(2) }}
          </span>
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-radio-group v-model="payForm.payment_method">
            <el-radio value="wechat">微信支付</el-radio>
            <el-radio value="alipay">支付宝</el-radio>
            <el-radio value="card">银行卡</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPay" :loading="submitting">确认支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const fineRecords = ref([])
const loading = ref(false)
const submitting = ref(false)
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statistics = reactive({
  unpaid_total: 0,
  unpaid_count: 0,
  paid_total: 0
})

const payDialogVisible = ref(false)
const payFormRef = ref()
const payForm = reactive({
  id: null,
  book_title: '',
  fine_type: '',
  amount: 0,
  payment_method: ''
})

const payRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'unpaid': 'danger',
    'paid': 'success',
    'waived': 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'unpaid': '未缴',
    'paid': '已缴',
    'waived': '已减免'
  }
  return texts[status] || status
}

const getFineTypeText = (type) => {
  const texts = {
    'overdue': '逾期罚款',
    'damage': '损坏赔偿',
    'lost': '遗失赔偿',
    'other': '其他'
  }
  return texts[type] || type
}

const getPaymentMethodText = (method) => {
  const texts = {
    'cash': '现金',
    'wechat': '微信',
    'alipay': '支付宝',
    'card': '银行卡'
  }
  return texts[method] || method
}

const getRowClassName = ({ row }) => {
  return row.status === 'unpaid' ? 'unpaid-row' : ''
}

const fetchMyFines = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterStatus.value) params.status = filterStatus.value
    const res = await axios.get('/fine-records/my_fines/', { params })
    fineRecords.value = res.data.results || res.data
    total.value = res.data.count || fineRecords.value.length
  } catch (e) {
    ElMessage.error('获取罚金记录失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const res = await axios.get('/fine-records/my_unpaid_fines/')
    Object.assign(statistics, res.data)
  } catch (e) {
    console.error('获取统计信息失败', e)
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchMyFines()
}

const handleReset = () => {
  filterStatus.value = ''
  currentPage.value = 1
  fetchMyFines()
}

const handlePay = (row) => {
  Object.assign(payForm, {
    id: row.id,
    book_title: row.book_title,
    fine_type: row.fine_type,
    amount: row.amount,
    payment_method: ''
  })
  payDialogVisible.value = true
}

const submitPay = async () => {
  try {
    await payFormRef.value.validate()
    const payMethodText = getPaymentMethodText(payForm.payment_method)
    ElMessageBox.confirm(
      `确定使用${payMethodText}支付 ¥${payForm.amount.toFixed(2)} 吗？`,
      '确认支付',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        submitting.value = true
        await axios.post('/fine-records/pay/', {
          id: payForm.id,
          payment_method: payForm.payment_method
        })
        ElMessage.success('支付成功')
        payDialogVisible.value = false
        fetchMyFines()
        fetchStatistics()
      } catch (e) {
        const errors = e.response?.data
        if (errors) {
          const firstError = Object.values(errors)[0]
          ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
        } else {
          ElMessage.error('支付失败')
        }
      } finally {
        submitting.value = false
      }
    }).catch(() => {})
  } catch (e) {}
}

onMounted(() => {
  fetchMyFines()
  fetchStatistics()
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-value.unpaid {
  color: #f56c6c;
}

.stat-value.paid {
  color: #67c23a;
}

.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.my-fines-page :deep(.el-pagination) {
  display: flex;
}

.unpaid-amount {
  color: #f56c6c;
  font-weight: bold;
}

.my-fines-page :deep(.unpaid-row) {
  background-color: #fef0f0 !important;
}

.my-fines-page :deep(.unpaid-row:hover > td) {
  background-color: #fde2e2 !important;
}
</style>
