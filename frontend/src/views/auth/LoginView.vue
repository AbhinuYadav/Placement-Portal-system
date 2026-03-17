<!-- frontend/src/views/auth/LoginView.vue -->
<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <h2 class="text-center mb-4">Placement Portal</h2>
        <p class="text-center text-muted mb-4">Sign in to continue</p>
        
        <div v-if="error" class="alert alert-danger mb-3">
          {{ error }}
        </div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input 
              type="email" 
              class="form-control" 
              id="email" 
              v-model="email"
              required
            >
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="password"
              required
            >
          </div>

          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <span v-else>Sign in</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('admin@placement.edu')
const password = ref('Admin@123')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  console.log('1️⃣ Login form submitted')
  
  const result = await authStore.login({
    email: email.value,
    password: password.value
  })
  
  console.log('2️⃣ Login result:', result)
  
  if (result.success) {
    console.log('3️⃣ Login successful, checking auth state')
    console.log('   Token exists:', !!authStore.token)
    console.log('   User role:', authStore.user?.role)
    
    if (authStore.isAdmin) {
      console.log('4️⃣ Redirecting to admin dashboard')
      router.push('/admin/dashboard')
    } else {
      console.log('4️⃣ Redirecting to home')
      router.push('/')
    }
  } else {
    console.log('3️⃣ Login failed:', result.error)
    error.value = result.error
  }
  
  loading.value = false
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
</style>