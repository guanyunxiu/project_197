<template>
  <div class="statistics-page" v-loading="loading">
    <el-card class="filter-card">
      <div class="filter-bar">
        <span class="filter-label">时间范围：</span>
        <el-select v-model="selectedDays" style="width: 150px;" @change="fetchData">
          <el-option :label="'近7天'" :value="7" />
          <el-option :label="'近30天'" :value="30" />
          <el-option :label="'近90天'" :value="90" />
        </el-select>
        <el-button type="primary" @click="fetchData" style="margin-left: 10px;">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="20" class="mt20">
      <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">借阅趋势</span>
          </template>
          <VChart class="chart" :option="borrowTrendOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="6" :xl="6">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">图书分类占比</span>
          </template>
          <VChart class="chart" :option="bookCategoryOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="6" :xl="6">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">借阅分类占比</span>
          </template>
          <VChart class="chart" :option="borrowCategoryOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt20">
      <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">热门图书 TOP10</span>
          </template>
          <VChart class="chart" :option="hotBooksOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">读者借阅排行 TOP10</span>
          </template>
          <VChart class="chart" :option="readerRankOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">逾期趋势</span>
          </template>
          <VChart class="chart" :option="overdueTrendOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import axios from 'axios'

const selectedDays = ref(30)
const loading = ref(false)
const statsData = ref({})

const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b4bd']

const borrowTrendOption = reactive({
  tooltip: { trigger: 'axis' },
  legend: { data: ['借阅数量', '归还数量'], bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '借阅数量',
      type: 'line',
      smooth: true,
      data: [],
      itemStyle: { color: '#5470c6' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.05)' }
          ]
        }
      }
    },
    {
      name: '归还数量',
      type: 'line',
      smooth: true,
      data: [],
      itemStyle: { color: '#91cc75' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(145, 204, 117, 0.3)' },
            { offset: 1, color: 'rgba(145, 204, 117, 0.05)' }
          ]
        }
      }
    }
  ]
})

const bookCategoryOption = reactive({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', right: '5%', top: 'center' },
  color: colors,
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: {
      label: { show: true, fontSize: 16, fontWeight: 'bold' }
    },
    labelLine: { show: false },
    data: []
  }]
})

const borrowCategoryOption = reactive({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', right: '5%', top: 'center' },
  color: colors,
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: {
      label: { show: true, fontSize: 16, fontWeight: 'bold' }
    },
    labelLine: { show: false },
    data: []
  }]
})

const hotBooksOption = reactive({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: [],
    axisLabel: { interval: 0, width: 120, overflow: 'truncate' }
  },
  series: [{
    type: 'bar',
    data: [],
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]
      },
      borderRadius: [0, 4, 4, 0]
    }
  }]
})

const readerRankOption = reactive({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', top: '3%', containLabel: true },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: [],
    axisLabel: { interval: 0, width: 100, overflow: 'truncate' }
  },
  series: [{
    type: 'bar',
    data: [],
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: '#f093fb' },
          { offset: 1, color: '#f5576c' }
        ]
      },
      borderRadius: [0, 4, 4, 0]
    }
  }]
})

const overdueTrendOption = reactive({
  tooltip: { trigger: 'axis' },
  legend: { data: ['逾期数量', '新增逾期'], bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: { type: 'value' },
  series: [
    {
      name: '逾期数量',
      type: 'line',
      smooth: true,
      data: [],
      itemStyle: { color: '#ee6666' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(238, 102, 102, 0.3)' },
            { offset: 1, color: 'rgba(238, 102, 102, 0.05)' }
          ]
        }
      }
    },
    {
      name: '新增逾期',
      type: 'line',
      smooth: true,
      data: [],
      itemStyle: { color: '#fac858' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(250, 200, 88, 0.3)' },
            { offset: 1, color: 'rgba(250, 200, 88, 0.05)' }
          ]
        }
      }
    }
  ]
})

const updateBorrowTrend = (data) => {
  const trend = data.borrow_trend || []
  borrowTrendOption.xAxis.data = trend.map(item => item.date)
  borrowTrendOption.series[0].data = trend.map(item => item.borrow_count || 0)
  borrowTrendOption.series[1].data = trend.map(item => item.return_count || 0)
}

const updateBookCategory = (data) => {
  const category = data.book_categories || []
  bookCategoryOption.series[0].data = category.map(item => ({
    value: item.count,
    name: item.name
  }))
}

const updateBorrowCategory = (data) => {
  const category = data.borrow_categories || []
  borrowCategoryOption.series[0].data = category.map(item => ({
    value: item.count,
    name: item.name
  }))
}

const updateHotBooks = (data) => {
  const books = data.hot_books || []
  hotBooksOption.yAxis.data = books.map(item => item.title).reverse()
  hotBooksOption.series[0].data = books.map(item => item.borrow_count).reverse()
}

const updateReaderRank = (data) => {
  const readers = data.reader_rank || []
  readerRankOption.yAxis.data = readers.map(item => item.reader_name).reverse()
  readerRankOption.series[0].data = readers.map(item => item.borrow_count).reverse()
}

const updateOverdueTrend = (data) => {
  const trend = data.overdue_trend || []
  overdueTrendOption.xAxis.data = trend.map(item => item.date)
  overdueTrendOption.series[0].data = trend.map(item => item.overdue_count || 0)
  overdueTrendOption.series[1].data = trend.map(item => item.new_overdue || 0)
}

const fetchData = async () => {
  try {
    loading.value = true
    const res = await axios.get('/stats/borrow/', {
      params: { days: selectedDays.value }
    })
    statsData.value = res.data
    updateBorrowTrend(res.data)
    updateBookCategory(res.data)
    updateBorrowCategory(res.data)
    updateHotBooks(res.data)
    updateReaderRank(res.data)
    updateOverdueTrend(res.data)
  } catch (e) {
    ElMessage.error('获取统计数据失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.statistics-page {
  padding: 0;
}

.filter-card {
  border-radius: 8px;
}

.filter-bar {
  display: flex;
  align-items: center;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.chart-card {
  border-radius: 8px;
  height: 100%;
}

.chart {
  height: 350px;
  width: 100%;
}

.mt20 {
  margin-top: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.statistics-page :deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 768px) {
  .chart {
    height: 280px;
  }

  .filter-bar {
    flex-wrap: wrap;
    gap: 10px;
  }
}
</style>
