<!-- frontend/src/components/layout/Navbar.vue -->
<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
    <div class="container-fluid">
      <button class="navbar-toggler" type="button" @click="$emit('toggle-sidebar')">
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <router-link class="navbar-brand" to="/admin/dashboard">
        <i class="bi bi-shield-lock-fill me-2"></i>
        Admin Portal
      </router-link>
      
      <div class="ms-auto d-flex align-items-center">
        <!-- Email display - white text -->
        <span class="text-white me-3 d-none d-md-inline">
          <i class="bi bi-person-circle me-1"></i>
          {{ authStore.user?.email }}
        </span>
        
        <!-- Logout button - light outline -->
        <button class="btn btn-outline-light btn-sm" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i>
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  height: var(--topNavbarHeight);
  padding: 0.5rem 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1040;
}

/* Ensure text is white on dark background */
.navbar-dark .navbar-brand {
  color: white;
}

/* ✅ FIXED: Text should be white, not black */
.text-white {
  color: white !important;
}

/* ✅ FIXED: Button text should be white with white border */
.btn-outline-light {
  color: white !important;
  border-color: white !important;
  background: transparent;
}

.btn-outline-light:hover {
  color: #343a40 !important;
  background-color: white !important;
  border-color: white !important;
}
</style>