import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/stores/user'

// 创建 axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000
})

// 请求拦截器 - 自动添加 token
service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理错误
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 401: 未授权，token 过期或无效
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      
      ElMessage.error('登录已过期，请重新登录')
      
      // 如果不在登录页，跳转到登录页
      if (router.currentRoute.value.name !== 'Login') {
        router.push('/login')
      }
    }
    // 403: 禁止访问
    else if (error.response?.status === 403) {
      ElMessage.error(error.response?.data?.detail || '无权限访问')
    }
    // 404: 资源不存在
    else if (error.response?.status === 404) {
      ElMessage.error(error.response?.data?.detail || '资源不存在')
    }
    // 500: 服务器错误
    else if (error.response?.status === 500) {
      ElMessage.error('服务器错误，请稍后重试')
    }
    // 其他错误
    else {
      ElMessage.error(error.response?.data?.detail || error.message || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default service
