<!-- frontend/src/views/admin/DashboardView.vue -->
<template>
  <div class="dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Dashboard Overview</h2>
      <div class="text-muted">
        <i class="bi bi-clock me-1"></i>
        Last updated: {{ lastUpdated }}
        <button class="btn btn-sm btn-outline-primary ms-2" @click="fetchDashboardData">
          <i class="bi bi-arrow-repeat"></i>
        </button>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3 text-muted">Fetching dashboard data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchDashboardData">Retry</button>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- Stats Cards Row -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card stat-card bg-primary text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="card-title text-white-50 text-uppercase small">Total Students</h6>
                  <h2 class="mb-0">{{ formatNumber(stats.total_students) }}</h2>
                </div>
                <i class="bi bi-people-fill fs-1 text-white-50"></i>
              </div>
            </div>
            <div class="card-footer bg-primary border-0 d-flex justify-content-between align-items-center">
              <span>View all students</span>
              <router-link to="/admin/students" class="text-white stretched-link">
                <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card stat-card bg-success text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="card-title text-white-50 text-uppercase small">Total Companies</h6>
                  <h2 class="mb-0">{{ formatNumber(stats.total_companies) }}</h2>
                </div>
                <i class="bi bi-building fs-1 text-white-50"></i>
              </div>
            </div>
            <div class="card-footer bg-success border-0 d-flex justify-content-between align-items-center">
              <span>View all companies</span>
              <router-link to="/admin/companies" class="text-white stretched-link">
                <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card stat-card bg-warning text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="card-title text-white-50 text-uppercase small">Active Drives</h6>
                  <h2 class="mb-0">{{ formatNumber(stats.active_drives || stats.total_drives) }}</h2>
                </div>
                <i class="bi bi-briefcase-fill fs-1 text-white-50"></i>
              </div>
            </div>
            <div class="card-footer bg-warning border-0 d-flex justify-content-between align-items-center">
              <span>View all drives</span>
              <router-link to="/admin/drives" class="text-white stretched-link">
                <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card stat-card bg-info text-white h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="card-title text-white-50 text-uppercase small">Applications</h6>
                  <h2 class="mb-0">{{ formatNumber(stats.total_applications) }}</h2>
                </div>
                <i class="bi bi-file-text-fill fs-1 text-white-50"></i>
              </div>
            </div>
            <div class="card-footer bg-info border-0 d-flex justify-content-between align-items-center">
              <span>View applications</span>
              <router-link to="/admin/applications" class="text-white stretched-link">
                <i class="bi bi-arrow-right"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Export Report -->
       <div class="row mb-4">
  <div class="col-12">
    <div class="d-flex justify-content-end">
      <button 
        class="btn btn-primary" 
        @click="generateMonthlyReport"
        :disabled="generatingReport"
      >
        <i class="bi" :class="generatingReport ? 'bi-hourglass-split' : 'bi-file-earmark-spreadsheet'"></i>
        {{ generatingReport ? 'Generating...' : 'Generate Monthly Report' }}
      </button>
    </div>
  </div>
