export default [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue'),
    meta: { title: '行情', requiresAuth: true }
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('@/views/Strategy.vue'),
    meta: { title: '策略', requiresAuth: true }
  },
  {
    path: '/order',
    name: 'Order',
    component: () => import('@/views/Order.vue'),
    meta: { title: '订单', requiresAuth: true }
  }
]
