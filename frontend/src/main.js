// frontend/src/main.js
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import axios from 'axios'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia setup
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// Import auth store AFTER pinia is installed
import { useAuthStore } from './stores/auth'

// Initialize auth
const authStore = useAuthStore()
authStore.initAuth()  // ✅ This will now work

// Log the current auth state
console.log('🚀 App starting...')
console.log('🔐 Auth state:', authStore.isAuthenticated ? 'Authenticated' : 'Not authenticated')
if (authStore.token) {
  console.log('🔑 Token exists, length:', authStore.token.length)
}

app.mount('#app')