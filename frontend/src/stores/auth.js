// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
    loading: false
  }),
  
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'auth_store',
        storage: sessionStorage,
        paths: ['token', 'user']
      }
    ]
  },
  
  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    getUserRole: (state) => state.user?.role || null,
    isAdmin: (state) => state.user?.role === 'admin',
    isCompany: (state) => state.user?.role === 'company',
    isStudent: (state) => state.user?.role === 'student',
    getUserEmail: (state) => state.user?.email || ''
  },
  
  actions: {
    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authentication-Token'] = this.token
        console.log('✅ Auth initialized with token from storage')
      }
    },
    
    async login(credentials) {
      this.loading = true
      
      try {
        const response = await axios.post(`${API_BASE_URL}/login`, credentials)
        
        if (response.data.auth_token) {
          this.token = response.data.auth_token
          this.user = response.data.user
          axios.defaults.headers.common['Authentication-Token'] = this.token
          return { success: true, user: this.user }
        }
        return { success: false, error: 'No token received' }
      } catch (error) {
        return { 
          success: false, 
          error: error.response?.data?.message || 'Login failed' 
        }
      } finally {
        this.loading = false
      }
    },
    
    // ✅ ADD THIS REGISTER FUNCTION
    async register(userData) {
      this.loading = true
      
      try {
        console.log('📤 Sending registration request:', userData)
        const response = await axios.post(`${API_BASE_URL}/register`, userData)
        console.log('📥 Registration response:', response.data)
        
        return { 
          success: true, 
          message: response.data.message || 'Registration successful!' 
        }
      } catch (error) {
        console.error('❌ Registration error:', error.response?.data || error.message)
        return { 
          success: false, 
          error: error.response?.data?.message || 'Registration failed' 
        }
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      delete axios.defaults.headers.common['Authentication-Token']
      sessionStorage.removeItem('auth_store')
    }
  }
})