import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import * as echarts from 'echarts'
import VChart from 'vue-echarts'

const app = createApp(App)

axios.defaults.baseURL = '/api'
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

app.config.globalProperties.$axios = axios
app.config.globalProperties.$echarts = echarts

app.component('VChart', VChart)

app.use(ElementPlus)
app.use(router)
app.mount('#app')
