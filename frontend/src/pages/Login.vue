<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-box">
        <h1 class="title">🏆 暗标竞标系统</h1>
        <p class="subtitle">安全 · 透明 · 公平</p>
        
        <el-form :model="form" :rules="rules" ref="loginFormRef" class="login-form">
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="邮箱"
              prefix-icon="Message"
              size="large"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              style="width: 100%"
            >
              登录
            </el-button>
          </el-form-item>
          
          <div class="links">
            <router-link to="/register">还没有账号？立即注册</router-link>
          </div>
          
          <div class="demo-accounts">
            <p class="demo-title">💡 测试账号</p>
            <el-descriptions :column="1" size="small">
              <el-descriptions-item label="招标方">tenderer@example.com / password123</el-descriptions-item>
              <el-descriptions-item label="投标方">bidder1@example.com / password123</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

const form = reactive({
  email: '',
  password: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      const response = await axios.post('/api/auth/login', form)
      
      if (response.data.access_token) {
        userStore.setToken(response.data.access_token, response.data.user)
        ElMessage.success('登录成功')
        router.push('/projects')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.login-box {
  background: #fff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 30px;
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
}

.links {
  text-align: center;
  margin-top: 15px;
  
  a {
    color: #409EFF;
    text-decoration: none;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.demo-accounts {
  margin-top: 30px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 4px;
  
  .demo-title {
    font-size: 14px;
    color: #606266;
    margin-bottom: 10px;
  }
}
</style>
