<template>
  <div class="home-page">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">🏆 暗标竞标系统</h1>
        <p class="hero-subtitle">安全 · 透明 · 公平</p>
        <p class="hero-description">
          专业的电子竞标平台，保护投标隐私，确保公平竞争
        </p>
        
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/login')">
            立即登录
          </el-button>
          <el-button size="large" @click="$router.push('/register')">
            免费注册
          </el-button>
        </div>
      </div>
      
      <div class="hero-features">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">🔐</div>
          <h3>安全加密</h3>
          <p>AES-256 加密保护报价数据</p>
        </el-card>
        
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">👁️</div>
          <h3>隐私保护</h3>
          <p>投标方互相看不到报价</p>
        </el-card>
        
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">⚖️</div>
          <h3>公平竞争</h3>
          <p>统一截止时间，公正开标</p>
        </el-card>
        
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">📊</div>
          <h3>透明结果</h3>
          <p>开标后自动排序，结果公示</p>
        </el-card>
      </div>
    </div>
    
    <div class="process-section">
      <h2 class="section-title">竞标流程</h2>
      
      <div class="process-steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3>创建项目</h3>
          <p>招标方发布竞标需求和产品参数</p>
        </div>
        
        <div class="step">
          <div class="step-number">2</div>
          <h3>提交投标</h3>
          <p>投标方加密提交报价和方案</p>
        </div>
        
        <div class="step">
          <div class="step-number">3</div>
          <h3>等待截止</h3>
          <p>所有投标保密存储直至截止</p>
        </div>
        
        <div class="step">
          <div class="step-number">4</div>
          <h3>公开开标</h3>
          <p>截止后解密报价，自动排序</p>
        </div>
      </div>
    </div>
    
    <div class="cta-section">
      <h2>准备好开始竞标了吗？</h2>
      <el-button type="primary" size="large" @click="$router.push('/register')">
        立即注册
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 已登录用户自动跳转到项目列表
if (userStore.isLoggedIn) {
  router.push('/projects')
}
</script>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero-section {
  padding: 80px 20px 60px;
  text-align: center;
  color: #fff;
  
  .hero-content {
    max-width: 800px;
    margin: 0 auto 60px;
  }
  
  .hero-title {
    font-size: 48px;
    margin-bottom: 15px;
    font-weight: bold;
  }
  
  .hero-subtitle {
    font-size: 24px;
    margin-bottom: 20px;
    opacity: 0.9;
  }
  
  .hero-description {
    font-size: 18px;
    margin-bottom: 40px;
    opacity: 0.8;
    line-height: 1.6;
  }
  
  .hero-actions {
    display: flex;
    gap: 20px;
    justify-content: center;
  }
}

.hero-features {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  
  :deep(.el-card__body) {
    padding: 30px 20px;
  }
  
  .feature-icon {
    font-size: 48px;
    margin-bottom: 15px;
  }
  
  h3 {
    font-size: 20px;
    color: #333;
    margin-bottom: 10px;
  }
  
  p {
    color: #606266;
    font-size: 14px;
  }
}

.process-section {
  background: #fff;
  padding: 80px 20px;
  
  .section-title {
    text-align: center;
    font-size: 32px;
    color: #333;
    margin-bottom: 60px;
  }
}

.process-steps {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 30px;
  
  .step {
    text-align: center;
    position: relative;
    
    .step-number {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      font-size: 24px;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
    }
    
    h3 {
      font-size: 18px;
      color: #333;
      margin-bottom: 10px;
    }
    
    p {
      color: #606266;
      font-size: 14px;
      line-height: 1.6;
    }
  }
}

.cta-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
  text-align: center;
  color: #fff;
  
  h2 {
    font-size: 32px;
    margin-bottom: 30px;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
