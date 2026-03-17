// frontend/src/services/api.js
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to log and add token
apiClient.interceptors.request.use(
  (config) => {
    console.log(`\n📤 ===== REQUEST: ${config.method.toUpperCase()} ${config.url} =====`)
    
    // Get token from multiple sources
    const fromStore = useAuthStore().token
    const fromSession = sessionStorage.getItem('auth_store')
    
    console.log('Token from store:', fromStore ? 'exists' : 'null')
    console.log('Session storage:', fromSession ? 'exists' : 'null')
    
    let token = null
    
    // Try to get token from store first
    if (fromStore) {
      token = fromStore
      console.log('Using token from store')
    } 
    // Then try to parse from sessionStorage
    else if (fromSession) {
      try {
        const parsed = JSON.parse(fromSession)
        token = parsed.token
        console.log('Using token from sessionStorage')
      } catch (e) {
        console.error('Error parsing session storage:', e)
      }
    }
    
    if (token) {
      config.headers['Authentication-Token'] = token
      console.log('✅ Header set:', config.headers)
    } else {
      console.log('❌ No token found for request')
    }
    
    console.log('Final headers:', config.headers)
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log(`📥 ===== RESPONSE: ${response.config.url} =====`)
    console.log('Status:', response.status)
    console.log('Data:', response.data)
    return response
  },
  (error) => {
    console.log(`❌ ===== ERROR: ${error.config?.url} =====`)
    console.log('Status:', error.response?.status)
    console.log('Data:', error.response?.data)
    console.log('Headers sent:', error.config?.headers)
    
    if (error.response?.status === 401) {
      console.log('🔐 401 Unauthorized - redirecting to login')
      sessionStorage.removeItem('auth_store')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Import at bottom to avoid circular dependency
import { useAuthStore } from '@/stores/auth'

// ==================== ADMIN APIS ====================
export const adminAPI = {
  getDashboardStats: () => apiClient.get('/admin/dashboard'),
  getCompanies: (params) => apiClient.get('/admin/companies', { params }),
  getCompanyDetails: (id) => apiClient.get(`/admin/companies/${id}`),
  approveCompany: (id) => apiClient.post(`/admin/companies/${id}/approve`),
  rejectCompany: (id, data) => apiClient.post(`/admin/companies/${id}/reject`, data),
  blacklistCompany: (id, data) => apiClient.post(`/admin/companies/${id}/blacklist`, data),
  activateCompany: (id) => apiClient.post(`/admin/companies/${id}/activate`),
  getDrives: (params) => apiClient.get('/admin/drives', { params }),
  getDriveDetails: (id) => apiClient.get(`/admin/drives/${id}`),
  approveDrive: (id) => apiClient.post(`/admin/drives/${id}/approve`),
  rejectDrive: (id) => apiClient.post(`/admin/drives/${id}/reject`),
  closeDrive: (id) => apiClient.post(`/admin/drives/${id}/close`),
  getStudents: (params) => apiClient.get('/admin/students', { params }),
  getStudentDetails: (id) => apiClient.get(`/admin/students/${id}`),
  blacklistStudent: (id, data) => apiClient.post(`/admin/students/${id}/blacklist`, data),
  activateStudent: (id) => apiClient.post(`/admin/students/${id}/activate`),
  getApplications: (params) => apiClient.get('/admin/applications', { params }),
  generateMonthlyReport: () => apiClient.post('/admin/reports/monthly'),
}

// ==================== COMPANY APIS ====================
export const companyAPI = {
  getProfile: () => apiClient.get('/company/profile'),
  updateProfile: (data) => apiClient.put('/company/profile', data),
  getDrives: () => apiClient.get('/company/drives'),
  getDrive: (id) => apiClient.get(`/company/drives/${id}`),
  createDrive: (data) => apiClient.post('/company/drives', data),
  updateDrive: (id, data) => apiClient.put(`/company/drives/${id}`, data),
  deleteDrive: (id) => apiClient.delete(`/company/drives/${id}`),
  getDriveApplications: (driveId) => apiClient.get(`/company/drives/${driveId}/applications`),
  getApplications: (params) => apiClient.get('/company/applications', { params }),
  getApplication: (id) => apiClient.get(`/company/applications/${id}`),
  shortlistApplication: (id) => apiClient.post(`/company/applications/${id}/shortlist`),
  selectApplication: (id) => apiClient.post(`/company/applications/${id}/select`),
  rejectApplication: (id, data) => apiClient.post(`/company/applications/${id}/reject`, data),
  scheduleInterview: (id, data) => apiClient.post(`/company/applications/${id}/schedule-interview`, data),
  getDashboard: () => apiClient.get('/company/dashboard'),
}

// ==================== STUDENT APIS ====================
export const studentAPI = {
  // Profile
  getProfile: () => apiClient.get('/student/profile'),
  updateProfile: (data) => apiClient.put('/student/profile', data),
  
  // Dashboard
  getDashboard: () => apiClient.get('/student/dashboard'),
  
  // Drives
  getDrives: (params) => apiClient.get('/student/drives', { params }),
  getDrive: (id) => apiClient.get(`/student/drives/${id}`),
  applyToDrive: (id) => apiClient.post(`/student/drives/${id}/apply`),
  
  // Applications
  getApplications: (params) => apiClient.get('/student/applications', { params }),
  getApplication: (id) => apiClient.get(`/student/applications/${id}`),
  deleteApplication: (id) => apiClient.delete(`/student/applications/${id}`),
  
  // History
  getHistory: () => apiClient.get('/student/history'),
  exportApplications: () => apiClient.post('/student/export/applications'),
}

export default apiClient