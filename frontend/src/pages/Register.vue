<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-box">
        <h1 class="title">🏆 用户注册</h1>
        <p class="subtitle">加入暗标竞标系统</p>
        
        <el-form :model="form" :rules="rules" ref="registerFormRef" class="register-form">
          <el-form-item prop="name">
            <el-input
              v-model="form.name"
              placeholder="姓名/公司名称"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>
          
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="邮箱"
              prefix-icon="Message"
              size="large"
            />
          </el-form-item>
          
          <el-form-item prop="company">
            <el-input
              v-model="form.company"
              placeholder="公司名称 (可选)"
              prefix-icon="OfficeBuilding"
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
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="role">
            <el-radio-group v-model="form.role" size="large">
              <el-radio-button value="tenderer">📋 招标方</el-radio-button>
              <el-radio-button value="bidder">💼 投标方</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleRegister"
              style="width: 100%"
            >
              注册
            </el-button>
          </el-form-item>
          
          <div class="links">
            <router-link to="/login">已有账号？立即登录</router-link>
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
import axios from 'axios'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  email: '',
  company: '',
  password: '',
  confirmPassword: '',
  role: 'bidder'
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      const { confirmPassword, ...registerData } = form
      const response = await axios.post('/api/auth/register', registerData)
      
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-container {
  width: 100%;
  max-width: 480px;
  padding: 20px;
}

.register-box {
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

.register-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  :deep(.el-radio-group) {
    width: 100%;
    display: flex;
    
    .el-radio-button {
      flex: 1;
    }
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
</style>
