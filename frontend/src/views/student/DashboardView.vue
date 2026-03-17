<!-- frontend/src/views/student/DashboardView.vue -->
<template>
  <div class="dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Student Dashboard</h2>
      <div class="text-muted">
        <i class="bi bi-person-circle me-1"></i>
        {{ studentProfile.name }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchDashboard">Retry</button>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- Stats Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="card stat-card bg-primary text-white">
            <div class="card-body">
              <h6 class="card-title text-white-50">Total Applications</h6>
              <h2 class="mb-0">{{ stats.total_applications || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card bg-warning text-white">
            <div class="card-body">
              <h6 class="card-title text-white-50">Pending</h6>
              <h2 class="mb-0">{{ stats.pending || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card bg-info text-white">
            <div class="card-body">
              <h6 class="card-title text-white-50">Shortlisted</h6>
              <h2 class="mb-0">{{ stats.shortlisted || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card bg-success text-white">
            <div class="card-body">
              <h6 class="card-title text-white-50">Selected</h6>
              <h2 class="mb-0">{{ stats.selected || 0 }}</h2>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Exporting -->
      <div class="row mb-4">
  <div class="col-12">
    <div class="d-flex justify-content-end">
      <button 
        class="btn btn-primary" 
        @click="exportApplications"
        :disabled="exporting"
      >
        <i class="bi" :class="exporting ? 'bi-hourglass-split' : 'bi-download'"></i>
        {{ exporting ? 'Exporting...' : 'Export Applications' }}
      </button>
    </div>
  </div>
</div>

      <!-- Upcoming Interviews Section (only if exists) -->
      <div v-if="upcomingInterviews.length > 0" class="row mb-4">
        <div class="col-12">
          <div class="card border-warning">
            <div class="card-header bg-warning text-white">
              <h5 class="mb-0">
                <i class="bi bi-calendar-event me-2"></i>
                Upcoming Interviews
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div v-for="interview in upcomingInterviews" :key="interview.id" class="col-md-6 mb-3">
                  <div class="border rounded p-3">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="mb-1">{{ interview.company_name }}</h6>
                        <p class="mb-1"><strong>{{ interview.drive_name }}</strong></p>
                        <p class="mb-0 text-muted">
                          <i class="bi bi-clock me-1"></i>
                          {{ formatDateTime(interview.interview_date) }}
                        </p>
                        <p v-if="interview.interview_notes" class="mb-0 mt-2 small">
                          <i class="bi bi-info-circle me-1"></i>
                          {{ interview.interview_notes }}
                        </p>
                      </div>
                      <span class="badge bg-warning text-dark">Scheduled</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Deadlines -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-calendar-week me-2 text-primary"></i>
                Upcoming Deadlines
              </h5>
              <router-link to="/student/drives" class="btn btn-sm btn-outline-primary">
                View All Drives
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="upcomingDeadlines.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-calendar-x fs-1 d-block mb-3"></i>
                <p>No upcoming deadlines</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Drive Name</th>
                      <th>Deadline</th>
                      <th>Days Left</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="drive in upcomingDeadlines" :key="drive.id">
                      <td>
                        <i class="bi bi-building me-1 text-primary"></i>
                        {{ drive.company_name }}
                      </td>
                      <td>
                        <strong>{{ drive.drive_name }}</strong>
                      </td>
                      <td>
                        <span class="badge" :class="getDeadlineClass(drive.deadline)">
                          {{ formatDate(drive.deadline) }}
                        </span>
                      </td>
                      <td>
                        <span class="badge" :class="getDaysLeftClass(drive.days_left)">
                          <i class="bi bi-clock me-1"></i>
                          {{ drive.days_left }} day{{ drive.days_left !== 1 ? 's' : '' }}
                        </span>
                      </td>
                      <td>
                        <router-link 
                          :to="`/student/drives/${drive.id}`" 
                          class="btn btn-sm btn-outline-primary"
                        >
                          <i class="bi bi-eye me-1"></i>
                          View
                        </router-link>
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
        <div class="col-md-12">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-file-text me-2 text-success"></i>
                Recent Applications
              </h5>
              <router-link to="/student/applications" class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="recentApplications.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-file-text fs-1 d-block mb-3"></i>
                <p>No applications yet</p>
                <router-link to="/student/drives" class="btn btn-primary">
                  Browse Drives
                </router-link>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Drive</th>
                      <th>Applied On</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in recentApplications" :key="app.id">
                      <td>
                        <i class="bi bi-building me-1 text-primary"></i>
                        {{ app.company_name }}
                      </td>
                      <td>{{ app.drive_name }}</td>
                      <td>{{ formatDate(app.applied_at) }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(app.status)">
                          {{ app.status }}
                        </span>
                      </td>
                      <td>
                        <router-link 
                          :to="`/student/applications/${app.id}`" 
                          class="btn btn-sm btn-outline-primary"
                        >
                          <i class="bi bi-eye me-1"></i>
                          View
                        </router-link>
                      </td>
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'
import { studentAPI } from '@/services/api'

const authStore = useAuthStore()
const messageStore = useMessageStore()

// State
const exporting = ref(false)
const loading = ref(true)
const error = ref(null)
const studentProfile = ref({})
const stats = ref({})
const upcomingDeadlines = ref([])
const recentApplications = ref([])
const upcomingInterviews = ref([])

// Helper Functions
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
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const exportApplications = async () => {
  if (exporting.value) return
  
  exporting.value = true
  try {
    const response = await studentAPI.exportApplications()
    messageStore.updateSuccessMessages('Export started! You will receive an email when complete.')
    console.log('Export task started:', response.data.task_id)
  } catch (error) {
    console.error('Export error:', error)
    messageStore.updateErrorMessages(error.response?.data?.message || 'Failed to start export')
  } finally {
    exporting.value = false
  }
}

const getStatusClass = (status) => {
  switch(status?.toLowerCase()) {
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    case 'rejected': return 'bg-danger text-white'
    default: return 'bg-secondary'
  }
}

const getDeadlineClass = (deadline) => {
  if (!deadline) return 'bg-secondary'
  
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const diffDays = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'bg-danger'
  if (diffDays <= 3) return 'bg-warning text-dark'
  if (diffDays <= 7) return 'bg-info'
  return 'bg-success'
}

const getDaysLeftClass = (days) => {
  if (days <= 3) return 'bg-danger'
  if (days <= 7) return 'bg-warning text-dark'
  return 'bg-success'
}

// Calculate days left from deadline
const calculateDaysLeft = (deadline) => {
  if (!deadline) return 0
  const deadlineDate = new Date(deadline)
  const today = new Date()
  const diffTime = deadlineDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays > 0 ? diffDays : 0
}

// Fetch Dashboard Data
const fetchDashboard = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('Fetching student dashboard...')
    const response = await studentAPI.getDashboard()
    console.log('Dashboard response:', response.data)
    
    studentProfile.value = response.data.student || {}
    stats.value = response.data.statistics || {}
    
    // Process upcoming deadlines with proper data
    const rawDeadlines = response.data.upcoming_deadlines || []
    console.log('Raw upcoming deadlines:', rawDeadlines)
    
    upcomingDeadlines.value = rawDeadlines.map(drive => {
      const daysLeft = calculateDaysLeft(drive.deadline)
      return {
        id: drive.id,
        company_name: drive.company_name || 'Unknown',
        drive_name: drive.drive_name || 'Unnamed Drive',
        deadline: drive.deadline,
        days_left: daysLeft
      }
    })
    
    console.log('Processed upcoming deadlines:', upcomingDeadlines.value)
    
    // Process recent applications
    recentApplications.value = (response.data.recent_applications || []).map(app => ({
      id: app.id,
      company_name: app.company_name || 'Unknown',
      drive_name: app.drive_name || 'Unnamed Drive',
      status: app.status || 'applied',
      applied_at: app.applied_at
    }))
    
    upcomingInterviews.value = response.data.upcoming_interviews || []
    
  } catch (err) {
    console.error('Error fetching dashboard:', err)
    error.value = err.response?.data?.message || 'Failed to load dashboard'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
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
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stat-card .card-body {
  padding: 1.25rem;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #495057;
}

.table td {
  vertical-align: middle;
  padding: 1rem 0.75rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}

.btn-outline-primary {
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-outline-primary:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
}

.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 15px rgba(0,0,0,0.05);
}

.card.border-warning {
  border: 2px solid #ffc107 !important;
}
</style>