<template>
  <div class="project-detail-page">
    <div class="back-nav">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>
    
    <el-card v-if="project" class="project-card">
      <template #header>
        <div class="card-header">
          <h1>{{ project.title }}</h1>
          <el-tag :type="getStatusType(project.status)" size="large">
            {{ getStatusText(project.status) }}
          </el-tag>
        </div>
      </template>
      
      <div class="project-content">
        <div class="section">
          <h3>📝 项目描述</h3>
          <p>{{ project.description || '暂无描述' }}</p>
        </div>
        
        <div class="section">
          <h3>⚙️ 产品参数</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="(value, key) in project.params"
              :key="key"
              :label="key"
            >
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="section">
          <h3>📅 时间信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="创建时间">
              {{ formatDate(project.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="截止时间">
              <span :class="{ 'deadline-warning': isDeadlineSoon }">
                {{ formatDate(project.deadline) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="投标数量">
              {{ project.bid_count }}
            </el-descriptions-item>
            <el-descriptions-item label="当前状态">
              {{ getStatusText(project.status) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
    
    <!-- 投标表单 (仅投标方，投标中状态) -->
    <el-card v-if="canBid" class="bid-card">
      <template #header>
        <h2>💼 提交投标</h2>
      </template>
      
      <el-form :model="bidForm" :rules="bidRules" ref="bidFormRef" label-width="100px">
        <el-form-item label="报价" prop="price">
          <el-input-number
            v-model="bidForm.price"
            :min="0"
            :precision="2"
            :step="100"
            placeholder="请输入报价"
            style="width: 100%"
          />
          <p class="form-tip">💰 报价将被加密存储，其他投标方无法查看</p>
        </el-form-item>
        
        <el-form-item label="投标参数" prop="params">
          <el-input
            v-model="paramsText"
            type="textarea"
            :rows="4"
            placeholder="JSON 格式，例如：&#123;&quot;交货期&quot;: &quot;7 天&quot;, &quot;质保&quot;: &quot;1 年&quot;&#125;"
          />
          <p class="form-tip">JSON 格式，例如：{"交货期": "7 天", "质保": "1 年"}</p>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleBid" :loading="submitting">
            提交投标
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 投标列表 -->
    <el-card v-if="canViewBids" class="bids-card">
      <template #header>
        <h2>📊 投标列表</h2>
      </template>
      
      <el-table :data="bids" style="width: 100%">
        <el-table-column prop="bidder_name" label="投标方" />
        <el-table-column prop="bidder_company" label="公司" />
        <el-table-column label="报价" v-if="showPrice">
          <template #default="{ row }">
            <span class="price-text">¥ {{ row.price?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag type="success">已提交</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="bids.length === 0" description="暂无投标" />
    </el-card>
    
    <!-- 开标结果 (仅招标方，已开标状态) -->
    <el-card v-if="showResults" class="results-card">
      <template #header>
        <h2>🏆 开标结果</h2>
      </template>
      
      <el-table :data="bidDetails" style="width: 100%" :default-sort="{ prop: 'price', order: 'ascending' }">
        <el-table-column prop="bidder_name" label="投标方" />
        <el-table-column prop="bidder_company" label="公司" />
        <el-table-column prop="price" label="报价" sortable>
          <template #default="{ row }">
            <span class="price-text">¥ {{ row.price?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="排名">
          <template #default="{ row, $index }">
            <el-tag :type="getRankType($index)">
              {{ $index + 1 }}{{ getRankSuffix($index + 1) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import dayjs from 'dayjs'

const route = useRoute()
const userStore = useUserStore()

const project = ref(null)
const bids = ref([])
const bidDetails = ref([])
const bidFormRef = ref(null)
const paramsText = ref('')
const submitting = ref(false)

const bidForm = reactive({
  price: null,
  params: {}
})

const bidRules = {
  price: [
    { required: true, message: '请输入报价', trigger: 'blur' },
    { type: 'number', message: '报价必须是数字', trigger: 'blur' }
  ]
}

const canBid = computed(() => {
  return userStore.isBidder && 
         project.value && 
         project.value.status === 'active'
})

const canViewBids = computed(() => {
  return project.value && 
         (userStore.isTenderer || project.value.status === 'opened')
})

const showPrice = computed(() => {
  return userStore.isTenderer && project.value?.status === 'opened'
})

const showResults = computed(() => {
  return userStore.isTenderer && project.value?.status === 'opened'
})

const isDeadlineSoon = computed(() => {
  if (!project.value?.deadline) return false
  const now = dayjs()
  const deadline = dayjs(project.value.deadline)
  const hoursLeft = deadline.diff(now, 'hour')
  return hoursLeft > 0 && hoursLeft <= 24
})

const loadProject = async () => {
  try {
    const response = await axios.get(`/api/projects/${route.params.id}`)
    project.value = response.data
  } catch (error) {
    ElMessage.error('加载项目详情失败')
  }
}

const loadBids = async () => {
  try {
    const endpoint = showPrice.value 
      ? `/api/projects/${route.params.id}/bids/detail`
      : `/api/projects/${route.params.id}/bids`
    
    const response = await axios.get(endpoint)
    
    if (showPrice.value) {
      bidDetails.value = response.data
    } else {
      bids.value = response.data
    }
  } catch (error) {
    console.error('加载投标列表失败:', error)
  }
}

const handleBid = async () => {
  if (!bidFormRef.value) return
  
  await bidFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 解析参数 JSON
    try {
      bidForm.params = paramsText.value ? JSON.parse(paramsText.value) : {}
    } catch (e) {
      ElMessage.error('投标参数必须是有效的 JSON 格式')
      return
    }
    
    submitting.value = true
    
    try {
      await axios.post(`/api/projects/${route.params.id}/bids`, bidForm)
      ElMessage.success('投标提交成功')
      
      // 重置表单
      bidForm.price = null
      paramsText.value = ''
      
      // 刷新数据
      loadProject()
      loadBids()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '投标失败')
    } finally {
      submitting.value = false
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

const getRankType = (index) => {
  const types = ['warning', 'info', 'success']
  return types[index] || ''
}

const getRankSuffix = (rank) => {
  const suffixes = ['名', '名', '名', '名']
  return suffixes[rank - 1] || '名'
}

onMounted(() => {
  loadProject()
  loadBids()
})
</script>

<style scoped lang="scss">
.project-detail-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.back-nav {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h1 {
    font-size: 24px;
    margin: 0;
  }
}

.project-content {
  .section {
    margin-bottom: 30px;
    
    h3 {
      font-size: 16px;
      color: #333;
      margin-bottom: 15px;
    }
    
    p {
      color: #606266;
      line-height: 1.8;
    }
  }
}

.bid-card, .bids-card, .results-card {
  margin-top: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.deadline-warning {
  color: #F56C6C;
  font-weight: bold;
}

.price-text {
  font-weight: bold;
  color: #F56C6C;
  font-size: 15px;
}
</style>
