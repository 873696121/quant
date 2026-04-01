import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 量化交易系统`
  }

  // Auth guard
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }
  }

  // If already logged in and going to login, redirect to dashboard
  if (to.path === '/login') {
    const userStore = useUserStore()
    if (userStore.isLoggedIn) {
      next('/')
      return
    }
  }

  next()
})

export default router
