<!-- frontend/src/views/admin/DriveDetailView.vue -->
<template>
  <div class="drive-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Drive Details</h2>
      <div>
        <button class="btn btn-outline-secondary me-2" @click="goBack">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Drives
        </button>
        <button class="btn btn-outline-primary" @click="refreshData">
          <i class="bi bi-arrow-repeat me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading drive details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchDriveDetails">Retry</button>
    </div>

    <!-- Drive Details -->
    <div v-else class="row">
      <!-- Left Column - Drive Info -->
      <div class="col-md-5 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-briefcase me-2 text-primary"></i>
              Drive Information
            </h5>
            <span class="badge fs-6 px-3 py-2" :class="getStatusClass(drive)">
              {{ formatStatus(drive.status) }}
            </span>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="drive-icon bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 100px; height: 100px;">
                <i class="bi bi-briefcase-fill fs-1 text-primary"></i>
              </div>
              <h3>{{ drive.drive_name }}</h3>
              <p class="text-muted mb-0">Drive ID: #{{ drive.id }}</p>
            </div>

            <table class="table table-bordered">
              <tbody>
                <tr>
                  <th style="width: 40%; background-color: #f8f9fa;">Company</th>
                  <td>
                    <router-link :to="`/admin/companies/${drive.company_id}`" class="text-decoration-none fw-bold">
                      <i class="bi bi-building me-1"></i>
                      {{ drive.company_name }}
                    </router-link>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Job Title</th>
                  <td>{{ drive.job_title }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Created On</th>
                  <td>{{ formatDate(drive.created_at) }}</td>
                </tr>
                <tr v-if="drive.approved_at">
                  <th style="background-color: #f8f9fa;">Approved On</th>
                  <td>{{ formatDate(drive.approved_at) }}</td>
                </tr>
                <tr v-if="drive.approved_by">
                  <th style="background-color: #f8f9fa;">Approved By</th>
                  <td>{{ drive.approved_by_name || 'Admin' }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 mt-4">
              <template v-if="drive.status === 'pending'">
                <button class="btn btn-success btn-lg" @click="approveDrive" :disabled="processingAction">
                  <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-lg me-2"></i>
                  Approve Drive
                </button>
                <button class="btn btn-danger btn-lg" @click="rejectDrive" :disabled="processingAction">
                  <i class="bi bi-x-lg me-2"></i>
                  Reject Drive
                </button>
              </template>
              
              <button v-if="drive.status === 'approved'" class="btn btn-warning btn-lg" @click="closeDrive" :disabled="processingAction">
                <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-stop-circle me-2"></i>
                Close Drive
              </button>

              <button v-if="drive.status === 'closed'" class="btn btn-secondary btn-lg" disabled>
                <i class="bi bi-lock me-2"></i>
                Drive Closed
              </button>

              <button v-if="drive.status === 'rejected'" class="btn btn-secondary btn-lg" disabled>
                <i class="bi bi-x-circle me-2"></i>
                Drive Rejected
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Additional Info -->
      <div class="col-md-7 mb-4">
        <!-- Job Description -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-file-text me-2 text-info"></i>
              Job Description
            </h5>
          </div>
          <div class="card-body">
            <p class="mb-0" style="white-space: pre-line;">{{ drive.job_description || 'No description provided.' }}</p>
          </div>
        </div>

        <!-- Eligibility Criteria -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-check-circle me-2 text-success"></i>
              Eligibility Criteria
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="border rounded p-3 mb-3">
                  <small class="text-muted d-block mb-1">Minimum CGPA</small>
                  <span class="badge bg-info fs-6 px-3 py-2">{{ drive.min_cgpa || 'Not specified' }}</span>
                </div>
              </div>
              <div class="col-md-6">
                <div class="border rounded p-3 mb-3">
                  <small class="text-muted d-block mb-1">Application Deadline</small>
                  <span class="badge bg-warning text-dark fs-6 px-3 py-2">
                    <i class="bi bi-calendar me-1"></i>
                    {{ formatDate(drive.application_deadline) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="border rounded p-3">
              <small class="text-muted d-block mb-2">Allowed Branches</small>
              <div v-if="drive.allowed_branches">
                <span 
                  v-for="branch in drive.allowed_branches.split(',').map(b => b.trim())" 
                  :key="branch" 
                  class="badge bg-secondary me-2 mb-2 fs-6 px-3 py-2"
                >
                  {{ branch }}
                </span>
              </div>
              <span v-else class="text-muted">All branches are eligible</span>
            </div>

            <div v-if="drive.eligibility_criteria" class="mt-3 border rounded p-3">
              <small class="text-muted d-block mb-2">Additional Criteria</small>
              <p class="mb-0">{{ drive.eligibility_criteria }}</p>
            </div>
          </div>
        </div>

        <!-- Drive Schedule -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-calendar-event me-2 text-warning"></i>
              Drive Schedule
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="border rounded p-3 text-center">
                  <i class="bi bi-calendar-check fs-2 text-primary mb-2"></i>
                  <h6>Drive Date</h6>
                  <p class="mb-0 fw-bold">{{ formatDate(drive.drive_date) || 'To be announced' }}</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="border rounded p-3 text-center">
                  <i class="bi bi-clock-history fs-2 text-warning mb-2"></i>
                  <h6>Days Remaining</h6>
                  <p class="mb-0 fw-bold">{{ daysRemaining }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Applications Summary -->
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-people me-2 text-success"></i>
              Applications Summary
            </h5>
            <span class="badge bg-primary fs-6 px-3 py-2">Total: {{ applications.length }}</span>
          </div>
          <div class="card-body">
            <div v-if="applications.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-inbox fs-1 d-block mb-3"></i>
              <p class="mb-0">No applications received yet</p>
            </div>
            <div v-else>
              <!-- Stats Cards -->
              <div class="row g-3 mb-4">
                <div class="col-3">
                  <div class="card bg-warning bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Applied</div>
                      <div class="h4 mb-0">{{ applicationStats.applied }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-info bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Shortlisted</div>
                      <div class="h4 mb-0">{{ applicationStats.shortlisted }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-success bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Selected</div>
                      <div class="h4 mb-0">{{ applicationStats.selected }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-danger bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Rejected</div>
                      <div class="h4 mb-0">{{ applicationStats.rejected }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent Applications Table -->
              <h6 class="mb-3">Recent Applications</h6>
              <div class="table-responsive">
                <table class="table table-hover table-sm">
                  <thead class="table-light">
                    <tr>
                      <th>Student</th>
                      <th>Roll No</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Status</th>
                      <th>Applied</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in applications.slice(0, 5)" :key="app.id">
                      <td>
                        <i class="bi bi-person-circle me-1"></i>
                        {{ app.student_name }}
                      </td>
                      <td>{{ app.student_roll }}</td>
                      <td>{{ app.student_branch }}</td>
                      <td>
                        <span class="badge" :class="getCGPAClass(app.student_cgpa)">
                          {{ app.student_cgpa }}
                        </span>
                      </td>
                      <td>
                        <span class="badge" :class="getApplicationStatusClass(app.status)">
                          {{ app.status }}
                        </span>
                      </td>
                      <td>{{ formatDate(app.applied_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="applications.length > 5" class="text-center mt-3">
                <button class="btn btn-outline-primary btn-sm">
                  View All {{ applications.length }} Applications
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { adminAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const processingAction = ref(false)
const drive = ref({})
const applications = ref([])

// Computed
const applicationStats = computed(() => {
  const stats = { applied: 0, shortlisted: 0, selected: 0, rejected: 0 }
  applications.value.forEach(app => {
    if (app.status === 'applied') stats.applied++
    else if (app.status === 'shortlisted') stats.shortlisted++
    else if (app.status === 'selected') stats.selected++
    else if (app.status === 'rejected') stats.rejected++
  })
  return stats
})

const daysRemaining = computed(() => {
  if (!drive.value.application_deadline) return 'No deadline'
  
  const deadline = new Date(drive.value.application_deadline)
  const today = new Date()
  const diffTime = deadline - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'Expired'
  if (diffDays === 0) return 'Today'
  return `${diffDays} days left`
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

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const getStatusClass = (drive) => {
  switch(drive.status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    case 'closed': return 'bg-secondary'
    default: return 'bg-secondary'
  }
}

const getApplicationStatusClass = (status) => {
  switch(status?.toLowerCase()) {
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    case 'rejected': return 'bg-danger text-white'
    default: return 'bg-secondary text-white'
  }
}

const getCGPAClass = (cgpa) => {
  if (cgpa >= 9.0) return 'bg-success'
  if (cgpa >= 8.0) return 'bg-info'
  if (cgpa >= 7.0) return 'bg-warning text-dark'
  if (cgpa >= 6.0) return 'bg-secondary'
  return 'bg-danger'
}

// Fetch Drive Details
const fetchDriveDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching drive details for ID: ${driveId}`)
    const response = await adminAPI.getDriveDetails(driveId)
    console.log('Drive details response:', response.data)
    
    drive.value = response.data.drive || {}
    applications.value = response.data.applications || []
  } catch (err) {
    console.error('Error fetching drive details:', err)
    error.value = err.response?.data?.message || 'Failed to load drive details'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Refresh Data
const refreshData = () => {
  fetchDriveDetails()
}

// Actions
const approveDrive = async () => {
  if (!confirm('Are you sure you want to approve this drive?')) return
  
  processingAction.value = true
  try {
    await adminAPI.approveDrive(driveId)
    messageStore.updateSuccessMessages('Drive approved successfully')
    await fetchDriveDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to approve drive')
  } finally {
    processingAction.value = false
  }
}

const rejectDrive = async () => {
  if (!confirm('Are you sure you want to reject this drive?')) return
  
  processingAction.value = true
  try {
    await adminAPI.rejectDrive(driveId)
    messageStore.updateSuccessMessages('Drive rejected')
    await fetchDriveDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to reject drive')
  } finally {
    processingAction.value = false
  }
}

const closeDrive = async () => {
  if (!confirm('Are you sure you want to close this drive?')) return
  
  processingAction.value = true
  try {
    await adminAPI.closeDrive(driveId)
    messageStore.updateSuccessMessages('Drive closed')
    await fetchDriveDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to close drive')
  } finally {
    processingAction.value = false
  }
}

const goBack = () => {
  router.push('/admin/drives')
}

// Initial load
onMounted(() => {
  fetchDriveDetails()
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

.drive-icon {
  background: linear-gradient(135deg, #e9ecef, #dee2e6);
  border: 3px solid #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 15px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  border-radius: 1rem 1rem 0 0 !important;
  padding: 1rem 1.5rem;
}

.badge {
  font-weight: 500;
  border-radius: 2rem;
}

.btn {
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.btn-success {
  background: linear-gradient(135deg, #28a745, #20c997);
  border: none;
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #fd7e14);
  border: none;
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  border: none;
  color: #212529;
}

.border.rounded {
  border-color: #e9ecef !important;
}
</style>