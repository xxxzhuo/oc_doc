<template>
  <div class="projects-page">
    <div class="page-header">
      <h1>📋 项目列表</h1>
      <el-button type="primary" @click="showCreateDialog = true" v-if="userStore.isTenderer">
        <el-icon><Plus /></el-icon>
        创建项目
      </el-button>
    </div>
    
    <div class="filter-bar">
      <el-radio-group v-model="statusFilter" @change="loadProjects">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="active">投标中</el-radio-button>
        <el-radio-button value="closed">已截止</el-radio-button>
        <el-radio-button value="opened">已开标</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="project-list">
      <el-empty v-if="projects.length === 0" description="暂无项目" />
      
      <el-card v-for="project in projects" :key="project.id" class="project-card" shadow="hover">
        <div class="project-header">
          <h3 class="project-title">{{ project.title }}</h3>
          <el-tag :type="getStatusType(project.status)">{{ getStatusText(project.status) }}</el-tag>
        </div>
        
        <p class="project-description">{{ project.description || '暂无描述' }}</p>
        
        <div class="project-info">
          <div class="info-item">
            <el-icon><Clock /></el-icon>
            <span>截止：{{ formatDate(project.deadline) }}</span>
          </div>
          <div class="info-item">
            <el-icon><Document /></el-icon>
            <span>投标数：{{ project.bid_count }}</span>
          </div>
        </div>
        
        <div class="project-actions">
          <el-button type="primary" @click="viewProject(project.id)">查看详情</el-button>
          <el-button 
            v-if="userStore.isTenderer && project.status === 'closed'" 
            type="success"
            @click="openBids(project.id)"
          >
            开标
          </el-button>
        </div>
      </el-card>
    </div>
    
    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建竞标项目" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="产品参数" prop="params">
          <el-input
            v-model="paramsText"
            type="textarea"
            :rows="4"
            placeholder="JSON 格式，例如：&#123;&quot;规格&quot;: &quot;A4&quot;, &quot;数量&quot;: 1000&#125;"
          />
          <p class="form-tip">JSON 格式，例如：{"规格": "A4", "数量": 1000}</p>
        </el-form-item>
        
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="createForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const projects = ref([])
const statusFilter = ref('')
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const paramsText = ref('')

const createForm = reactive({
  title: '',
  description: '',
  params: {},
  deadline: ''
})

const createRules = {
  title: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  params: [{ required: true, message: '请输入产品参数', trigger: 'blur' }],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }]
}

const loadProjects = async () => {
  try {
    const params = statusFilter.value ? { status_filter: statusFilter.value } : {}
    const response = await axios.get('/api/projects', { params })
    projects.value = response.data
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

const viewProject = (id) => {
  router.push(`/projects/${id}`)
}

const openBids = async (id) => {
  try {
    await ElMessageBox.confirm('确认要开标吗？开标后将显示所有报价。', '开标确认', {
      type: 'warning'
    })
    
    await axios.post(`/api/projects/${id}/open`)
    ElMessage.success('开标成功')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '开标失败')
    }
  }
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 解析参数 JSON
    try {
      createForm.params = paramsText.value ? JSON.parse(paramsText.value) : {}
    } catch (e) {
      ElMessage.error('产品参数必须是有效的 JSON 格式')
      return
    }
    
    creating.value = true
    
    try {
      await axios.post('/api/projects', createForm)
      ElMessage.success('项目创建成功')
      showCreateDialog.value = false
      loadProjects()
      
      // 重置表单
      createForm.title = ''
      createForm.description = ''
      paramsText.value = ''
      createForm.deadline = ''
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '创建失败')
    } finally {
      creating.value = false
    }
  })
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

const disabledDate = (time) => {
  return time.getTime() < Date.now()
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped lang="scss">
.projects-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h1 {
    font-size: 24px;
    color: #333;
  }
}

.filter-bar {
  margin-bottom: 20px;
}

.project-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.project-card {
  .project-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .project-title {
    font-size: 18px;
    color: #333;
    margin: 0;
  }
  
  .project-description {
    color: #606266;
    margin-bottom: 15px;
    line-height: 1.6;
  }
  
  .project-info {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    color: #909399;
    font-size: 14px;
    
    .info-item {
      display: flex;
      align-items: center;
      gap: 5px;
    }
  }
  
  .project-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
