import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/pages/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue')
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/pages/Projects.vue')
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/pages/ProjectDetail.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 解码 JWT token 检查是否过期
const isTokenExpired = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp
    if (!exp) return true
    return Date.now() >= exp * 1000
  } catch (e) {
    return true
  }
}

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const authRequired = ['Projects', 'ProjectDetail', 'Dashboard']
  
  if (authRequired.includes(to.name)) {
    if (!userStore.token) {
      next('/login')
      return
    }
    
    // 检查 token 是否过期
    if (isTokenExpired(userStore.token)) {
      userStore.logout()
      next('/login')
      return
    }
  }
  
  next()
})

export default router
