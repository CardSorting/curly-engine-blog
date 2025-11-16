import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'

// Lazy-loaded components
const LoginView = () => import('@/views/auth/LoginView.vue')
const RegisterView = () => import('@/views/auth/RegisterView.vue')
const AccountSelectView = () => import('@/views/auth/AccountSelectView.vue')
const AccountCreateView = () => import('@/views/auth/AccountCreateView.vue')

const BlogHomeView = () => import('@/views/blog/BlogHomeView.vue')
const ArticleDetailView = () => import('@/views/blog/ArticleDetailView.vue')
const TopicArticlesView = () => import('@/views/blog/TopicArticlesView.vue')
const PageView = () => import('@/views/blog/PageView.vue')
const SearchView = () => import('@/views/blog/SearchView.vue')

const AdminDashboard = () => import('@/views/admin/AdminDashboard.vue')
const ArticleListView = () => import('@/views/admin/ArticleListView.vue')
const ArticleCreateView = () => import('@/views/admin/ArticleCreateView.vue')
const ArticleEditView = () => import('@/views/admin/ArticleEditView.vue')
const MediaManagerView = () => import('@/views/admin/MediaManagerView.vue')
const UserManagementView = () => import('@/views/admin/UserManagementView.vue')
const SettingsView = () => import('@/views/admin/SettingsView.vue')

// Route guards
const requireAuth = (to: any, from: any, next: any) => {
  const authStore = useAuthStore()

  if (!authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
}

const requireTenant = (to: any, from: any, next: any) => {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()

  if (!authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (!tenantStore.currentAccount) {
    next({ name: 'account-select' })
    return
  }

  next()
}

const checkAccountFromRoute = (to: any, from: any, next: any) => {
  const tenantStore = useTenantStore()
  const accountSlug = to.params.accountSlug as string

  if (accountSlug && tenantStore.currentAccount?.slug !== accountSlug) {
    // Try to switch to this account if user has access
    const availableAccount = tenantStore.userAccounts.find(acc => acc.slug === accountSlug)
    if (availableAccount) {
      tenantStore.setCurrentAccount(availableAccount)
    }
  }

  next()
}

const routes: RouteRecordRaw[] = [
  // Authentication routes
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/account-select',
    name: 'account-select',
    component: AccountSelectView,
    meta: { requiresAuth: true, layout: 'auth' },
    beforeEnter: requireAuth
  },
  {
    path: '/account-create',
    name: 'account-create',
    component: AccountCreateView,
    meta: { requiresAuth: true, layout: 'auth' },
    beforeEnter: requireAuth
  },

  // Public blog routes
  {
    path: '/',
    name: 'blog-home',
    component: BlogHomeView,
    meta: { layout: 'blog', seo: { title: 'Home' } }
  },
  {
    path: '/:accountSlug/:articleSlug',
    name: 'article-detail',
    component: ArticleDetailView,
    meta: { layout: 'blog' }
  },
  {
    path: '/:accountSlug/topics/:topicSlug',
    name: 'topic-articles',
    component: TopicArticlesView,
    meta: { layout: 'blog' }
  },
  {
    path: '/:accountSlug/:pageSlug',
    name: 'page',
    component: PageView,
    meta: { layout: 'blog' }
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView,
    meta: { layout: 'blog' }
  },

  // Admin routes (tenant-aware)
  {
    path: '/:accountSlug/admin',
    name: 'admin-dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/articles',
    name: 'admin-articles',
    component: ArticleListView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/articles/create',
    name: 'admin-article-create',
    component: ArticleCreateView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/articles/:articleId/edit',
    name: 'admin-article-edit',
    component: ArticleEditView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/media',
    name: 'admin-media',
    component: MediaManagerView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/users',
    name: 'admin-users',
    component: UserManagementView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },
  {
    path: '/:accountSlug/admin/settings',
    name: 'admin-settings',
    component: SettingsView,
    meta: { requiresAuth: true, requiresTenant: true, layout: 'admin' },
    beforeEnter: [requireAuth, requireTenant, checkAccountFromRoute]
  },

  // Legacy redirects (for backward compatibility)
  {
    path: '/admin',
    redirect: (to) => {
      const tenantStore = useTenantStore()
      if (tenantStore.currentAccount) {
        return { name: 'admin-dashboard' }
      }
      return { name: 'account-select' }
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Set page meta information
  if (to.meta.title) {
    document.title = `${to.meta.title} | ${import.meta.env.VITE_APP_NAME || 'Chronicle'}`
  }

  // Handle authentication requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Prevent authenticated users from accessing auth pages
  if (!to.meta.requiresAuth && authStore.isAuthenticated && to.name === 'login') {
    next({ name: 'blog-home' })
    return
  }

  next()
})

export default router
