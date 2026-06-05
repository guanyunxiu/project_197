<template>
  <div class="fines-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">未缴罚金总额</div>
            <div class="stat-value unpaid">¥{{ statistics.unpaid_total.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">未缴罚金笔数</div>
            <div class="stat-value">{{ statistics.unpaid_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">今日已缴笔数</div>
            <div class="stat-value paid">{{ statistics.today_paid_count }}</div>
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
          <el-option label="未缴" value="unpaid" />
          <el-option label="已缴" value="paid" />
          <el-option label="已减免" value="waived" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="fineRecords" style="width: 100%; margin-top: 20px;" v-loading="loading">
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
        <el-table-column prop="fine_type" label="罚金类型" width="120">
          <template #default="{ row }">
            {{ getFineTypeText(row.fine_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            ¥{{ row.amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="100">
          <template #default="{ row }">
            {{ row.overdue_days || 0 }}天
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ row.payment_method ? getPaymentMethodText(row.payment_method) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="缴纳时间" width="180">
          <template #default="{ row }">
            {{ row.paid_at ? formatDateTime(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'unpaid'"
              size="small"
              type="primary"
              @click="handlePay(row)"
            >
              缴纳
            </el-button>
            <el-button
              v-if="isSuperAdmin && row.status === 'unpaid'"
              size="small"
              type="warning"
              @click="handleWaive(row)"
            >
              减免
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
        @size-change="fetchFineRecords"
        @current-change="fetchFineRecords"
      />
    </el-card>

    <el-dialog v-model="payDialogVisible" title="缴纳罚金" width="400px">
      <el-form ref="payFormRef" :model="payForm" :rules="payRules" label-width="100px">
        <el-form-item label="罚金金额">
          <span style="color: #f56c6c; font-size: 18px; font-weight: bold;">
            ¥{{ payForm.amount.toFixed(2) }}
          </span>
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="payForm.payment_method" style="width: 100%;">
            <el-option label="现金" value="cash" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行卡" value="card" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPay" :loading="submitting">确认缴纳</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="waiveDialogVisible" title="减免罚金" width="500px">
      <el-form ref="waiveFormRef" :model="waiveForm" :rules="waiveRules" label-width="100px">
        <el-form-item label="罚金金额">
          <span style="color: #f56c6c; font-size: 18px; font-weight: bold;">
            ¥{{ waiveForm.amount.toFixed(2) }}
          </span>
        </el-form-item>
        <el-form-item label="减免原因" prop="reason">
          <el-input
            v-model="waiveForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入减免原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="waiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitWaive" :loading="submitting">确认减免</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isSuperAdmin = computed(() => user.role === 'super_admin')

const fineRecords = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchReader = ref('')
const searchBook = ref('')
const searchStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statistics = reactive({
  unpaid_total: 0,
  unpaid_count: 0,
  today_paid_count: 0
})

const payDialogVisible = ref(false)
const payFormRef = ref()
const payForm = reactive({
  id: null,
  amount: 0,
  payment_method: ''
})

const payRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const waiveDialogVisible = ref(false)
const waiveFormRef = ref()
const waiveForm = reactive({
  id: null,
  amount: 0,
  reason: ''
})

const waiveRules = {
  reason: [{ required: true, message: '请输入减免原因', trigger: 'blur' }]
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
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

const fetchFineRecords = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchReader.value) params.reader = searchReader.value
    if (searchBook.value) params.book = searchBook.value
    if (searchStatus.value) params.status = searchStatus.value
    const res = await axios.get('/fine-records/', { params })
    fineRecords.value = res.data.results || res.data
    total.value = res.data.count || fineRecords.value.length
    
    if (res.data.statistics) {
      Object.assign(statistics, res.data.statistics)
    }
  } catch (e) {
    ElMessage.error('获取罚金记录失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchFineRecords()
}

const handleReset = () => {
  searchReader.value = ''
  searchBook.value = ''
  searchStatus.value = ''
  currentPage.value = 1
  fetchFineRecords()
}

const handlePay = (row) => {
  Object.assign(payForm, {
    id: row.id,
    amount: row.amount,
    payment_method: ''
  })
  payDialogVisible.value = true
}

const handleWaive = (row) => {
  Object.assign(waiveForm, {
    id: row.id,
    amount: row.amount,
    reason: ''
  })
  waiveDialogVisible.value = true
}

const submitPay = async () => {
  try {
    await payFormRef.value.validate()
    submitting.value = true
    await axios.post('/fine-records/pay/', {
      id: payForm.id,
      payment_method: payForm.payment_method
    })
    ElMessage.success('缴纳成功')
    payDialogVisible.value = false
    fetchFineRecords()
  } catch (e) {
    if (e !== false) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('缴纳失败')
      }
    }
  } finally {
    submitting.value = false
  }
}

const submitWaive = async () => {
  try {
    await waiveFormRef.value.validate()
    submitting.value = true
    await axios.post(`/fine-records/${waiveForm.id}/waive/`, {
      reason: waiveForm.reason
    })
    ElMessage.success('减免成功')
    waiveDialogVisible.value = false
    fetchFineRecords()
  } catch (e) {
    if (e !== false) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('减免失败')
      }
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchFineRecords()
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

.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.fines-page :deep(.el-pagination) {
  display: flex;
}
</style>