</div>

      <!-- Pending Approvals Row -->
      <div class="row g-4 mb-4">
        <!-- Pending Companies -->
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-building me-2 text-warning"></i>
                Pending Company Approvals
                <span class="badge bg-warning ms-2">{{ pendingCompanies.length }}</span>
              </h5>
              <router-link to="/admin/companies?status=pending" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="pendingCompanies.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-check-circle fs-1 d-block mb-2"></i>
                No pending companies
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>HR Name</th>
                      <th>Registered</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="company in pendingCompanies.slice(0, 5)" :key="company.id">
                      <td>
                        <strong>{{ company.company_name }}</strong>
                      </td>
                      <td>{{ company.hr_name }}</td>
                      <td>{{ formatDate(company.created_at) }}</td>
                      <td>
                        <button 
                          class="btn btn-sm btn-success me-1" 
                          @click="approveCompany(company.id)"
                          :disabled="processingId === company.id"
                          title="Approve"
                        >
                          <span v-if="processingId === company.id" class="spinner-border spinner-border-sm"></span>
                          <i v-else class="bi bi-check-lg"></i>
                        </button>
                        <button 
                          class="btn btn-sm btn-danger" 
                          @click="rejectCompany(company.id)"
                          :disabled="processingId === company.id"
                          title="Reject"
                        >
                          <i class="bi bi-x-lg"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Drives -->
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-briefcase me-2 text-warning"></i>
                Pending Drive Approvals
                <span class="badge bg-warning ms-2">{{ pendingDrives.length }}</span>
              </h5>
              <router-link to="/admin/drives?status=pending" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="pendingDrives.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-check-circle fs-1 d-block mb-2"></i>
                No pending drives
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Drive Name</th>
                      <th>Company</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="drive in pendingDrives.slice(0, 5)" :key="drive.id">
                      <td>
                        <strong>{{ drive.drive_name }}</strong>
                      </td>
                      <td>{{ drive.company_name }}</td>
                      <td>{{ formatDate(drive.created_at) }}</td>
                      <td>
                        <button 
                          class="btn btn-sm btn-success me-1" 
                          @click="approveDrive(drive.id)"
                          :disabled="processingId === drive.id"
                          title="Approve"
                        >
                          <span v-if="processingId === drive.id" class="spinner-border spinner-border-sm"></span>
                          <i v-else class="bi bi-check-lg"></i>
                        </button>
                        <button 
                          class="btn btn-sm btn-danger" 
                          @click="rejectDrive(drive.id)"
                          :disabled="processingId === drive.id"
                          title="Reject"
                        >
                          <i class="bi bi-x-lg"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Applications -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-table me-2 text-primary"></i>
                Recent Applications
              </h5>
              <router-link to="/admin/applications" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="recentApplications.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>
                No recent applications
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Company</th>
                      <th>Drive</th>
                      <th>Status</th>
                      <th>Applied On</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in recentApplications" :key="app.id">
                      <td>
                        <i class="bi bi-person-circle me-2"></i>
                        {{ app.student_name }}
                      </td>
                      <td>{{ app.company_name }}</td>
                      <td>{{ app.drive_name }}</td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(app.status)">
                          {{ app.status }}
                        </span>
                      </td>
                      <td>{{ formatDateTime(app.applied_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { adminAPI } from '@/services/api'

const router = useRouter()
const messageStore = useMessageStore()

// State
const generatingReport = ref(false)
const loading = ref(true)
const error = ref(null)
const stats = ref({
  total_students: 0,
  total_companies: 0,
  total_drives: 0,
  total_applications: 0
})

const pendingCompanies = ref([])
const pendingDrives = ref([])
const recentApplications = ref([])
const processingId = ref(null)

const lastUpdated = ref(new Date().toLocaleString())

// Helper Functions
const formatNumber = (num) => {
  return num?.toLocaleString() || '0'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const generateMonthlyReport = async () => {
  if (generatingReport.value) return
  
  generatingReport.value = true
  try {
    const response = await adminAPI.generateMonthlyReport()
    messageStore.updateSuccessMessages('Monthly report generation started! You will receive an email when complete.')
    console.log('Report task started:', response.data.task_id)
  } catch (error) {
    console.error('Report generation error:', error)
    messageStore.updateErrorMessages(error.response?.data?.message || 'Failed to generate report')
  } finally {
    generatingReport.value = false
  }
}

const getStatusBadgeClass = (status) => {
  const statusMap = {
    'applied': 'bg-warning text-dark',
    'shortlisted': 'bg-info text-white',
    'selected': 'bg-success text-white',
    'rejected': 'bg-danger text-white',
    'pending': 'bg-warning text-dark',
    'approved': 'bg-success text-white'
  }
  return statusMap[status?.toLowerCase()] || 'bg-secondary text-white'
}

// Fetch all dashboard data
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await adminAPI.getDashboardStats()
    console.log('Dashboard data:', response.data)
    
    if (response.data) {
      stats.value = response.data.stats || {}
      pendingCompanies.value = response.data.pending_companies || []
      pendingDrives.value = response.data.pending_drives || []
      recentApplications.value = response.data.recent_applications || []
    }
    
    lastUpdated.value = new Date().toLocaleString()
    
  } catch (err) {
    console.error('Dashboard error:', err)
    error.value = err.response?.data?.message || 'Failed to load dashboard'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Actions
const approveCompany = async (id) => {
  processingId.value = id
  try {
    await adminAPI.approveCompany(id)
    messageStore.updateSuccessMessages('Company approved')
    await fetchDashboardData()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Approval failed')
  } finally {
    processingId.value = null
  }
}

const rejectCompany = async (id) => {
  const reason = prompt('Enter rejection reason:')
  if (!reason) return
  
  processingId.value = id
  try {
    await adminAPI.rejectCompany(id, { reason })
    messageStore.updateSuccessMessages('Company rejected')
    await fetchDashboardData()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Rejection failed')
  } finally {
    processingId.value = null
  }
}

const approveDrive = async (id) => {
  processingId.value = id
  try {
    await adminAPI.approveDrive(id)
    messageStore.updateSuccessMessages('Drive approved')
    await fetchDashboardData()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Approval failed')
  } finally {
    processingId.value = null
  }
}

const rejectDrive = async (id) => {
  processingId.value = id
  try {
    await adminAPI.rejectDrive(id)
    messageStore.updateSuccessMessages('Drive rejected')
    await fetchDashboardData()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Rejection failed')
  } finally {
    processingId.value = null
  }
}

// Auto-refresh
let refreshInterval
onMounted(() => {
  fetchDashboardData()
  refreshInterval = setInterval(fetchDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.dashboard-title {
  font-size: 1.8rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card {
  border: none;
  border-radius: 1rem;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
}

.stat-card .card-footer {
  background: rgba(0,0,0,0.1);
  border-top: none;
  padding: 0.75rem 1.25rem;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #6c757d;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}
</style>