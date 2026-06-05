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
    meta: { requiresAuth: true, roles: ['admin'] }
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
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/readers',
    name: 'Readers',
    component: () => import('../views/Readers.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/borrow',
    name: 'Borrow',
    component: () => import('../views/Borrow.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
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
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
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
    if (user.role === 'admin') {
      next('/dashboard')
    } else {
      next('/books')
    }
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    if (user.role === 'admin') {
      next('/dashboard')
    } else {
      next('/books')
    }
  } else {
    next()
  }
})

export default router
