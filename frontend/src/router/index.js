import { createRouter, createWebHistory } from 'vue-router'

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

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const authRequired = ['Projects', 'ProjectDetail', 'Dashboard']
  
  if (authRequired.includes(to.name) && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
