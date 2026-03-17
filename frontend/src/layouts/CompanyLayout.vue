<!-- frontend/src/layouts/CompanyLayout.vue -->
<template>
  <div class="company-layout">
    <!-- Blacklisted Banner -->
    <div v-if="isBlacklisted" class="blacklisted-banner">
      <div class="container-fluid">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <strong>ACCOUNT BLACKLISTED:</strong> Your company has been blacklisted. You cannot access any features. Please contact the institute administrator.
      </div>
    </div>

    <!-- Pending Approval Banner -->
    <div v-else-if="!isApproved" class="pending-banner">
      <div class="container-fluid">
        <i class="bi bi-clock-history me-2"></i>
        <strong>PENDING APPROVAL:</strong> Your company is awaiting admin approval. You can view your profile but cannot create drives until approved.
      </div>
    </div>

    <!-- Navbar -->
    <nav class="navbar navbar-dark" :class="navbarClass" :style="{ top: bannerHeight }">
      <div class="container-fluid">
        <button class="btn" :class="navButtonClass" @click="toggleSidebar" :disabled="isBlacklisted">
          <i class="bi bi-list text-white"></i>
        </button>
        <router-link class="navbar-brand text-white" to="/company/dashboard">
          <i class="bi bi-building me-2"></i>
          Company Portal
        </router-link>
        <div class="d-flex align-items-center">
          <!-- Status Badge -->
          <span class="badge me-3" :class="statusBadgeClass">
            {{ statusText }}
          </span>
          <span class="text-black me-3">
            <i class="bi bi-person-circle me-1"></i>
            {{ companyName }}
          </span>
          <button class="btn btn-outline-dark btn-sm" @click="logout">
            <i class="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar - Hide completely if blacklisted -->
    <div v-if="!isBlacklisted" class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <h5 class="text-white">Company Menu</h5>
        <div v-if="!isApproved" class="text-warning small mt-2">
          <i class="bi bi-clock-history me-1"></i>
          Limited access - Pending approval
        </div>
      </div>
      <ul class="nav flex-column">
        <li class="nav-item">
          <router-link to="/company/dashboard" class="nav-link" @click="closeSidebar">
            <i class="bi bi-speedometer2 me-2"></i> Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/company/profile" class="nav-link" @click="closeSidebar">
            <i class="bi bi-building me-2"></i> Company Profile
          </router-link>
        </li>
        <!-- Only show Create Drive link if approved -->
        <li v-if="isApproved" class="nav-item">
          <router-link to="/company/drives/create" class="nav-link" @click="closeSidebar">
            <i class="bi bi-plus-circle me-2"></i> Create Drive
          </router-link>
        </li>
        <!-- Show My Drives and Applications regardless (view only) -->
        <li class="nav-item">
          <router-link to="/company/drives" class="nav-link" @click="closeSidebar">
            <i class="bi bi-briefcase me-2"></i> My Drives
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/company/applications" class="nav-link" @click="closeSidebar">
            <i class="bi bi-file-text me-2"></i> Applications
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Blacklisted Message - Full screen message -->
    <div v-if="isBlacklisted" class="blacklisted-fullscreen">
      <div class="container">
        <div class="alert alert-danger text-center p-5">
          <i class="bi bi-lock-fill fs-1 d-block mb-4"></i>
          <h2 class="mb-3">Account Blacklisted</h2>
          <p class="lead mb-4">Your company account has been blacklisted by the administrator.</p>
          <p class="mb-4">You cannot access any company features. Please contact the institute for more information.</p>
          <button class="btn btn-danger btn-lg" @click="logout">
            <i class="bi bi-box-arrow-right me-2"></i>
            Logout
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content - Only show if not blacklisted -->
    <div v-else class="main-content" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="container-fluid">
        <!-- Pending Approval Overlay for restricted features -->
        <router-view v-slot="{ Component }">
          <template v-if="Component">
            <div v-if="!isApproved && $route.path.includes('/drives/create')" class="pending-overlay">
              <div class="alert alert-warning text-center p-5">
                <i class="bi bi-clock-history fs-1 d-block mb-4"></i>
                <h3 class="mb-3">Pending Approval</h3>
                <p class="lead mb-4">Your company is awaiting admin approval.</p>
                <p class="mb-4">You cannot create drives until your company is approved by the administrator.</p>
                <router-link to="/company/dashboard" class="btn btn-warning btn-lg">
                  <i class="bi bi-arrow-left me-2"></i>
                  Back to Dashboard
                </router-link>
              </div>
            </div>
            <component v-else :is="Component" />
          </template>
        </router-view>
      </div>
    </div>

    <!-- Sidebar backdrop for mobile -->
    <div class="sidebar-backdrop" v-if="sidebarOpen && !isBlacklisted" @click="sidebarOpen = false"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const messageStore = useMessageStore()

