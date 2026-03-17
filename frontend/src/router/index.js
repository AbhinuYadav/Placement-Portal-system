// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Auth views
import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import HomeView from '@/views/HomeView.vue'

// Admin Layout
import AdminLayout from '@/layouts/AdminLayout.vue'
import CompanyLayout from '@/layouts/CompanyLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true }
    },
    // Admin routes
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue')
        },
        {
          path: 'companies',
          name: 'admin-companies',
          component: () => import('@/views/admin/CompaniesView.vue')
        },
        {
          path: 'drives',
          name: 'admin-drives',
          component: () => import('@/views/admin/DrivesView.vue')
        },
        {
          path: 'students',
          name: 'admin-students',
          component: () => import('@/views/admin/StudentsView.vue')
        },
        {
         path: 'companies/:id',
         name: 'admin-company-detail',
         component: () => import('@/views/admin/CompanyDetailView.vue')
        },
        {
         path: 'drives/:id',
         name: 'admin-drive-detail',
         component: () => import('@/views/admin/DriveDetailView.vue')
        },
        {
         path: 'students/:id',
         name: 'admin-student-detail',
         component: () => import('@/views/admin/StudentDetailView.vue')
        },
        {
         path: 'applications',
         name: 'admin-applications',
         component: () => import('@/views/admin/ApplicationsView.vue')
        }
      ]
    },

    // Company Routes
    {
      path: '/company',
      component: CompanyLayout,
      meta: { requiresAuth: true, role: 'company' },
      children: [
        {
          path: 'dashboard',
          name: 'company-dashboard',
          component: () => import('@/views/company/DashboardView.vue')
        },
        {
          path: 'profile',
          name: 'company-profile',
          component: () => import('@/views/company/ProfileView.vue')
        },
        {
          path: 'drives',
          name: 'company-drives',
          component: () => import('@/views/company/DrivesView.vue')
        },
        {
          path: 'drives/create',
          name: 'company-drive-create',
          component: () => import('@/views/company/CreateDriveView.vue')
        },
        {
          path: 'drives/:id',
          name: 'company-drive-detail',
          component: () => import('@/views/company/DriveDetailView.vue')
        },
        {
          path: 'applications',
          name: 'company-applications',
          component: () => import('@/views/company/ApplicationsView.vue')
        },
        {
          path: 'applications/:id',
          name: 'company-application-detail',
          component: () => import('@/views/company/ApplicationDetailView.vue')
        }
      ]
    },

    {
      path: '/student',
      component: StudentLayout,
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: 'dashboard',
          name: 'student-dashboard',
          component: () => import('@/views/student/DashboardView.vue')
        },
        {
          path: 'drives',
          name: 'student-drives',
          component: () => import('@/views/student/DrivesView.vue')
        },
        {
          path: 'drives/:id',
          name: 'student-drive-detail',
          component: () => import('@/views/student/DriveDetailView.vue')
        },
        {
          path: 'applications',
          name: 'student-applications',
          component: () => import('@/views/student/ApplicationsView.vue')
        },
        {
          path: 'applications/:id',
          name: 'student-application-detail',
          component: () => import('@/views/student/ApplicationDetailView.vue')
        },
        {
          path: 'profile',
          name: 'student-profile',
          component: () => import('@/views/student/ProfileView.vue')
        },
        {
          path: 'history',
          name: 'student-history',
          component: () => import('@/views/student/HistoryView.vue')
        }
      ]
    }
  ]
})

// Navigation guard - NEW SYNTAX (no next() callback)
router.beforeEach((to, from) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.getUserRole

  console.log('Navigation to:', to.path)
  console.log('Auth state:', { isAuthenticated, userRole })

  // Routes that require authentication
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // Redirect to login
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    
    // Check role
    if (to.meta.role && to.meta.role !== userRole) {
      // Redirect to appropriate dashboard based on role
      if (userRole === 'admin') return { name: 'admin-dashboard' }
      else return { name: 'home' }
    }
  }
  
  // Guest routes (login/register) - redirect if already logged in
  if (to.meta.guest && isAuthenticated) {
    if (userRole === 'admin') return { name: 'admin-dashboard' }
    else return { name: 'home' }
  }
  
  // Allow navigation
  return true
})

export default router