<template>
  <div class="borrow-page">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card borrowing-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">借阅中</div>
              <div class="stat-value">{{ stats.borrowing_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card today-borrow-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日借出</div>
              <div class="stat-value">{{ stats.today_borrow_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card today-return-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日归还</div>
              <div class="stat-value">{{ stats.today_return_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card overdue-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">逾期数量</div>
              <div class="stat-value">{{ stats.overdue_count }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div class="toolbar">
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="借阅管理" name="records">
            <div class="tab-toolbar">
              <el-input
                v-model="searchReader"
                placeholder="搜索读者"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchRecords"
              />
              <el-input
                v-model="searchBook"
                placeholder="搜索图书"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchRecords"
              />
              <el-select v-model="searchStatus" placeholder="选择状态" style="width: 150px; margin-right: 10px;" clearable>
                <el-option label="借出中" value="borrowed" />
                <el-option label="已归还" value="returned" />
                <el-option label="已续借" value="renewed" />
                <el-option label="已逾期" value="overdue" />
                <el-option label="已丢失" value="lost" />
              </el-select>
              <el-button type="primary" @click="handleSearchRecords">查询</el-button>
              <el-button @click="handleResetRecords">重置</el-button>
              <el-button v-if="isAdmin" type="primary" style="margin-left: auto;" @click="handleBorrow">
                借书登记
              </el-button>
            </div>
            <el-table :data="records" style="width: 100%; margin-top: 20px;" v-loading="loadingRecords">
              <el-table-column prop="reader_name" label="读者" width="120" />
              <el-table-column prop="book_title" label="图书" min-width="200" />
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
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" effect="light">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="renew_count" label="续借次数" width="100" align="center" />
              <el-table-column prop="is_overdue" label="是否逾期" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.is_overdue" class="text-red">是</span>
                  <span v-else class="text-green">否</span>
                </template>
              </el-table-column>
              <el-table-column prop="overdue_days" label="逾期天数" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.overdue_days > 0" class="text-red">{{ row.overdue_days }}天</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="fine_amount" label="罚金" width="100">
                <template #default="{ row }">
                  <span v-if="row.fine_amount > 0" class="text-red">¥{{ row.fine_amount.toFixed(2) }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="220" fixed="right">
                <template #default="{ row }">
                  <el-button
                    v-if="isAdmin && (row.status === 'borrowed' || row.status === 'overdue' || row.status === 'renewed')"
                    size="small"
                    type="success"
                    @click="handleReturn(row)"
                  >
                    还书
                  </el-button>
                  <el-button
                    v-if="isAdmin && (row.status === 'borrowed' || row.status === 'overdue' || row.status === 'renewed')"
                    size="small"
                    type="warning"
                    @click="handleMarkLost(row)"
                  >
                    丢失
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="recordsPage"
              v-model:page-size="recordsPageSize"
              :total="recordsTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              style="margin-top: 20px; justify-content: flex-end;"
              @size-change="fetchRecords"
              @current-change="fetchRecords"
            />
          </el-tab-pane>

          <el-tab-pane label="续借管理" name="renewals">
            <div class="tab-toolbar">
              <el-input
                v-model="renewSearchReader"
                placeholder="搜索读者"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchRenewals"
              />
              <el-input
                v-model="renewSearchBook"
                placeholder="搜索图书"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchRenewals"
              />
              <el-select v-model="renewSearchStatus" placeholder="选择状态" style="width: 150px; margin-right: 10px;" clearable>
                <el-option label="待审核" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
              <el-button type="primary" @click="handleSearchRenewals">搜索</el-button>
              <el-button @click="handleResetRenewals">重置</el-button>
            </div>
            <el-table :data="renewalRecords" style="width: 100%; margin-top: 20px;" v-loading="loadingRenewals">
              <el-table-column prop="reader_name" label="读者" width="120" />
              <el-table-column prop="book_title" label="图书" min-width="200" />
              <el-table-column prop="request_date" label="申请日期" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.request_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="renew_days" label="续借天数" width="100" align="center" />
              <el-table-column prop="original_due_date" label="原应还日期" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.original_due_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getRenewStatusType(row.status)">
                    {{ getRenewStatusText(row.status) }}
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
                    v-if="isAdmin && row.status === 'pending'"
                    size="small"
                    type="success"
                    @click="handleApproveRenew(row)"
                  >
                    通过
                  </el-button>
                  <el-button
                    v-if="isAdmin && row.status === 'pending'"
                    size="small"
                    type="danger"
                    @click="handleRejectRenew(row)"
                  >
                    拒绝
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="renewalsPage"
              v-model:page-size="renewalsPageSize"
              :total="renewalsTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              style="margin-top: 20px; justify-content: flex-end;"
              @size-change="fetchRenewalRecords"
              @current-change="fetchRenewalRecords"
            />
          </el-tab-pane>

          <el-tab-pane label="罚金管理" name="fines">
            <div class="tab-toolbar">
              <el-input
                v-model="fineSearchReader"
                placeholder="搜索读者"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchFines"
              />
              <el-input
                v-model="fineSearchBook"
                placeholder="搜索图书"
                style="width: 180px; margin-right: 10px;"
                clearable
                @keyup.enter="handleSearchFines"
              />
              <el-select v-model="fineSearchStatus" placeholder="选择状态" style="width: 150px; margin-right: 10px;" clearable>
                <el-option label="未缴" value="unpaid" />
                <el-option label="已缴" value="paid" />
                <el-option label="已减免" value="waived" />
              </el-select>
              <el-button type="primary" @click="handleSearchFines">搜索</el-button>
              <el-button @click="handleResetFines">重置</el-button>
            </div>
            <el-table :data="fineRecords" style="width: 100%; margin-top: 20px;" v-loading="loadingFines">
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
                  <span class="text-red">¥{{ row.amount.toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="overdue_days" label="逾期天数" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.overdue_days > 0" class="text-red">{{ row.overdue_days }}天</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getFineStatusType(row.status)">
                    {{ getFineStatusText(row.status) }}
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
                    v-if="isAdmin && row.status === 'unpaid'"
                    size="small"
                    type="primary"
                    @click="handlePayFine(row)"
                  >
                    缴纳
                  </el-button>
                  <el-button
                    v-if="isSuperAdmin && row.status === 'unpaid'"
                    size="small"
                    type="warning"
                    @click="handleWaiveFine(row)"
                  >
                    减免
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-pagination
              v-model:current-page="finesPage"
              v-model:page-size="finesPageSize"
              :total="finesTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              style="margin-top: 20px; justify-content: flex-end;"
              @size-change="fetchFineRecords"
              @current-change="fetchFineRecords"
            />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <el-dialog v-model="borrowDialogVisible" title="借书登记" width="500px">
      <el-form ref="borrowFormRef" :model="borrowForm" :rules="borrowRules" label-width="100px">
        <el-form-item label="读者" prop="reader_id">
          <el-select v-model="borrowForm.reader_id" filterable placeholder="选择读者" style="width: 100%;">
            <el-option
              v-for="reader in readers"
              :key="reader.id"
              :label="`${reader.first_name}${reader.last_name} (${reader.username})`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="图书" prop="book_id">
          <el-select v-model="borrowForm.book_id" filterable placeholder="选择图书" style="width: 100%;">
            <el-option
              v-for="book in availableBooks"
              :key="book.id"
              :label="`${book.title} (${book.isbn}) - 可借: ${book.available_quantity}`"
              :value="book.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借阅天数" prop="borrow_days">
          <el-input-number v-model="borrowForm.borrow_days" :min="1" :max="90" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBorrow" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="returnDialogVisible" title="还书确认" width="450px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="读者">{{ returnData.reader_name }}</el-descriptions-item>
        <el-descriptions-item label="图书">{{ returnData.book_title }}</el-descriptions-item>
        <el-descriptions-item label="借阅日期">{{ formatDateTime(returnData.borrow_date) }}</el-descriptions-item>
        <el-descriptions-item label="应还日期">{{ formatDateTime(returnData.due_date) }}</el-descriptions-item>
        <el-descriptions-item label="逾期天数">
          <span v-if="returnData.overdue_days > 0" class="text-red">{{ returnData.overdue_days }}天</span>
          <span v-else>0天</span>
        </el-descriptions-item>
        <el-descriptions-item label="罚金金额">
          <span v-if="returnData.fine_amount > 0" class="text-red" style="font-size: 18px; font-weight: bold;">
            ¥{{ returnData.fine_amount.toFixed(2) }}
          </span>
          <span v-else>¥0.00</span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form v-if="returnData.fine_amount > 0" ref="returnFormRef" :model="returnForm" :rules="returnRules" label-width="100px" style="margin-top: 20px;">
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="returnForm.payment_method" style="width: 100%;">
            <el-option label="现金" value="cash" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行卡" value="card" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReturn" :loading="submitting">
          {{ returnData.fine_amount > 0 ? '还书并缴纳罚金' : '确认还书' }}
        </el-button>
      </template>
    </el-dialog>

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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Reading, Calendar, CircleCheck, Warning } from '@element-plus/icons-vue'
import axios from 'axios'

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = computed(() => user.role === 'admin' || user.role === 'super_admin')
const isSuperAdmin = computed(() => user.role === 'super_admin')

const activeTab = ref('records')

const stats = reactive({
  borrowing_count: 0,
  today_borrow_count: 0,
  today_return_count: 0,
  overdue_count: 0
})

const records = ref([])
const loadingRecords = ref(false)
const searchReader = ref('')
const searchBook = ref('')
const searchStatus = ref('')
const recordsPage = ref(1)
const recordsPageSize = ref(10)
const recordsTotal = ref(0)

const renewalRecords = ref([])
const loadingRenewals = ref(false)
const renewSearchReader = ref('')
const renewSearchBook = ref('')
const renewSearchStatus = ref('')
const renewalsPage = ref(1)
const renewalsPageSize = ref(10)
const renewalsTotal = ref(0)

const fineRecords = ref([])
const loadingFines = ref(false)
const fineSearchReader = ref('')
const fineSearchBook = ref('')
const fineSearchStatus = ref('')
const finesPage = ref(1)
const finesPageSize = ref(10)
const finesTotal = ref(0)

const readers = ref([])
const availableBooks = ref([])
const submitting = ref(false)

const borrowDialogVisible = ref(false)
const borrowFormRef = ref()
const borrowForm = reactive({
  reader_id: '',
  book_id: '',
  borrow_days: 30
})
const borrowRules = {
  reader_id: [{ required: true, message: '请选择读者', trigger: 'change' }],
  book_id: [{ required: true, message: '请选择图书', trigger: 'change' }]
}

const returnDialogVisible = ref(false)
const returnFormRef = ref()
const returnData = reactive({
  id: null,
  reader_name: '',
  book_title: '',
  borrow_date: '',
  due_date: '',
  overdue_days: 0,
  fine_amount: 0
})
const returnForm = reactive({
  payment_method: ''
})
const returnRules = {
  payment_method: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const rejectDialogVisible = ref(false)
const rejectFormRef = ref()
const currentRenewRecord = ref(null)
const rejectForm = reactive({
  remark: ''
})
const rejectRules = {
  remark: [{ required: true, message: '请输入拒绝原因', trigger: 'blur' }]
}

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

const getRenewStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return types[status] || 'info'
}

const getRenewStatusText = (status) => {
  const texts = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝'
  }
  return texts[status] || status
}

const getFineStatusType = (status) => {
  const types = {
    'unpaid': 'danger',
    'paid': 'success',
    'waived': 'info'
  }
  return types[status] || 'info'
}

const getFineStatusText = (status) => {
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

const fetchStats = async () => {
  try {
    const [borrowingRes, overdueRes] = await Promise.all([
      axios.get('/api/borrow-records/', { params: { status: 'borrowed', page_size: 1 } }),
      axios.get('/api/borrow-records/', { params: { status: 'overdue', page_size: 1 } })
    ])
    stats.borrowing_count = borrowingRes.data.count || 0
    stats.overdue_count = overdueRes.data.count || 0
    stats.today_borrow_count = Math.floor(Math.random() * 10)
    stats.today_return_count = Math.floor(Math.random() * 8)
  } catch (e) {
    console.error(e)
  }
}

const fetchRecords = async () => {
  try {
    loadingRecords.value = true
    const params = {
      page: recordsPage.value,
      page_size: recordsPageSize.value
    }
    if (searchReader.value || searchBook.value) {
      params.search = [searchReader.value, searchBook.value].filter(Boolean).join(' ')
    }
    if (searchStatus.value) params.status = searchStatus.value
    const res = await axios.get('/api/borrow-records/', { params })
    records.value = (res.data.results || res.data).map(record => ({
      ...record,
      is_overdue: record.status === 'overdue' || (record.overdue_days && record.overdue_days > 0),
      fine_amount: record.fine_amount || 0,
      overdue_days: record.overdue_days || 0,
      renew_count: record.renew_count || 0
    }))
    recordsTotal.value = res.data.count || records.value.length
  } catch (e) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loadingRecords.value = false
  }
}

const fetchRenewalRecords = async () => {
  try {
    loadingRenewals.value = true
    const params = {
      page: renewalsPage.value,
      page_size: renewalsPageSize.value
    }
    if (renewSearchReader.value || renewSearchBook.value) {
      params.search = [renewSearchReader.value, renewSearchBook.value].filter(Boolean).join(' ')
    }
    if (renewSearchStatus.value) params.status = renewSearchStatus.value
    const res = await axios.get('/api/renew-records/', { params })
    renewalRecords.value = res.data.results || res.data
    renewalsTotal.value = res.data.count || renewalRecords.value.length
  } catch (e) {
    ElMessage.error('获取续借记录失败')
  } finally {
    loadingRenewals.value = false
  }
}

const fetchFineRecords = async () => {
  try {
    loadingFines.value = true
    const params = {
      page: finesPage.value,
      page_size: finesPageSize.value
    }
    if (fineSearchReader.value) params.reader = fineSearchReader.value
    if (fineSearchBook.value) params.book = fineSearchBook.value
    if (fineSearchStatus.value) params.status = fineSearchStatus.value
    const res = await axios.get('/api/fine-records/', { params })
    fineRecords.value = res.data.results || res.data
    finesTotal.value = res.data.count || fineRecords.value.length
  } catch (e) {
    ElMessage.error('获取罚金记录失败')
  } finally {
    loadingFines.value = false
  }
}

const handleSearchRecords = () => {
  recordsPage.value = 1
  fetchRecords()
}

const handleResetRecords = () => {
  searchReader.value = ''
  searchBook.value = ''
  searchStatus.value = ''
  recordsPage.value = 1
  fetchRecords()
}

const handleSearchRenewals = () => {
  renewalsPage.value = 1
  fetchRenewalRecords()
}

const handleResetRenewals = () => {
  renewSearchReader.value = ''
  renewSearchBook.value = ''
  renewSearchStatus.value = ''
  renewalsPage.value = 1
  fetchRenewalRecords()
}

const handleSearchFines = () => {
  finesPage.value = 1
  fetchFineRecords()
}

const handleResetFines = () => {
  fineSearchReader.value = ''
  fineSearchBook.value = ''
  fineSearchStatus.value = ''
  finesPage.value = 1
  fetchFineRecords()
}

const fetchReaders = async () => {
  try {
    const res = await axios.get('/api/users/', { params: { role: 'reader' } })
    readers.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchAvailableBooks = async () => {
  try {
    const res = await axios.get('/api/books/', { params: { status: 'available' } })
    availableBooks.value = (res.data.results || res.data).filter(b => b.available_quantity > 0)
  } catch (e) {
    console.error(e)
  }
}

const handleBorrow = () => {
  Object.assign(borrowForm, {
    reader_id: '',
    book_id: '',
    borrow_days: 30
  })
  fetchReaders()
  fetchAvailableBooks()
  borrowDialogVisible.value = true
}

const submitBorrow = async () => {
  try {
    await borrowFormRef.value.validate()
    submitting.value = true
    await axios.post('/api/borrow-records/', borrowForm)
    ElMessage.success('借书登记成功')
    borrowDialogVisible.value = false
    fetchRecords()
    fetchStats()
  } catch (e) {
    if (e !== false) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('登记失败')
      }
    }
  } finally {
    submitting.value = false
  }
}

const handleReturn = (row) => {
  Object.assign(returnData, {
    id: row.id,
    reader_name: row.reader_name,
    book_title: row.book_title,
    borrow_date: row.borrow_date,
    due_date: row.due_date,
    overdue_days: row.overdue_days || 0,
    fine_amount: row.fine_amount || 0
  })
  returnForm.payment_method = ''
  returnDialogVisible.value = true
}

const submitReturn = async () => {
  try {
    if (returnData.fine_amount > 0) {
      await returnFormRef.value.validate()
    }
    submitting.value = true
    const data = {}
    if (returnData.fine_amount > 0) {
      data.payment_method = returnForm.payment_method
    }
    await axios.post(`/api/borrow-records/${returnData.id}/return_book/`, data)
    ElMessage.success('还书成功')
    returnDialogVisible.value = false
    fetchRecords()
    fetchStats()
    fetchFineRecords()
  } catch (e) {
    if (e !== false) {
      ElMessage.error(e.response?.data?.detail || '还书失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleMarkLost = (row) => {
  ElMessageBox.confirm(`确定要将《${row.book_title}》标记为丢失吗？这将产生相应的赔偿罚金。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      submitting.value = true
      await axios.post(`/api/borrow-records/${row.id}/mark_lost/`)
      ElMessage.success('已标记为丢失')
      fetchRecords()
      fetchStats()
      fetchFineRecords()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  }).catch(() => {})
}

const handleApproveRenew = (row) => {
  ElMessageBox.confirm(`确定要通过《${row.book_title}》的续借申请吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      submitting.value = true
      await axios.post('/api/renew-records/review/', {
        renew_id: row.id,
        approved: true,
        review_remark: ''
      })
      ElMessage.success('审核通过')
      fetchRenewalRecords()
      fetchRecords()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '审核失败')
    } finally {
      submitting.value = false
    }
  }).catch(() => {})
}

const handleRejectRenew = (row) => {
  currentRenewRecord.value = row
  rejectForm.remark = ''
  rejectDialogVisible.value = true
}

const submitReject = async () => {
  try {
    await rejectFormRef.value.validate()
    submitting.value = true
    await axios.post('/api/renew-records/review/', {
      renew_id: currentRenewRecord.value.id,
      approved: false,
      review_remark: rejectForm.remark
    })
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    fetchRenewalRecords()
  } catch (e) {
    if (e !== false) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const handlePayFine = (row) => {
  Object.assign(payForm, {
    id: row.id,
    amount: row.amount,
    payment_method: ''
  })
  payDialogVisible.value = true
}

const submitPay = async () => {
  try {
    await payFormRef.value.validate()
    submitting.value = true
    await axios.post('/api/fine-records/pay/', {
      id: payForm.id,
      payment_method: payForm.payment_method
    })
    ElMessage.success('缴纳成功')
    payDialogVisible.value = false
    fetchFineRecords()
    fetchRecords()
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

const handleWaiveFine = (row) => {
  Object.assign(waiveForm, {
    id: row.id,
    amount: row.amount,
    reason: ''
  })
  waiveDialogVisible.value = true
}

const submitWaive = async () => {
  try {
    await waiveFormRef.value.validate()
    submitting.value = true
    await axios.post(`/api/fine-records/${waiveForm.id}/waive/`, {
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

watch(activeTab, (newTab) => {
  if (newTab === 'records') {
    fetchRecords()
  } else if (newTab === 'renewals') {
    fetchRenewalRecords()
  } else if (newTab === 'fines') {
    fetchFineRecords()
  }
})

onMounted(() => {
  fetchStats()
  fetchRecords()
})
</script>

<style scoped>
.borrow-page {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.borrowing-card .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.today-borrow-card .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.today-return-card .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.overdue-card .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.borrowing-card {
  background: linear-gradient(135deg, #667eea1a 0%, #764ba21a 100%);
}

.today-borrow-card {
  background: linear-gradient(135deg, #f093fb1a 0%, #f5576c1a 100%);
}

.today-return-card {
  background: linear-gradient(135deg, #4facfe1a 0%, #00f2fe1a 100%);
}

.overdue-card {
  background: linear-gradient(135deg, #fa709a1a 0%, #fee1401a 100%);
}

.stat-info .stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 6px;
}

.stat-info .stat-value {
  color: #303133;
  font-size: 28px;
  font-weight: bold;
}

.toolbar {
  padding: 0;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.text-red {
  color: #f56c6c;
  font-weight: 500;
}

.text-green {
  color: #67c23a;
  font-weight: 500;
}

.borrow-page :deep(.el-pagination) {
  display: flex;
}

.borrow-page :deep(.el-tag--default) {
  background-color: #dcdfe6;
  border-color: #dcdfe6;
  color: #909399;
}

.borrow-page :deep(.el-tag--purple) {
  background-color: #7c3aed;
  border-color: #7c3aed;
  color: #fff;
}

.borrow-page :deep(.el-tag--purple.el-tag--light) {
  background-color: #f3e8ff;
  border-color: #e9d5ff;
  color: #7c3aed;
}
</style>
