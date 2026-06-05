<template>
  <div class="dashboard" v-loading="loading">
    <template v-if="isAdmin">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card total-books" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">图书总数</div>
                <div class="stat-value">{{ stats.total_books || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Reading /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card available-books" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">可借图书</div>
                <div class="stat-value">{{ stats.available_books || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Collection /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card total-readers" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">读者总数</div>
                <div class="stat-value">{{ stats.total_readers || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><User /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card borrowed-books" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">借出图书</div>
                <div class="stat-value">{{ stats.borrowed_count || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Notebook /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt20">
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card overdue-books clickable" shadow="hover" @click="goToBorrow">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">逾期数量</div>
                <div class="stat-value">{{ stats.overdue_count || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Warning /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card pending-renewal clickable" shadow="hover" @click="goToRenewals">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">待审核续借</div>
                <div class="stat-value">{{ stats.pending_renewal_count || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><RefreshRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card pending-fines clickable" shadow="hover" @click="goToFines">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">待缴罚金</div>
                <div class="stat-value">¥{{ (stats.unpaid_fine || 0).toFixed(2) }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Money /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="6" :lg="6">
          <el-card class="stat-card today-borrowed" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">今日借出</div>
                <div class="stat-value">{{ stats.today_borrowed || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Calendar /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt20">
        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card class="todo-card">
            <template #header>
              <div class="card-header">
                <el-icon><List /></el-icon>
                <span>待办事项</span>
              </div>
            </template>
            <div class="todo-section">
              <div class="todo-title">
                <el-tag type="warning" size="small">待审核续借</el-tag>
                <span class="todo-count">{{ pendingRenewals.length }} 条</span>
              </div>
              <div class="todo-list">
                <div v-if="pendingRenewals.length === 0" class="empty-todo">暂无待审核续借</div>
                <div v-for="item in pendingRenewals" :key="item.id" class="todo-item">
                  <div class="todo-info">
                    <span class="todo-reader">{{ item.reader_name }}</span>
                    <span class="todo-book">{{ item.book_title }}</span>
                  </div>
                  <el-tag size="small" type="warning">待审核</el-tag>
                </div>
              </div>
            </div>
            <el-divider />
            <div class="todo-section">
              <div class="todo-title">
                <el-tag type="primary" size="small">可借阅预约</el-tag>
                <span class="todo-count">{{ availableReservations.length }} 条</span>
              </div>
              <div class="todo-list">
                <div v-if="availableReservations.length === 0" class="empty-todo">暂无可用预约</div>
                <div v-for="item in availableReservations" :key="item.id" class="todo-item">
                  <div class="todo-info">
                    <span class="todo-reader">{{ item.reader_name }}</span>
                    <span class="todo-book">{{ item.book_title }}</span>
                  </div>
                  <el-tag size="small" type="success">可借阅</el-tag>
                </div>
              </div>
            </div>
            <el-divider />
            <div class="todo-section">
              <div class="todo-title">
                <el-tag type="success" size="small">新增读者</el-tag>
                <span class="todo-count">{{ newReaders.length }} 位</span>
              </div>
              <div class="todo-list">
                <div v-if="newReaders.length === 0" class="empty-todo">暂无新增读者</div>
                <div v-for="item in newReaders" :key="item.id" class="todo-item">
                  <div class="todo-info">
                    <span class="todo-reader">{{ item.first_name }}{{ item.last_name }}</span>
                    <span class="todo-book">{{ item.username }}</span>
                  </div>
                  <span class="todo-date">{{ formatDate(item.date_joined) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card class="mb20">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>最新借阅记录</span>
              </div>
            </template>
            <el-table :data="recentRecords" style="width: 100%" size="small">
              <el-table-column prop="reader_name" label="读者" width="100" />
              <el-table-column prop="book_title" label="图书" min-width="150" show-overflow-tooltip />
              <el-table-column prop="borrow_date" label="借阅日期" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.borrow_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><Warning /></el-icon>
                <span>逾期提醒</span>
              </div>
            </template>
            <el-alert
              v-if="stats.overdue_count > 0"
              :title="`有 ${stats.overdue_count} 本图书已逾期，请及时处理`"
              type="warning"
              show-icon
              :closable="false"
              class="mb10"
            />
            <el-table :data="overdueRecords" style="width: 100%" size="small">
              <el-table-column prop="reader_name" label="读者" width="100" />
              <el-table-column prop="book_title" label="图书" min-width="150" show-overflow-tooltip />
              <el-table-column prop="due_date" label="应还日期" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.due_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="fine_amount" label="罚款" width="80">
                <template #default="{ row }">
                  ¥{{ row.fine_amount || 0 }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row class="mt20">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><Operation /></el-icon>
                <span>快速操作</span>
              </div>
            </template>
            <div class="quick-actions">
              <el-button type="primary" size="large" @click="goToAddReader">
                <el-icon><UserFilled /></el-icon>
                新增读者
              </el-button>
              <el-button type="success" size="large" @click="goToAddBook">
                <el-icon><Reading /></el-icon>
                新增图书
              </el-button>
              <el-button type="warning" size="large" @click="goToBorrow">
                <el-icon><Notebook /></el-icon>
                借阅登记
              </el-button>
              <el-button type="info" size="large" @click="goToReturn">
                <el-icon><CircleCheckFilled /></el-icon>
                归还登记
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <template v-else>
      <el-row :gutter="20">
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-total" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">累计借阅</div>
                <div class="stat-value">{{ readerStats.total_borrowed || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Collection /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-current" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">当前借阅</div>
                <div class="stat-value">{{ readerStats.current_borrowed || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Reading /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-returned" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">已归还</div>
                <div class="stat-value">{{ readerStats.returned_count || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><CircleCheck /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt20">
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-overdue" shadow="hover">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">逾期次数</div>
                <div class="stat-value">{{ readerStats.overdue_count || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Warning /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-fines clickable" shadow="hover" @click="goToMyFines">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">待缴罚金</div>
                <div class="stat-value">¥{{ (readerStats.unpaid_fine || 0).toFixed(2) }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Money /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="12" :md="8" :lg="8">
          <el-card class="stat-card reader-reservations clickable" shadow="hover" @click="goToMyReservations">
            <div class="stat-content">
              <div class="stat-info">
                <div class="stat-label">有效预约</div>
                <div class="stat-value">{{ readerStats.active_reservations || 0 }}</div>
              </div>
              <div class="stat-icon">
                <el-icon :size="36"><Clock /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt20">
        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card class="mb20">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>我的当前借阅</span>
              </div>
            </template>
            <div v-if="myCurrentBorrow.length === 0" class="empty-state">
              <el-empty description="暂无借阅图书" />
            </div>
            <div v-else class="book-list">
              <div v-for="item in myCurrentBorrow" :key="item.id" class="book-item">
                <div class="book-cover">
                  <img v-if="item.book_cover" :src="item.book_cover" :alt="item.book_title" />
                  <div v-else class="cover-placeholder">
                    <el-icon :size="24"><Reading /></el-icon>
                  </div>
                </div>
                <div class="book-info">
                  <div class="book-title">{{ item.book_title }}</div>
                  <div class="book-meta">
                    <el-tag :type="getStatusType(item.status)" size="small">
                      {{ getStatusText(item.status) }}
                    </el-tag>
                    <span class="due-date">应还：{{ formatDate(item.due_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>我的预约</span>
              </div>
            </template>
            <div v-if="myReservations.length === 0" class="empty-state">
              <el-empty description="暂无预约记录" />
            </div>
            <div v-else class="reservation-list">
              <div v-for="item in myReservations" :key="item.id" class="reservation-item">
                <div class="reservation-info">
                  <div class="reservation-book">{{ item.book_title }}</div>
                  <div class="reservation-meta">
                    <span class="queue-position">排队位置：{{ item.queue_position || 1 }}</span>
                    <el-tag :type="getReservationStatusType(item.status)" size="small">
                      {{ getReservationStatusText(item.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12">
          <el-card v-if="myOverdue.length > 0" class="mb20">
            <template #header>
              <div class="card-header">
                <el-icon><WarningFilled /></el-icon>
                <span>逾期提醒</span>
              </div>
            </template>
            <el-alert
              :title="`您有 ${myOverdue.length} 本图书已逾期，请尽快归还`"
              type="error"
              show-icon
              :closable="false"
              class="mb10"
            />
            <div class="reminder-list">
              <div v-for="item in myOverdue" :key="item.id" class="reminder-item overdue">
                <div class="reminder-book">{{ item.book_title }}</div>
                <div class="reminder-info">
                  <span>应还日期：{{ formatDate(item.due_date) }}</span>
                  <span class="fine">罚款：¥{{ item.fine_amount || 0 }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <el-card v-if="mySoonDue.length > 0" class="mb20">
            <template #header>
              <div class="card-header">
                <el-icon><Bell /></el-icon>
                <span>待续借提醒</span>
              </div>
            </template>
            <el-alert
              :title="`您有 ${mySoonDue.length} 本图书将在7天内到期`"
              type="warning"
              show-icon
              :closable="false"
              class="mb10"
            />
            <div class="reminder-list">
              <div v-for="item in mySoonDue" :key="item.id" class="reminder-item soon">
                <div class="reminder-book">{{ item.book_title }}</div>
                <div class="reminder-info">
                  <span>应还日期：{{ formatDate(item.due_date) }}</span>
                  <span class="days-left">剩余 {{ getDaysLeft(item.due_date) }} 天</span>
                </div>
              </div>
            </div>
          </el-card>

          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><Star /></el-icon>
                <span>推荐图书</span>
              </div>
            </template>
            <div v-if="recommendedBooks.length === 0" class="empty-state">
              <el-empty description="暂无推荐图书" />
            </div>
            <div v-else class="recommend-list">
              <div v-for="book in recommendedBooks" :key="book.id" class="recommend-item">
                <div class="recommend-cover">
                  <img v-if="book.cover" :src="book.cover" :alt="book.title" />
                  <div v-else class="cover-placeholder small">
                    <el-icon :size="20"><Reading /></el-icon>
                  </div>
                </div>
                <div class="recommend-info">
                  <div class="recommend-title">{{ book.title }}</div>
                  <div class="recommend-meta">
                    <span>{{ book.author }}</span>
                    <el-tag v-if="book.can_borrow" type="success" size="small">可借</el-tag>
                    <el-tag v-else type="info" size="small">已借出</el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import {
  Reading, User, Notebook, Warning, Money, Calendar,
  RefreshRight, List, Document, Operation, UserFilled,
  CircleCheckFilled, Collection, CircleCheck, Clock,
  WarningFilled, Bell, Star
} from '@element-plus/icons-vue'

const router = useRouter()
const user = JSON.parse(localStorage.getItem('user') || '{}')
const isAdmin = computed(() => ['super_admin', 'admin'].includes(user.role))

const loading = ref(false)
const stats = ref({})
const readerStats = ref({})
const recentRecords = ref([])
const overdueRecords = ref([])
const pendingRenewals = ref([])
const availableReservations = ref([])
const newReaders = ref([])
const myCurrentBorrow = ref([])
const myReservations = ref([])
const myOverdue = ref([])
const mySoonDue = ref([])
const recommendedBooks = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'borrowed': 'primary',
    'returned': 'success',
    'overdue': 'danger',
    'lost': 'warning',
    'renewed': 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'borrowed': '借阅中',
    'returned': '已归还',
    'overdue': '已逾期',
    'lost': '已遗失',
    'renewed': '已续借'
  }
  return texts[status] || status
}

const getReservationStatusType = (status) => {
  const types = {
    'pending': 'warning',
    'available': 'success',
    'completed': 'info',
    'expired': 'danger'
  }
  return types[status] || 'info'
}

const getReservationStatusText = (status) => {
  const texts = {
    'pending': '等待中',
    'available': '可借阅',
    'completed': '已完成',
    'expired': '已过期'
  }
  return texts[status] || status
}

const getDaysLeft = (dueDate) => {
  if (!dueDate) return 0
  const now = new Date()
  const due = new Date(dueDate)
  const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
}

const goToBorrow = () => router.push('/borrow')
const goToRenewals = () => router.push('/renewals')
const goToFines = () => router.push('/fines')
const goToAddReader = () => router.push('/readers')
const goToAddBook = () => router.push('/books')
const goToReturn = () => router.push('/borrow')
const goToMyFines = () => router.push('/my-fines')
const goToMyReservations = () => router.push('/my-reservations')

const fetchStats = async () => {
  try {
    const res = await axios.get('/dashboard/stats/')
    if (isAdmin.value) {
      stats.value = res.data
    } else {
      readerStats.value = res.data
    }
  } catch (e) {
    console.error(e)
  }
}

const fetchRecentRecords = async () => {
  try {
    const res = await axios.get('/borrow-records/', { params: { page_size: 10 } })
    recentRecords.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchOverdueRecords = async () => {
  try {
    const res = await axios.get('/borrow-records/', { params: { status: 'overdue', page_size: 10 } })
    overdueRecords.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchPendingRenewals = async () => {
  try {
    const res = await axios.get('/renew-records/', { params: { status: 'pending', page_size: 5 } })
    pendingRenewals.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchAvailableReservations = async () => {
  try {
    const res = await axios.get('/reservations/', { params: { status: 'available', page_size: 5 } })
    availableReservations.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchNewReaders = async () => {
  try {
    const res = await axios.get('/users/', { params: { page_size: 5, ordering: '-date_joined' } })
    newReaders.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchMyBorrowRecords = async () => {
  try {
    const res = await axios.get('/borrow-records/my_borrows/', { params: { status: 'borrowed', page_size: 10 } })
    const records = res.data.results || res.data
    myCurrentBorrow.value = records.filter(r => r.status !== 'returned')
    myOverdue.value = records.filter(r => r.status === 'overdue')
    mySoonDue.value = records.filter(r => {
      if (r.status === 'overdue' || r.status === 'returned') return false
      return getDaysLeft(r.due_date) <= 7 && getDaysLeft(r.due_date) > 0
    })
  } catch (e) {
    console.error(e)
  }
}

const fetchMyReservations = async () => {
  try {
    const res = await axios.get('/reservations/my_reservations/', { params: { page_size: 10 } })
    myReservations.value = (res.data.results || res.data).filter(r => 
      ['pending', 'available'].includes(r.status)
    )
  } catch (e) {
    console.error(e)
  }
}

const fetchRecommendedBooks = async () => {
  try {
    const res = await axios.get('/books/', { params: { page_size: 6, ordering: '-borrow_count' } })
    recommendedBooks.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchAdminData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStats(),
      fetchRecentRecords(),
      fetchOverdueRecords(),
      fetchPendingRenewals(),
      fetchAvailableReservations(),
      fetchNewReaders()
    ])
  } finally {
    loading.value = false
  }
}

const fetchReaderData = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchStats(),
      fetchMyBorrowRecords(),
      fetchMyReservations(),
      fetchRecommendedBooks()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isAdmin.value) {
    fetchAdminData()
  } else {
    fetchReaderData()
  }
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
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info .stat-label {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-info .stat-value {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
}

.stat-icon {
  color: rgba(255, 255, 255, 0.3);
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

.overdue-books {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.pending-renewal {
  background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
}

.pending-fines {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}

.today-borrowed {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.reader-total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.reader-current {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.reader-returned {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.reader-overdue {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.reader-fines {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}

.reader-reservations {
  background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
}

.total-books :deep(.el-card__body),
.available-books :deep(.el-card__body),
.total-readers :deep(.el-card__body),
.borrowed-books :deep(.el-card__body),
.overdue-books :deep(.el-card__body),
.pending-renewal :deep(.el-card__body),
.pending-fines :deep(.el-card__body),
.today-borrowed :deep(.el-card__body),
.reader-total :deep(.el-card__body),
.reader-current :deep(.el-card__body),
.reader-returned :deep(.el-card__body),
.reader-overdue :deep(.el-card__body),
.reader-fines :deep(.el-card__body),
.reader-reservations :deep(.el-card__body) {
  background: transparent;
}

.mt20 {
  margin-top: 20px;
}

.mb20 {
  margin-bottom: 20px;
}

.mb10 {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
}

.todo-card .todo-section {
  margin-bottom: 0;
}

.todo-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.todo-count {
  font-size: 13px;
  color: #909399;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  transition: background 0.2s;
}

.todo-item:hover {
  background: #ecf5ff;
}

.todo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  overflow: hidden;
}

.todo-reader {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.todo-book {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.todo-date {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.empty-todo {
  text-align: center;
  color: #c0c4cc;
  padding: 12px;
  font-size: 13px;
}

.quick-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  padding: 20px 0;
}

.quick-actions .el-button {
  min-width: 160px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-list,
.reservation-list,
.reminder-list,
.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.book-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.book-item:hover {
  background: #ecf5ff;
}

.book-cover {
  width: 60px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.cover-placeholder.small {
  width: 50px;
  height: 70px;
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}

.book-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.due-date {
  font-size: 12px;
  color: #909399;
}

.reservation-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.reservation-item:hover {
  background: #ecf5ff;
}

.reservation-book {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.reservation-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.queue-position {
  font-size: 12px;
  color: #606266;
}

.reminder-item {
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid;
}

.reminder-item.overdue {
  background: #fef0f0;
  border-color: #f56c6c;
}

.reminder-item.soon {
  background: #fdf6ec;
  border-color: #e6a23c;
}

.reminder-book {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.reminder-info {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: #606266;
}

.fine {
  color: #f56c6c;
  font-weight: 500;
}

.days-left {
  color: #e6a23c;
  font-weight: 500;
}

.recommend-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.recommend-item:hover {
  background: #ecf5ff;
}

.recommend-cover {
  width: 50px;
  height: 70px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.recommend-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}

.recommend-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #606266;
}

.empty-state {
  padding: 20px 0;
}
</style>