const sidebarOpen = ref(false)
const windowWidth = ref(window.innerWidth)
const companyProfile = ref({})
const loading = ref(true)

// Computed properties
const isBlacklisted = computed(() => companyProfile.value?.is_blacklisted || false)
const isApproved = computed(() => companyProfile.value?.approval_status === 'approved')
const companyName = computed(() => companyProfile.value?.company_name || authStore.user?.email)

const statusText = computed(() => {
  if (isBlacklisted.value) return 'Blacklisted'
  if (isApproved.value) return 'Approved'
  return 'Pending Approval'
})

const statusBadgeClass = computed(() => {
  if (isBlacklisted.value) return 'bg-danger'
  if (isApproved.value) return 'bg-success'
  return 'bg-warning text-dark'
})

const navbarClass = computed(() => {
  if (isBlacklisted.value) return 'bg-danger'
  if (!isApproved.value) return 'bg-warning'
  return 'bg-success'
})

const navButtonClass = computed(() => {
  if (isBlacklisted.value) return 'btn-danger'
  if (!isApproved.value) return 'btn-warning'
  return 'btn-success'
})

const bannerHeight = computed(() => {
  if (isBlacklisted.value || !isApproved.value) return '40px'
  return '0'
})

// Fetch company profile
const fetchCompanyProfile = async () => {
  try {
    const response = await companyAPI.getProfile()
    companyProfile.value = response.data.profile || {}
    
    // Redirect if blacklisted trying to access features
    if (companyProfile.value.is_blacklisted) {
      messageStore.updateErrorMessages('Your company account has been blacklisted.')
    }
  } catch (err) {
    console.error('Error fetching company profile:', err)
  }
}

const toggleSidebar = () => {
  if (!isBlacklisted.value) {
    sidebarOpen.value = !sidebarOpen.value
  }
}

const closeSidebar = () => {
  if (windowWidth.value < 768) {
    sidebarOpen.value = false
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (windowWidth.value >= 768 && !isBlacklisted.value) {
    sidebarOpen.value = true
  } else {
    sidebarOpen.value = false
  }
}

const logout = async () => {
  await authStore.logout()
  router.push('/')
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  handleResize()
  fetchCompanyProfile()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.company-layout {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Banners */
.blacklisted-banner,
.pending-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 40px;
  display: flex;
  align-items: center;
  z-index: 1050;
  font-size: 0.9rem;
  padding: 0 1rem;
}

.blacklisted-banner {
  background: #dc3545;
  color: white;
}

.pending-banner {
  background: #ffc107;
  color: #212529;
}

/* Navbar */
.navbar {
  height: 60px;
  padding: 0 1rem;
  z-index: 1040;
  transition: top 0.3s ease;
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 60px;
  left: -250px;
  width: 250px;
  height: calc(100vh - 60px);
  background: #198754;
  color: white;
  transition: left 0.3s ease;
  z-index: 1020;
  overflow-y: auto;
}

.sidebar.sidebar-open {
  left: 0;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.sidebar .nav-link {
  color: rgba(255,255,255,0.85);
  padding: 0.8rem 1rem;
  transition: all 0.3s;
  text-decoration: none;
  display: block;
}

.sidebar .nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.15);
}

.sidebar .nav-link.router-link-active {
  color: white;
  background: rgba(255,255,255,0.25);
  border-left: 4px solid white;
}

/* Blacklisted Fullscreen */
.blacklisted-fullscreen {
  margin-top: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 160px);
}

.blacklisted-fullscreen .alert {
  max-width: 600px;
  margin: 0 auto;
  border: none;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.2);
}

/* Pending Overlay */
.pending-overlay {
  max-width: 600px;
  margin: 2rem auto;
}

.pending-overlay .alert {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(255, 193, 7, 0.2);
}

/* Main Content */
.main-content {
  margin-top: 60px;
  margin-left: 0;
  padding: 1.5rem;
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - 60px);
}

.main-content.sidebar-open {
  margin-left: 250px;
}

/* Backdrop */
.sidebar-backdrop {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1010;
}

/* Desktop */
@media (min-width: 768px) {
  .sidebar {
    left: 0;
  }
  
  .main-content {
    margin-left: 250px;
  }
  
  .sidebar-backdrop {
    display: none;
  }
}
</style>