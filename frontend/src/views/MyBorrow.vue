<template>
  <div class="my-borrow-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="activeTab = 'all'">
          <div class="stat-content">
            <div class="stat-icon borrowed">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">借阅中</div>
              <div class="stat-value">{{ statistics.borrowing_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="activeTab = 'all'">
          <div class="stat-content">
            <div class="stat-icon returned">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">已归还</div>
              <div class="stat-value">{{ statistics.returned_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="goToOverdue">
          <div class="stat-content">
            <div class="stat-icon overdue">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">逾期数量</div>
              <div class="stat-value">{{ statistics.overdue_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="goToFines">
          <div class="stat-content">
            <div class="stat-icon fine">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">待缴罚金</div>
              <div class="stat-value">¥{{ statistics.unpaid_fine.toFixed(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="我的借阅" name="all" />
        <el-tab-pane label="逾期图书" name="overdue" />
        <el-tab-pane label="待缴罚金" name="fines" />
      </el-tabs>

      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="按状态筛选" style="width: 180px; margin-right: 10px;" clearable @change="handleFilter">
          <el-option label="借出中" value="borrowed" />
          <el-option label="已续借" value="renewed" />
          <el-option label="已逾期" value="overdue" />
          <el-option label="已归还" value="returned" />
          <el-option label="已丢失" value="lost" />
        </el-select>
        <el-button @click="handleReset">重置筛选</el-button>
      </div>

      <el-table
        :data="records"
        style="width: 100%; margin-top: 20px;"
        v-loading="loading"
        :row-class-name="getRowClassName"
        stripe
      >
        <el-table-column label="图书信息" min-width="280">
          <template #default="{ row }">
            <div class="book-info">
              <div class="book-cover">
                <img v-if="row.book_cover" :src="row.book_cover" :alt="row.book_title" />
                <el-icon v-else class="default-cover"><Reading /></el-icon>
              </div>
              <div class="book-detail">
                <div class="book-title">{{ row.book_title }}</div>
                <div class="book-isbn">ISBN: {{ row.book_isbn }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="借阅日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.borrow_date) }}
          </template>
        </el-table-column>
        <el-table-column label="应还日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="续借次数" width="100" align="center">
          <template #default="{ row }">
            {{ row.renew_count || 0 }} / {{ row.max_renew_count || 3 }}
          </template>
        </el-table-column>
        <el-table-column label="逾期天数" width="100" align="center">
          <template #default="{ row }">
            <span v-if="getOverdueDays(row) > 0" class="overdue-days">
              {{ getOverdueDays(row) }}天
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="罚金金额" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.fine_amount > 0" class="fine-amount">
              ¥{{ row.fine_amount.toFixed(2) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canRenew(row)"
              size="small"
              type="primary"
              @click="handleRenew(row)"
            >
              续借
            </el-button>
            <el-button
              v-else-if="row.status === 'borrowed' || row.status === 'renewed' || row.status === 'overdue'"
              size="small"
              type="primary"
              disabled
              title="已达到续借上限"
            >
              续借
            </el-button>
            <el-button
              v-if="row.status === 'borrowed' || row.status === 'renewed' || row.status === 'overdue'"
              size="small"
              type="success"
              @click="handleReturn(row)"
            >
              还书
            </el-button>
            <el-button
              v-if="row.fine_amount > 0 && row.status !== 'returned'"
              size="small"
              type="warning"
              @click="handlePayFine(row)"
            >
              支付罚金
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && records.length === 0" description="暂无借阅记录" />

      <el-pagination
        v-if="total > 0"
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

    <el-dialog v-model="renewDialogVisible" title="续借申请" width="500px">
      <el-form ref="renewFormRef" :model="renewForm" :rules="renewRules" label-width="100px">
        <el-form-item label="图书名称">
          <span>{{ renewForm.book_title }}</span>
        </el-form-item>
        <el-form-item label="当前应还">
          <span>{{ formatDate(renewForm.due_date) }}</span>
        </el-form-item>
        <el-form-item label="已续借">
          <span>{{ renewForm.renew_count || 0 }} 次</span>
        </el-form-item>
        <el-form-item label="续借天数" prop="renew_days">
          <el-input-number
            v-model="renewForm.renew_days"
            :min="7"
            :max="30"
            :step="7"
            style="width: 100%;"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            可选择7-30天，默认每次续借30天
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRenew" :loading="renewSubmitting">确认续借</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payFineDialogVisible" title="支付罚金" width="450px">
      <el-form ref="payFineFormRef" :model="payFineForm" :rules="payFineRules" label-width="100px">
        <el-form-item label="图书名称">
          <span>{{ payFineForm.book_title }}</span>
        </el-form-item>
        <el-form-item label="罚金金额">
          <span style="color: #f56c6c; font-size: 24px; font-weight: bold;">
            ¥{{ payFineForm.fine_amount.toFixed(2) }}
          </span>
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-radio-group v-model="payFineForm.payment_method">
            <el-radio value="wechat">微信支付</el-radio>
            <el-radio value="alipay">支付宝</el-radio>
            <el-radio value="card">银行卡</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payFineDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPayFine" :loading="payFineSubmitting">确认支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Reading, CircleCheck, Warning, Money } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const records = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterStatus = ref('')
const activeTab = ref('all')

const statistics = reactive({
  borrowing_count: 0,
  returned_count: 0,
  overdue_count: 0,
  unpaid_fine: 0
})

const renewDialogVisible = ref(false)
const renewSubmitting = ref(false)
const renewFormRef = ref()
const renewForm = reactive({
  id: null,
  book_title: '',
  due_date: '',
  renew_count: 0,
  renew_days: 30
})

const renewRules = {
  renew_days: [{ required: true, message: '请选择续借天数', trigger: 'change' }]
}

const payFineDialogVisible = ref(false)
const payFineSubmitting = ref(false)
const payFineFormRef = ref()
const payFineForm = reactive({
  id: null,
  book_title: '',
  fine_amount: 0,
  payment_method: ''
})

const payFineRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'borrowed': 'primary',
    'returned': 'success',
    'renewed': 'purple',
    'overdue': 'danger',
    'lost': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'borrowed': '借出中',
    'returned': '已归还',
    'renewed': '已续借',
    'overdue': '已逾期',
    'lost': '已丢失'
  }
  return texts[status] || status
}

const getOverdueDays = (row) => {
  if (row.status !== 'overdue') return 0
  const now = new Date()
  const due = new Date(row.due_date)
  const diff = Math.ceil((now - due) / (1000 * 60 * 60 * 24))
  return Math.max(0, diff)
}

const getRowClassName = ({ row }) => {
  if (row.status === 'overdue') return 'overdue-row'
  return ''
}

const canRenew = (row) => {
  if (row.status !== 'borrowed' && row.status !== 'renewed') return false
  const current = row.renew_count || 0
  const max = row.max_renew_count || 3
  return current < max
}

const fetchRecords = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (activeTab.value === 'overdue') params.status = 'overdue'
    
    const res = await axios.get('/borrow-records/my_borrows/', { params })
    records.value = res.data.results || res.data
    total.value = res.data.count || records.value.length
  } catch (e) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const res = await axios.get('/borrow-records/my_borrows/')
    const allRecords = res.data.results || res.data
    
    statistics.borrowing_count = allRecords.filter(r => 
      r.status === 'borrowed' || r.status === 'renewed'
    ).length
    statistics.returned_count = allRecords.filter(r => r.status === 'returned').length
    statistics.overdue_count = allRecords.filter(r => r.status === 'overdue').length
    statistics.unpaid_fine = allRecords.reduce((sum, r) => 
      sum + (r.status !== 'returned' ? (r.fine_amount || 0) : 0), 0
    )
  } catch (e) {
    console.error('获取统计信息失败', e)
  }
}

const handleTabChange = (tabName) => {
  if (tabName === 'fines') {
    router.push('/my-fines')
    return
  }
  if (tabName === 'overdue') {
    filterStatus.value = 'overdue'
  } else {
    filterStatus.value = ''
  }
  currentPage.value = 1
  fetchRecords()
}

const handleFilter = () => {
  currentPage.value = 1
  activeTab.value = 'all'
  fetchRecords()
}

const handleReset = () => {
  filterStatus.value = ''
  activeTab.value = 'all'
  currentPage.value = 1
  fetchRecords()
}

const goToOverdue = () => {
  activeTab.value = 'overdue'
  handleTabChange('overdue')
}

const goToFines = () => {
  router.push('/my-fines')
}

const handleRenew = (row) => {
  Object.assign(renewForm, {
    id: row.id,
    book_title: row.book_title,
    due_date: row.due_date,
    renew_count: row.renew_count || 0,
    renew_days: 30
  })
  renewDialogVisible.value = true
}

const submitRenew = async () => {
  try {
    await renewFormRef.value.validate()
    ElMessageBox.confirm(
      `确定续借《${renewForm.book_title}》${renewForm.renew_days}天吗？`,
      '确认续借',
      {
        confirmButtonText: '确认续借',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        renewSubmitting.value = true
        await axios.post(`/borrow-records/${renewForm.id}/renew/`, {
          renew_days: renewForm.renew_days
        })
        ElMessage.success('续借成功')
        renewDialogVisible.value = false
        fetchRecords()
        fetchStatistics()
      } catch (e) {
        const errors = e.response?.data
        if (errors) {
          const firstError = Object.values(errors)[0]
          ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
        } else {
          ElMessage.error('续借失败')
        }
      } finally {
        renewSubmitting.value = false
      }
    }).catch(() => {})
  } catch (e) {}
}

const handleReturn = (row) => {
  ElMessageBox.confirm(
    `确定归还《${row.book_title}》吗？`,
    '确认还书',
    {
      confirmButtonText: '确认归还',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      loading.value = true
      await axios.post(`/borrow-records/${row.id}/return_book/`)
      ElMessage.success('还书成功')
      fetchRecords()
      fetchStatistics()
    } catch (e) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('还书失败')
      }
    } finally {
      loading.value = false
    }
  }).catch(() => {})
}

const handlePayFine = (row) => {
  Object.assign(payFineForm, {
    id: row.id,
    book_title: row.book_title,
    fine_amount: row.fine_amount,
    payment_method: ''
  })
  payFineDialogVisible.value = true
}

const submitPayFine = async () => {
  try {
    await payFineFormRef.value.validate()
    const payMethodText = {
      'wechat': '微信支付',
      'alipay': '支付宝',
      'card': '银行卡'
    }[payFineForm.payment_method]
    
    ElMessageBox.confirm(
      `确定使用${payMethodText}支付 ¥${payFineForm.fine_amount.toFixed(2)} 吗？`,
      '确认支付',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        payFineSubmitting.value = true
        await axios.post('/fine-records/pay/', {
          borrow_record_id: payFineForm.id,
          payment_method: payFineForm.payment_method
        })
        ElMessage.success('支付成功')
        payFineDialogVisible.value = false
        fetchRecords()
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
        payFineSubmitting.value = false
      }
    }).catch(() => {})
  } catch (e) {}
}

onMounted(() => {
  fetchRecords()
  fetchStatistics()
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-icon.borrowed {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stat-icon.returned {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-icon.overdue {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.stat-icon.fine {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.book-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.book-cover {
  width: 50px;
  height: 70px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-cover {
  font-size: 24px;
  color: #c0c4cc;
}

.book-detail {
  min-width: 0;
}

.book-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-isbn {
  font-size: 12px;
  color: #909399;
}

.overdue-days {
  color: #f56c6c;
  font-weight: bold;
}

.fine-amount {
  color: #f56c6c;
  font-weight: bold;
}

.my-borrow-page :deep(.el-pagination) {
  display: flex;
}

.my-borrow-page :deep(.overdue-row) {
  background-color: #fef0f0 !important;
}

.my-borrow-page :deep(.overdue-row:hover > td) {
  background-color: #fde2e2 !important;
}

.my-borrow-page :deep(.el-tag--purple) {
  background-color: #9b59b6;
  border-color: #9b59b6;
  color: #fff;
}
</style>
