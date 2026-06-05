<template>
  <div class="system-config-page" v-loading="loading">
    <el-card>
      <div class="page-header">
        <h2>系统配置</h2>
        <el-button type="primary" @click="goToOperationLogs">
          <el-icon><Operation /></el-icon>
          查看操作日志
        </el-button>
      </div>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>借阅配置</span>
              </div>
            </template>
            <el-table :data="borrowConfigs" style="width: 100%;">
              <el-table-column prop="config_key" label="配置项" min-width="140">
                <template #default="{ row }">
                  <span class="config-key">{{ getConfigLabel(row.config_key) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="config_value" label="配置值" width="120">
                <template #default="{ row }">
                  <el-tag type="primary" effect="plain">
                    {{ row.config_value }}
                    {{ getConfigUnit(row.config_key) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Money /></el-icon>
                <span>罚金配置</span>
              </div>
            </template>
            <el-table :data="fineConfigs" style="width: 100%;">
              <el-table-column prop="config_key" label="配置项" min-width="140">
                <template #default="{ row }">
                  <span class="config-key">{{ getConfigLabel(row.config_key) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="config_value" label="配置值" width="120">
                <template #default="{ row }">
                  <el-tag type="warning" effect="plain">
                    {{ row.config_value }}
                    {{ getConfigUnit(row.config_key) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>预约配置</span>
              </div>
            </template>
            <el-table :data="reservationConfigs" style="width: 100%;">
              <el-table-column prop="config_key" label="配置项" min-width="140">
                <template #default="{ row }">
                  <span class="config-key">{{ getConfigLabel(row.config_key) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="config_value" label="配置值" width="120">
                <template #default="{ row }">
                  <el-tag type="success" effect="plain">
                    {{ row.config_value }}
                    {{ getConfigUnit(row.config_key) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="80" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" type="primary" link @click="handleEdit(row)">编辑</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card class="config-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Collection /></el-icon>
                <span>图书状态</span>
              </div>
            </template>
            <div class="book-status-list">
              <div class="status-item" v-for="status in bookStatusList" :key="status.value">
                <el-tag :type="status.type" size="large" effect="light">
                  <el-icon style="margin-right: 5px;"><component :is="status.icon" /></el-icon>
                  {{ status.label }}
                </el-tag>
                <span class="status-desc">{{ status.description }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="dialogVisible" title="编辑配置" width="500px" :close-on-click-modal="false">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="140px">
        <el-form-item label="配置项">
          <span class="form-value">{{ getConfigLabel(configForm.config_key) }}</span>
        </el-form-item>
        <el-form-item label="配置分组">
          <span class="form-value">{{ getGroupLabel(configForm.config_group) }}</span>
        </el-form-item>
        <el-form-item label="说明">
          <span class="form-value">{{ configForm.description }}</span>
        </el-form-item>
        <el-form-item label="配置值" prop="config_value">
          <el-input-number
            v-if="isNumericConfig(configForm.config_key)"
            v-model="configForm.config_value"
            :min="getMinValue(configForm.config_key)"
            :max="getMaxValue(configForm.config_key)"
            :step="getStepValue(configForm.config_key)"
            style="width: 100%;"
          />
          <el-input v-else v-model="configForm.config_value" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Operation, Reading, Money, Clock, Collection, CircleCheck, Warning, Timer, SetUp, CircleClose } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isSuperAdmin = computed(() => user.role === 'super_admin')

const configs = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const configFormRef = ref()

const configForm = reactive({
  id: null,
  config_key: '',
  config_value: '',
  description: '',
  config_group: ''
})

const configRules = {
  config_value: [{ required: true, message: '请输入配置值', trigger: 'blur' }]
}

const borrowConfigs = computed(() => {
  return configs.value.filter(c => c.config_group === 'borrow')
})

const fineConfigs = computed(() => {
  return configs.value.filter(c => c.config_group === 'fine')
})

const reservationConfigs = computed(() => {
  return configs.value.filter(c => c.config_group === 'reservation')
})

const bookStatusList = [
  { value: 'available', label: '可借', type: 'success', icon: CircleCheck, description: '图书在馆，可被借阅' },
  { value: 'borrowed', label: '借出', type: 'warning', icon: Warning, description: '图书已被借出，不在馆中' },
  { value: 'reserved', label: '已预约', type: 'primary', icon: Timer, description: '图书已被读者预约' },
  { value: 'organizing', label: '整理中', type: 'info', icon: SetUp, description: '图书正在整理，暂不可借' },
  { value: 'lost', label: '已丢失', type: 'danger', icon: CircleClose, description: '图书已丢失，无法借阅' }
]

const configLabels = {
  'default_borrow_days': '默认借阅天数',
  'max_renew_times': '最大续借次数',
  'max_borrow_count': '单次最大借阅数',
  'daily_fine': '每日罚金',
  'max_fine_ratio': '最大罚金比例',
  'reservation_hold_days': '预约保留天数'
}

const configUnits = {
  'default_borrow_days': '天',
  'max_renew_times': '次',
  'max_borrow_count': '本',
  'daily_fine': '元',
  'max_fine_ratio': '%',
  'reservation_hold_days': '天'
}

const groupLabels = {
  'borrow': '借阅配置',
  'fine': '罚金配置',
  'reservation': '预约配置'
}

const numericConfigKeys = ['default_borrow_days', 'max_renew_times', 'max_borrow_count', 'daily_fine', 'max_fine_ratio', 'reservation_hold_days']

const getConfigLabel = (key) => configLabels[key] || key
const getConfigUnit = (key) => configUnits[key] || ''
const getGroupLabel = (group) => groupLabels[group] || group
const isNumericConfig = (key) => numericConfigKeys.includes(key)

const getMinValue = (key) => {
  const mins = {
    'default_borrow_days': 1,
    'max_renew_times': 0,
    'max_borrow_count': 1,
    'daily_fine': 0,
    'max_fine_ratio': 0,
    'reservation_hold_days': 1
  }
  return mins[key] || 0
}

const getMaxValue = (key) => {
  const maxes = {
    'default_borrow_days': 365,
    'max_renew_times': 10,
    'max_borrow_count': 50,
    'daily_fine': 100,
    'max_fine_ratio': 500,
    'reservation_hold_days': 30
  }
  return maxes[key] || 9999
}

const getStepValue = (key) => {
  return key === 'daily_fine' ? 0.1 : 1
}

const fetchConfigs = async () => {
  try {
    loading.value = true
    const res = await axios.get('/api/system-configs/')
    configs.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取系统配置失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleEdit = (row) => {
  Object.assign(configForm, { ...row })
  if (isNumericConfig(row.config_key)) {
    configForm.config_value = Number(row.config_value)
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await configFormRef.validate()
    submitting.value = true
    await axios.put(`/api/system-configs/${configForm.id}/`, configForm)
    ElMessage.success('配置更新成功')
    dialogVisible.value = false
    fetchConfigs()
  } catch (e) {
    if (e !== false) {
      const errors = e.response?.data
      if (errors) {
        const firstError = Object.values(errors)[0]
        ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
      } else {
        ElMessage.error('更新失败')
      }
    }
  } finally {
    submitting.value = false
  }
}

const goToOperationLogs = () => {
  router.push('/operation-logs')
}

onMounted(() => {
  if (!isSuperAdmin.value) {
    ElMessage.error('只有超级管理员可以访问此页面')
    router.push('/dashboard')
    return
  }
  fetchConfigs()
})
</script>

<style scoped>
.system-config-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.config-key {
  font-weight: 500;
}

.form-value {
  color: #606266;
}

.book-status-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-desc {
  color: #909399;
  font-size: 14px;
}

.config-card :deep(.el-table .el-table__cell) {
  padding: 10px 0;
}
</style>
