import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard',
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/Statistics.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/operation-logs',
    name: 'OperationLogs',
    component: () => import('../views/OperationLogs.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/books',
    name: 'Books',
    component: () => import('../views/Books.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/readers',
    name: 'Readers',
    component: () => import('../views/Readers.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/borrow',
    name: 'Borrow',
    component: () => import('../views/Borrow.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/fines',
    name: 'Fines',
    component: () => import('../views/Fines.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/renewals',
    name: 'Renewals',
    component: () => import('../views/Renewals.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/reservations-admin',
    name: 'ReservationsAdmin',
    component: () => import('../views/ReservationsAdmin.vue'),
    meta: { requiresAuth: true, roles: ['super_admin', 'admin'] }
  },
  {
    path: '/my-borrow',
    name: 'MyBorrow',
    component: () => import('../views/MyBorrow.vue'),
    meta: { requiresAuth: true, roles: ['reader'] }
  },
  {
    path: '/my-history',
    name: 'MyHistory',
    component: () => import('../views/MyHistory.vue'),
    meta: { requiresAuth: true, roles: ['reader'] }
  },
  {
    path: '/my-reservations',
    name: 'MyReservations',
    component: () => import('../views/MyReservations.vue'),
    meta: { requiresAuth: true, roles: ['reader'] }
  },
  {
    path: '/my-fines',
    name: 'MyFines',
    component: () => import('../views/MyFines.vue'),
    meta: { requiresAuth: true, roles: ['reader'] }
  },
  {
    path: '/my-stats',
    name: 'MyStats',
    component: () => import('../views/MyStats.vue'),
    meta: { requiresAuth: true, roles: ['reader'] }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/system-config',
    name: 'SystemConfig',
    component: () => import('../views/SystemConfig.vue'),
    meta: { requiresAuth: true, roles: ['super_admin'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(user.role)) {
    next('/dashboard')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
