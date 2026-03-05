<template>
  <el-header class="nav-bar">
    <div class="nav-content">
      <div class="nav-logo" @click="$router.push('/')">
        🏆 暗标竞标系统
      </div>
      
      <div class="nav-menu">
        <template v-if="userStore.isLoggedIn">
          <el-button text @click="$router.push('/projects')">
            <el-icon><Document /></el-icon>
            项目
          </el-button>
          <el-button text @click="$router.push('/dashboard')">
            <el-icon><DataAnalysis /></el-icon>
            工作台
          </el-button>
          
          <el-dropdown @command="handleCommand">
            <span class="user-name">
              <el-avatar :size="28">{{ userStore.userInfo?.name?.charAt(0) }}</el-avatar>
              {{ userStore.userInfo?.name }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <el-tag size="small" :type="userStore.isTenderer ? 'primary' : 'success'">
                    {{ userStore.isTenderer ? '招标方' : '投标方' }}
                  </el-tag>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        
        <template v-else>
          <el-button text @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const handleCommand = async (command) => {
  if (command === 'logout') {
    await ElMessageBox.confirm('确认要退出登录吗？', '退出确认', { type: 'warning' })
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  }
}
</script>

<style scoped lang="scss">
.nav-bar {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  
  .nav-content {
    max-width: 1200px;
    margin: 0 auto;
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
  }
  
  .nav-logo {
    font-size: 20px;
    font-weight: bold;
    color: #409EFF;
    cursor: pointer;
    user-select: none;
  }
  
  .nav-menu {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .user-name {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: #606266;
      
      &:hover {
        color: #409EFF;
      }
    }
  }
}
</style>
