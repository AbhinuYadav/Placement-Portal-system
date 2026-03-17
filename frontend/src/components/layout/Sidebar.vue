<!-- frontend/src/components/layout/Sidebar.vue -->
<template>
  <div class="sidebar-nav bg-dark" :class="{ show: isOpen }">
    <div class="sidebar-content">
      <ul class="navbar-nav flex-column">
        <!-- Admin Section - Always visible for admin -->
        <template v-if="authStore.isAdmin">
          <!-- CORE Section -->
          <li class="nav-item mt-3">
            <div class="text-white-50 small fw-bold text-uppercase px-3 mb-2">
              CORE
            </div>
          </li>
          <li class="nav-item">
            <router-link to="/admin/dashboard" class="nav-link" :class="{ active: isActive('/admin/dashboard') }" @click="closeSidebar">
              <i class="bi bi-speedometer2 me-3"></i>
              <span>Dashboard</span>
            </router-link>
          </li>
          
          <!-- MANAGEMENT Section -->
          <li class="nav-item mt-3">
            <div class="text-white-50 small fw-bold text-uppercase px-3 mb-2">
              MANAGEMENT
            </div>
          </li>
          <li class="nav-item">
            <router-link to="/admin/companies" class="nav-link" :class="{ active: isActive('/admin/companies') }" @click="closeSidebar">
              <i class="bi bi-building me-3"></i>
              <span>Companies</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/admin/drives" class="nav-link" :class="{ active: isActive('/admin/drives') }" @click="closeSidebar">
              <i class="bi bi-briefcase me-3"></i>
              <span>Drives</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/admin/students" class="nav-link" :class="{ active: isActive('/admin/students') }" @click="closeSidebar">
              <i class="bi bi-people me-3"></i>
              <span>Students</span>
            </router-link>
          </li>
          <!-- APPLICATIONS LINK -->
          <li class="nav-item">
            <router-link to="/admin/applications" class="nav-link" :class="{ active: isActive('/admin/applications') }" @click="closeSidebar">
              <i class="bi bi-file-text me-3"></i>
              <span>Applications</span>
            </router-link>
          </li>
          
          <!-- REPORTS Section -->
          <li class="nav-item mt-3">
            <div class="text-white-50 small fw-bold text-uppercase px-3 mb-2">
              REPORTS
            </div>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent>
              <i class="bi bi-graph-up me-3"></i>
              <span>Statistics</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent>
              <i class="bi bi-calendar me-3"></i>
              <span>Monthly Report</span>
            </a>
          </li>
          
          <hr class="dropdown-divider bg-light mx-3 my-3">
          
          <!-- ACCOUNT Section -->
          <li class="nav-item">
            <a href="#" class="nav-link" @click.prevent>
              <i class="bi bi-gear me-3"></i>
              <span>Settings</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link text-danger" @click.prevent="logout">
              <i class="bi bi-box-arrow-right me-3"></i>
              <span>Logout</span>
            </a>
          </li>
        </template>

        <!-- Company Section - Different menu for company users -->
        <template v-else-if="authStore.isCompany">
          <li class="nav-item mt-3">
            <div class="text-white-50 small fw-bold text-uppercase px-3 mb-2">
              COMPANY
            </div>
          </li>
          <li class="nav-item">
            <router-link to="/company/dashboard" class="nav-link" @click="closeSidebar">
              <i class="bi bi-speedometer2 me-3"></i>
              <span>Dashboard</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/company/drives" class="nav-link" @click="closeSidebar">
              <i class="bi bi-briefcase me-3"></i>
              <span>My Drives</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/company/applications" class="nav-link" @click="closeSidebar">
              <i class="bi bi-file-text me-3"></i>
              <span>Applications</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/company/profile" class="nav-link" @click="closeSidebar">
              <i class="bi bi-building me-3"></i>
              <span>Company Profile</span>
            </router-link>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link text-danger" @click.prevent="logout">
              <i class="bi bi-box-arrow-right me-3"></i>
              <span>Logout</span>
            </a>
          </li>
        </template>

        <!-- Student Section - Different menu for students -->
        <template v-else-if="authStore.isStudent">
          <li class="nav-item mt-3">
            <div class="text-white-50 small fw-bold text-uppercase px-3 mb-2">
              STUDENT
            </div>
          </li>
          <li class="nav-item">
            <router-link to="/student/dashboard" class="nav-link" @click="closeSidebar">
              <i class="bi bi-speedometer2 me-3"></i>
              <span>Dashboard</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/student/drives" class="nav-link" @click="closeSidebar">
              <i class="bi bi-briefcase me-3"></i>
              <span>Available Drives</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/student/applications" class="nav-link" @click="closeSidebar">
              <i class="bi bi-file-text me-3"></i>
              <span>My Applications</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/student/profile" class="nav-link" @click="closeSidebar">
              <i class="bi bi-person-circle me-3"></i>
              <span>Profile</span>
            </router-link>
          </li>
          <li class="nav-item">
            <a href="#" class="nav-link text-danger" @click.prevent="logout">
              <i class="bi bi-box-arrow-right me-3"></i>
              <span>Logout</span>
            </a>
          </li>
        </template>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const closeSidebar = () => {
  if (window.innerWidth < 992) {
    emit('close')
  }
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar-nav {
  width: var(--offcanvas-width);
  position: fixed;
  top: var(--topNavbarHeight);
  left: 0;
  height: calc(100vh - var(--topNavbarHeight));
  background: var(--sidebar-bg);
  color: white;
  transition: transform 0.3s ease;
  z-index: 1030;
  overflow-y: auto;
}

.sidebar-content {
  padding: 1rem 0;
}

.nav-link {
  color: rgba(255,255,255,0.65);
  padding: 0.8rem 1.5rem;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  text-decoration: none;
}

.nav-link:hover {
  color: white;
  background: rgba(255,255,255,0.1);
}

.nav-link.router-link-active,
.nav-link.active {
  color: white;
  background: rgba(255,255,255,0.2);
  border-left: 4px solid #0d6efd;
}

/* ✅ FIXED: Ensure logout button text is visible */
.nav-link.text-danger {
  color: #dc3545 !important;
}

.nav-link.text-danger:hover {
  color: white !important;
  background: rgba(220, 53, 69, 0.8);
}

hr {
  opacity: 0.1;
  margin: 1rem 1.5rem;
}

.text-white-50 {
  color: rgba(255, 255, 255, 0.5) !important;
}

@media (max-width: 991.98px) {
  .sidebar-nav {
    transform: translateX(-100%);
  }
  
  .sidebar-nav.show {
    transform: translateX(0);
  }
}
</style>