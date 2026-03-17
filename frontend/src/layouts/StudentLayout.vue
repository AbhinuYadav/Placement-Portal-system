<!-- frontend/src/layouts/StudentLayout.vue -->
<template>
  <div class="student-layout">
    <!-- Navbar -->
    <nav class="navbar navbar-dark bg-primary fixed-top">
      <div class="container-fluid">
        <button class="btn btn-primary" @click="toggleSidebar">
          <i class="bi bi-list text-white"></i>
        </button>
        <router-link class="navbar-brand text-white" to="/student/dashboard">
          <i class="bi bi-mortarboard-fill me-2"></i>
          Student Portal
        </router-link>
        <div class="d-flex align-items-center">
          <span class="text-black me-3">
            <i class="bi bi-person-circle me-1"></i>
            {{ authStore.user?.email }}
          </span>
          <button class="btn btn-outline-dark btn-sm" @click="logout">
            <i class="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar -->
    <div class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-header">
        <h5 class="text-white">Student Menu</h5>
      </div>
      <ul class="nav flex-column">
        <li class="nav-item">
          <router-link to="/student/dashboard" class="nav-link" @click="closeSidebar">
            <i class="bi bi-speedometer2 me-2"></i> Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/student/drives" class="nav-link" @click="closeSidebar">
            <i class="bi bi-briefcase me-2"></i> Available Drives
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/student/applications" class="nav-link" @click="closeSidebar">
            <i class="bi bi-file-text me-2"></i> My Applications
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/student/profile" class="nav-link" @click="closeSidebar">
            <i class="bi bi-person-circle me-2"></i> My Profile
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/student/history" class="nav-link" @click="closeSidebar">
            <i class="bi bi-clock-history me-2"></i> Placement History
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="container-fluid">
        <router-view />
      </div>
    </div>

    <!-- Sidebar backdrop for mobile -->
    <div class="sidebar-backdrop" v-if="sidebarOpen" @click="sidebarOpen = false"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const windowWidth = ref(window.innerWidth)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  if (windowWidth.value < 768) {
    sidebarOpen.value = false
  }
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (windowWidth.value >= 768) {
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
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Navbar */
.navbar {
  height: 60px;
  padding: 0 1rem;
  z-index: 1030;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Sidebar */
.sidebar {
  position: fixed;
  top: 60px;
  left: -250px;
  width: 250px;
  height: calc(100vh - 60px);
  background: #343a40;
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
  border-bottom: 1px solid #495057;
}

.sidebar .nav-link {
  color: #adb5bd;
  padding: 0.8rem 1rem;
  transition: all 0.3s;
  text-decoration: none;
}

.sidebar .nav-link:hover {
  color: white;
  background: #495057;
}

.sidebar .nav-link.router-link-active {
  color: white;
  background: #667eea;
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