<template>
  <div class="dashboard-page">
    <div class="dashboard-header">
      <h1>📊 工作台</h1>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="user-name">
            <el-avatar :size="32">{{ userStore.userInfo?.name?.charAt(0) }}</el-avatar>
            {{ userStore.userInfo?.name }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #409EFF">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalProjects }}</div>
          <div class="stat-label">总项目数</div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #67C23A">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.activeProjects }}</div>
          <div class="stat-label">投标中</div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #E6A23C">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.myBids }}</div>
          <div class="stat-label">我的投标</div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-icon" style="background: #F56C6C">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.wonBids }}</div>
          <div class="stat-label">中标次数</div>
        </div>
      </el-card>
    </div>
    
    <div class="content-grid">
      <el-card class="projects-card">
        <template #header>
          <div class="card-header">
            <h3>📋 最近项目</h3>
            <el-button text @click="$router.push('/projects')">查看全部</el-button>
          </div>
        </template>
        
        <el-table :data="recentProjects" style="width: 100%">
          <el-table-column prop="title" label="项目名称" />
          <el-table-column label="状态">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deadline" label="截止时间">
            <template #default="{ row }">
              {{ formatDate(row.deadline) }}
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{ row }">
              <el-button text type="primary" @click="$router.push(`/projects/${row.id}`)">
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-if="recentProjects.length === 0" description="暂无项目" />
      </el-card>
      
      <el-card class="notifications-card">
        <template #header>
          <h3>🔔 系统通知</h3>
        </template>
        
        <el-timeline>
          <el-timeline-item
            v-for="note in notifications"
            :key="note.id"
            :timestamp="note.time"
            placement="top"
            :type="note.type"
          >
            <p>{{ note.content }}</p>
          </el-timeline-item>
        </el-timeline>
        
        <el-empty v-if="notifications.length === 0" description="暂无通知" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  totalProjects: 0,
  activeProjects: 0,
  myBids: 0,
  wonBids: 0
})

const recentProjects = ref([])
const notifications = ref([
  { id: 1, content: '欢迎使用暗标竞标系统', time: '刚刚', type: 'primary' },
  { id: 2, content: '完善个人信息以获得更好的体验', time: '系统提示', type: 'warning' }
])

const loadStats = async () => {
  try {
    const response = await axios.get('/api/projects')
    const projects = response.data
    
    stats.value.totalProjects = projects.length
    stats.value.activeProjects = projects.filter(p => p.status === 'active').length
    
    // 这里可以调用更多 API 获取详细统计
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentProjects = async () => {
  try {
    const response = await axios.get('/api/projects')
    recentProjects.value = response.data.slice(0, 5)
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    await ElMessageBox.confirm('确认要退出登录吗？', '退出确认', {
      type: 'warning'
    })
    
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中')
  }
}

const getStatusType = (status) => {
  const types = {
    draft: 'info',
    active: 'primary',
    closed: 'warning',
    opened: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    draft: '草稿',
    active: '投标中',
    closed: '已截止',
    opened: '已开标'
  }
  return texts[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadStats()
  loadRecentProjects()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  
  h1 {
    font-size: 28px;
    color: #333;
  }
  
  .user-info {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  
  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    width: 100%;
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .el-icon {
      font-size: 32px;
      color: #fff;
    }
  }
  
  .stat-content {
    flex: 1;
    
    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #333;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 5px;
    }
  }
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    font-size: 16px;
    color: #333;
  }
}

.notifications-card {
  :deep(.el-timeline-item__content) {
    p {
      margin: 0;
      color: #606266;
    }
  }
}
</style>
