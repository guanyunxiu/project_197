<template>
  <div class="my-stats-page" v-loading="loading">
    <el-card class="filter-card">
      <div class="filter-bar">
        <span class="filter-label">时间范围：</span>
        <el-select v-model="selectedDays" style="width: 150px;" @change="fetchData">
          <el-option :label="'近30天'" :value="30" />
          <el-option :label="'近90天'" :value="90" />
          <el-option :label="'近180天'" :value="180" />
        </el-select>
        <el-button type="primary" @click="fetchData" style="margin-left: 10px;">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>

    <el-row :gutter="20" class="mt20">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card total-borrowed">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">累计借阅</div>
              <div class="stat-value">{{ stats.total_borrowed || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card current-borrowed">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Collection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">当前借阅</div>
              <div class="stat-value">{{ stats.current_borrowed || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card total-returned">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">已归还</div>
              <div class="stat-value">{{ stats.total_returned || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card total-overdue">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">逾期次数</div>
              <div class="stat-value">{{ stats.total_overdue || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card total-fines">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">累计罚金</div>
              <div class="stat-value">¥{{ stats.total_fines || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card unpaid-fines">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Tickets /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">待缴罚金</div>
              <div class="stat-value">¥{{ stats.unpaid_fines || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card active-reservations">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">有效预约</div>
              <div class="stat-value">{{ stats.active_reservations || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="3">
        <el-card class="stat-card pending-renews">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">待审核续借</div>
              <div class="stat-value">{{ stats.pending_renews || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt20">
      <el-col :xs="24" :sm="24" :md="24" :lg="14" :xl="14">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">借阅历史趋势</span>
          </template>
          <VChart class="chart" :option="borrowHistoryOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="10" :xl="10">
        <el-card class="chart-card">
          <template #header>
            <span class="card-header">分类偏好</span>
          </template>
          <VChart class="chart" :option="categoryPreferenceOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Reading, Collection, CircleCheck, Warning, Money, Tickets, Clock, Timer } from '@element-plus/icons-vue'
import axios from 'axios'

const selectedDays = ref(90)
const loading = ref(false)
const stats = ref({})

const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b4bd']

const borrowHistoryOption = reactive({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e4e7ed',
    borderWidth: 1,
    textStyle: {
      color: '#303133'
    }
  },
  legend: {
    data: ['借阅数量'],
    bottom: 0,
    textStyle: {
      color: '#606266'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: [],
    axisLine: {
      lineStyle: {
        color: '#dcdfe6'
      }
    },
    axisLabel: {
      color: '#606266',
      rotate: 45,
      interval: 0
    }
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLine: {
      lineStyle: {
        color: '#dcdfe6'
      }
    },
    axisLabel: {
      color: '#606266'
    },
    splitLine: {
      lineStyle: {
        color: '#f2f6fc'
      }
    }
  },
  series: [
    {
      name: '借阅数量',
      type: 'line',
      smooth: true,
      data: [],
      itemStyle: {
        color: '#5470c6'
      },
      lineStyle: {
        width: 3
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(84, 112, 198, 0.4)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.05)' }
          ]
        }
      },
      symbol: 'circle',
      symbolSize: 8,
      emphasis: {
        focus: 'series',
        itemStyle: {
          borderWidth: 2,
          borderColor: '#fff'
        }
      }
    }
  ]
})

const categoryPreferenceOption = reactive({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e4e7ed',
    borderWidth: 1,
    textStyle: {
      color: '#303133'
    }
  },
  legend: {
    orient: 'vertical',
    right: '5%',
    top: 'center',
    textStyle: {
      color: '#606266'
    }
  },
  color: colors,
  series: [{
    type: 'pie',
    radius: ['45%', '75%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: true,
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: false,
      position: 'center'
    },
    emphasis: {
      label: {
        show: true,
        fontSize: 18,
        fontWeight: 'bold',
        color: '#303133'
      }
    },
    labelLine: {
      show: false
    },
    data: []
  }]
})

const updateBorrowHistory = (data) => {
  const history = data.borrow_history || []
  borrowHistoryOption.xAxis.data = history.map(item => item.date)
  borrowHistoryOption.series[0].data = history.map(item => item.count || 0)
}

const updateCategoryPreference = (data) => {
  const preference = data.category_preference || []
  categoryPreferenceOption.series[0].data = preference.map(item => ({
    value: item.count,
    name: item.book__category__name || item.name || '未分类'
  }))
}

const fetchData = async () => {
  try {
    loading.value = true
    const res = await axios.get('/stats/reader/', {
      params: { days: selectedDays.value }
    })
    stats.value = res.data
    updateBorrowHistory(res.data)
    updateCategoryPreference(res.data)
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
.my-stats-page {
  padding: 0;
}

.filter-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.filter-bar {
  display: flex;
  align-items: center;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
  font-weight: 500;
}

.stat-card {
  border: none;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.1);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.total-borrowed {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.current-borrowed {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.total-returned {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.total-overdue {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.total-fines {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.unpaid-fines {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.active-reservations {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
}

.pending-renews {
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon :deep(.el-icon) {
  font-size: 24px;
  color: #fff;
}

.stat-info .stat-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}

.stat-info .stat-value {
  color: #fff;
  font-size: 28px;
  font-weight: bold;
  line-height: 1.2;
}

.total-borrowed :deep(.el-card__body),
.current-borrowed :deep(.el-card__body),
.total-returned :deep(.el-card__body),
.total-overdue :deep(.el-card__body),
.total-fines :deep(.el-card__body),
.unpaid-fines :deep(.el-card__body),
.active-reservations :deep(.el-card__body),
.pending-renews :deep(.el-card__body) {
  background: transparent;
}

.chart-card {
  border-radius: 8px;
  height: 100%;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.chart {
  height: 380px;
  width: 100%;
}

.mt20 {
  margin-top: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.my-stats-page :deep(.el-card__body) {
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

  .stat-info .stat-value {
    font-size: 24px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-icon :deep(.el-icon) {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stat-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
  }

  .stat-icon :deep(.el-icon) {
    font-size: 18px;
  }
}
</style>
