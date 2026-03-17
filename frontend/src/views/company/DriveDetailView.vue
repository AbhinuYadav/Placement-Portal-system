<!-- frontend/src/views/company/DriveDetailView.vue -->
<template>
  <div class="drive-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Drive Details</h2>
      <div>
        <router-link to="/company/drives" class="btn btn-outline-secondary me-2">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Drives
        </router-link>
        <router-link 
          v-if="drive.status === 'pending' && canEdit"
          :to="`/company/drives/${drive.id}/edit`" 
          class="btn btn-warning me-2"
        >
          <i class="bi bi-pencil me-2"></i>
          Edit
        </router-link>
        <button class="btn btn-outline-primary" @click="refreshData">
          <i class="bi bi-arrow-repeat me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Status Banner -->
    <div v-if="drive.status === 'pending'" class="alert alert-warning mb-4">
      <i class="bi bi-clock-history me-2"></i>
      This drive is pending admin approval. Students cannot see it yet.
    </div>
    <div v-else-if="drive.status === 'approved'" class="alert alert-success mb-4">
      <i class="bi bi-check-circle-fill me-2"></i>
      This drive is approved and visible to students!
    </div>
    <div v-else-if="drive.status === 'rejected'" class="alert alert-danger mb-4">
      <i class="bi bi-x-circle-fill me-2"></i>
      This drive has been rejected by admin.
    </div>
    <div v-else-if="drive.status === 'closed'" class="alert alert-secondary mb-4">
      <i class="bi bi-lock-fill me-2"></i>
      This drive is closed. No more applications accepted.
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
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
          <div class="card-header bg-white">
            <h5 class="mb-0">Drive Information</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <tr>
                <th style="width: 40%;">Drive Name</th>
                <td>{{ drive.drive_name }}</td>
              </tr>
              <tr>
                <th>Job Title</th>
                <td>{{ drive.job_title }}</td>
              </tr>
              <tr>
                <th>Status</th>
                <td>
                  <span class="badge" :class="getStatusClass(drive.status)">
                    {{ drive.status }}
                  </span>
                </td>
              </tr>
              <tr>
                <th>Created On</th>
                <td>{{ formatDate(drive.created_at) }}</td>
              </tr>
              <tr v-if="drive.approved_at">
                <th>Approved On</th>
                <td>{{ formatDate(drive.approved_at) }}</td>
              </tr>
            </table>

            <h6 class="mt-4 mb-3">Eligibility Criteria</h6>
            <table class="table table-sm">
              <tr>
                <th>Min CGPA</th>
                <td>{{ drive.min_cgpa || 'Not specified' }}</td>
              </tr>
              <tr>
                <th>Allowed Branches</th>
                <td>{{ drive.allowed_branches || 'All' }}</td>
              </tr>
              <tr>
                <th>Additional Criteria</th>
                <td>{{ drive.eligibility_criteria || 'None' }}</td>
              </tr>
            </table>

            <h6 class="mt-4 mb-3">Important Dates</h6>
            <table class="table table-sm">
              <tr>
                <th>Application Deadline</th>
                <td>{{ formatDateTime(drive.application_deadline) }}</td>
              </tr>
              <tr>
                <th>Drive Date</th>
                <td>{{ formatDateTime(drive.drive_date) || 'To be announced' }}</td>
              </tr>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column - Job Description & Applications -->
      <div class="col-md-7 mb-4">
        <!-- Job Description -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">Job Description</h5>
          </div>
          <div class="card-body">
            <p class="mb-0" style="white-space: pre-line;">{{ drive.job_description || 'No description provided.' }}</p>
          </div>
        </div>

        <!-- Applications Summary -->
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-people me-2"></i>
              Applications ({{ applications.length }})
            </h5>
            <router-link 
              :to="`/company/applications?drive=${drive.id}`" 
              class="btn btn-sm btn-outline-success"
            >
              View All
            </router-link>
          </div>
          <div class="card-body">
            <!-- Stats Cards -->
            <div class="row g-2 mb-3">
              <div class="col-3">
                <div class="card bg-warning bg-opacity-10">
                  <div class="card-body text-center p-2">
                    <small class="text-muted">Applied</small>
                    <h5 class="mb-0">{{ stats.applied }}</h5>
                  </div>
                </div>
              </div>
              <div class="col-3">
                <div class="card bg-info bg-opacity-10">
                  <div class="card-body text-center p-2">
                    <small class="text-muted">Shortlisted</small>
                    <h5 class="mb-0">{{ stats.shortlisted }}</h5>
                  </div>
                </div>
              </div>
              <div class="col-3">
                <div class="card bg-success bg-opacity-10">
                  <div class="card-body text-center p-2">
                    <small class="text-muted">Selected</small>
                    <h5 class="mb-0">{{ stats.selected }}</h5>
                  </div>
                </div>
              </div>
              <div class="col-3">
                <div class="card bg-danger bg-opacity-10">
                  <div class="card-body text-center p-2">
                    <small class="text-muted">Rejected</small>
                    <h5 class="mb-0">{{ stats.rejected }}</h5>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Applications Table -->
            <h6 class="mb-3">Recent Applications</h6>
            <div class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Roll No</th>
                    <th>CGPA</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in applications.slice(0, 5)" :key="app.id">
                    <td>{{ app.student_name }}</td>
                    <td>{{ app.student_roll }}</td>
                    <td>
                      <span class="badge" :class="getCGPAClass(app.student_cgpa)">
                        {{ app.student_cgpa }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="getStatusClass(app.status)">
                        {{ app.status }}
                      </span>
                    </td>
                    <td>
                      <router-link 
                        :to="`/company/applications/${app.id}`" 
                        class="btn btn-sm btn-outline-primary"
                      >
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const drive = ref({})
const applications = ref([])
const companyProfile = ref({})

// Computed
const canEdit = computed(() => {
  return companyProfile.value?.approval_status === 'approved' && !companyProfile.value?.is_blacklisted
})

const stats = computed(() => {
  const s = { applied: 0, shortlisted: 0, selected: 0, rejected: 0 }
  applications.value.forEach(app => {
    if (app.status === 'applied') s.applied++
    else if (app.status === 'shortlisted') s.shortlisted++
    else if (app.status === 'selected') s.selected++
    else if (app.status === 'rejected') s.rejected++
  })
  return s
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

const getStatusClass = (status) => {
  if (!status) return 'bg-secondary'
  switch(status.toLowerCase()) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    case 'closed': return 'bg-secondary'
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    default: return 'bg-secondary'
  }
}

const getCGPAClass = (cgpa) => {
  if (!cgpa) return 'bg-secondary'
  if (cgpa >= 9.0) return 'bg-success'
  if (cgpa >= 8.0) return 'bg-info'
  if (cgpa >= 7.0) return 'bg-warning text-dark'
  if (cgpa >= 6.0) return 'bg-secondary'
  return 'bg-danger'
}

// Fetch company profile
const fetchCompanyProfile = async () => {
  try {
    const response = await companyAPI.getProfile()
    companyProfile.value = response.data.profile || {}
  } catch (err) {
    console.error('Error fetching company profile:', err)
  }
}

// Fetch drive details
const fetchDriveDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await companyAPI.getDrive(driveId)
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

const refreshData = () => {
  fetchDriveDetails()
}

onMounted(() => {
  fetchCompanyProfile()
  fetchDriveDetails()
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

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  border-radius: 1rem 1rem 0 0 !important;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}
</style>