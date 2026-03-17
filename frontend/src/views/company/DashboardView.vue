<!-- frontend/src/views/company/DashboardView.vue -->
<template>
  <div class="dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Company Dashboard</h2>
      <div class="d-flex align-items-center">
        <span class="badge me-2" :class="statusBadgeClass">
          {{ statusText }}
        </span>
        <span class="text-muted">
          <i class="bi bi-building me-1"></i>
          {{ companyName }}
        </span>
      </div>
    </div>

    <!-- Blacklisted Warning -->
    <div v-if="isBlacklisted" class="alert alert-danger mb-4">
      <i class="bi bi-lock-fill me-2"></i>
      <strong>Account Blacklisted:</strong> Your company has been blacklisted. You cannot create new drives or manage applications. Please contact the administrator.
    </div>

    <!-- Pending Approval Warning -->
    <div v-else-if="!isApproved" class="alert alert-warning mb-4">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>Pending Approval:</strong> Your company is awaiting admin approval. You can create drives, but they will need admin approval before students can see them.
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
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
          <div class="card stat-card" :class="isBlacklisted ? 'bg-secondary' : 'bg-primary'" :style="cardStyle">
            <div class="card-body text-white">
              <h6 class="card-title text-white-50">Total Drives</h6>
              <h2 class="mb-0">{{ stats.total_drives || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card" :class="isBlacklisted ? 'bg-secondary' : 'bg-warning'" :style="cardStyle">
            <div class="card-body text-white">
              <h6 class="card-title text-white-50">Pending Drives</h6>
              <h2 class="mb-0">{{ stats.pending_drives || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card" :class="isBlacklisted ? 'bg-secondary' : 'bg-info'" :style="cardStyle">
            <div class="card-body text-white">
              <h6 class="card-title text-white-50">Total Applications</h6>
              <h2 class="mb-0">{{ stats.total_applications || 0 }}</h2>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card stat-card" :class="isBlacklisted ? 'bg-secondary' : 'bg-success'" :style="cardStyle">
            <div class="card-body text-white">
              <h6 class="card-title text-white-50">Shortlisted</h6>
              <h2 class="mb-0">{{ stats.shortlisted || 0 }}</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title mb-3">Quick Actions</h5>
              <div class="d-flex gap-2">
                <router-link to="/company/drives/create" class="btn btn-success" :class="{ 'disabled': !canCreateDrive }">
                  <i class="bi bi-plus-circle me-2"></i>
                  Create New Drive
                </router-link>
                <router-link to="/company/applications" class="btn btn-outline-success">
                  <i class="bi bi-file-text me-2"></i>
                  View Applications
                </router-link>
                <router-link to="/company/profile" class="btn btn-outline-success">
                  <i class="bi bi-pencil me-2"></i>
                  Update Profile
                </router-link>
              </div>
              <div v-if="!canCreateDrive" class="text-danger small mt-2">
                <i class="bi bi-info-circle me-1"></i>
                {{ createDriveDisabledReason }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Drives -->
      <div class="row mb-4">
        <div class="col-md-12">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Recent Drives</h5>
              <router-link to="/company/drives" class="btn btn-sm btn-outline-success">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Drive Name</th>
                      <th>Job Title</th>
                      <th>Deadline</th>
                      <th>Status</th>
                      <th>Applications</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="drive in recentDrives" :key="drive.id">
                      <td>{{ drive.drive_name }}</td>
                      <td>{{ drive.job_title }}</td>
                      <td>{{ formatDate(drive.application_deadline) }}</td>
                      <td>
                        <span class="badge" :class="getDriveStatusClass(drive.status)">
                          {{ drive.status }}
                        </span>
                      </td>
                      <td>{{ drive.application_count || 0 }}</td>
                      <td>
                        <router-link :to="`/company/drives/${drive.id}`" class="btn btn-sm btn-outline-primary">
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
              <h5 class="mb-0">Recent Applications</h5>
              <router-link to="/company/applications" class="btn btn-sm btn-outline-success">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Student</th>
                      <th>Drive</th>
                      <th>Applied On</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in recentApplications" :key="app.id">
                      <td>{{ app.student_name }}</td>
                      <td>{{ app.drive_name }}</td>
                      <td>{{ formatDate(app.applied_at) }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(app.status)">
                          {{ app.status }}
                        </span>
                      </td>
                      <td>
                        <router-link :to="`/company/applications/${app.id}`" class="btn btn-sm btn-outline-primary">
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
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const authStore = useAuthStore()
const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const companyProfile = ref({})
const stats = ref({})
const recentDrives = ref([])
const recentApplications = ref([])

// Computed properties for company status
const isBlacklisted = computed(() => companyProfile.value?.is_blacklisted || false)
const isApproved = computed(() => companyProfile.value?.approval_status === 'approved')
const companyName = computed(() => companyProfile.value?.company_name || 'Company')
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
const cardStyle = computed(() => {
  return isBlacklisted.value ? { opacity: '0.7' } : {}
})
const canCreateDrive = computed(() => {
  return !isBlacklisted.value && isApproved.value
})
const createDriveDisabledReason = computed(() => {
  if (isBlacklisted.value) return 'Cannot create drives: Account is blacklisted'
  if (!isApproved.value) return 'Cannot create drives: Company pending approval'
  return ''
})

// Helper Functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getDriveStatusClass = (status) => {
  switch(status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    case 'closed': return 'bg-secondary'
    default: return 'bg-secondary'
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

// Fetch Dashboard Data
const fetchDashboard = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Fetch company profile first
    const profileResponse = await companyAPI.getProfile()
    companyProfile.value = profileResponse.data.profile || {}
    
    // Then fetch dashboard data
    const response = await companyAPI.getDashboard()
    console.log('Dashboard data:', response.data)
    
    stats.value = response.data.statistics || {}
    recentDrives.value = response.data.recent_drives || []
    recentApplications.value = response.data.recent_applications || []
    
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
  background: linear-gradient(135deg, #198754 0%, #20c997 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}

.btn.disabled {
  pointer-events: none;
  opacity: 0.5;
}
</style>