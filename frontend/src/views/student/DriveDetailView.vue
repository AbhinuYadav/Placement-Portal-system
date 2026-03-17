<!-- frontend/src/views/student/DriveDetailView.vue -->
<template>
  <div class="drive-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Drive Details</h2>
      <div>
        <router-link to="/student/drives" class="btn btn-outline-secondary me-2">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Drives
        </router-link>
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
            <span class="badge fs-6 px-3 py-2" :class="getStatusClass(drive.status)">
              {{ drive.status }}
            </span>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="drive-icon bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 100px; height: 100px;">
                <i class="bi bi-building fs-1 text-primary"></i>
              </div>
              <h3>{{ drive.drive_name }}</h3>
              <h5 class="text-primary">{{ drive.company_name }}</h5>
            </div>

            <table class="table table-bordered">
              <tbody>
                <tr>
                  <th style="width: 40%; background-color: #f8f9fa;">Job Title</th>
                  <td>{{ drive.job_title }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Application Deadline</th>
                  <td>
                    <span class="badge" :class="getDeadlineClass(drive)">
                      {{ formatDateTime(drive.application_deadline) }}
                      ({{ getDaysLeft(drive) }})
                    </span>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Drive Date</th>
                  <td>{{ formatDateTime(drive.drive_date) || 'To be announced' }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Company</th>
                  <td>
                    <strong>{{ drive.company_name }}</strong>
                    <p v-if="drive.company" class="small text-muted mb-0 mt-1">
                      {{ drive.company.industry }} • {{ drive.company.location }}
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- Eligibility Status Card - Using backend data -->
            <div class="card mt-3" :class="eligibilityCardClass">
              <div class="card-body">
                <h6 class="card-title">Your Eligibility Status</h6>
                <div class="d-flex justify-content-between mb-2">
                  <span>CGPA ({{ studentProfile.cgpa }}) vs Required ({{ drive.min_cgpa || 'No minimum' }})</span>
                  <span :class="drive.eligibility?.cgpa_eligible ? 'text-success' : 'text-danger'">
                    <i :class="drive.eligibility?.cgpa_eligible ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                    {{ drive.eligibility?.cgpa_eligible ? 'Eligible' : 'Not Eligible' }}
                  </span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                  <span>Branch ({{ studentProfile.branch }})</span>
                  <span :class="drive.eligibility?.branch_eligible ? 'text-success' : 'text-danger'">
                    <i :class="drive.eligibility?.branch_eligible ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                    {{ drive.eligibility?.branch_eligible ? 'Eligible' : 'Not Eligible' }}
                  </span>
                </div>
                <div class="d-flex justify-content-between">
                  <span>Deadline Status</span>
                  <span :class="drive.eligibility?.deadline_active ? 'text-success' : 'text-danger'">
                    <i :class="drive.eligibility?.deadline_active ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                    {{ drive.eligibility?.deadline_active ? 'Active' : 'Passed' }}
                  </span>
                </div>
                <div v-if="drive.allowed_branches" class="small text-muted mt-2">
                  <i class="bi bi-people me-1"></i>
                  Allowed Branches: {{ drive.allowed_branches }}
                </div>
              </div>
            </div>

            <!-- Action Button -->
            <div class="d-grid gap-2 mt-4">
              <button 
                v-if="!drive.already_applied && drive.eligibility?.is_eligible"
                class="btn btn-success btn-lg"
                @click="applyToDrive"
                :disabled="applying"
              >
                <span v-if="applying" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-send me-2"></i>
                Apply Now
              </button>
              
              <button 
                v-else-if="drive.already_applied"
                class="btn btn-warning btn-lg"
                disabled
              >
                <i class="bi bi-check-circle me-2"></i>
                Already Applied
              </button>
              
              <button 
                v-else-if="!drive.eligibility?.deadline_active"
                class="btn btn-secondary btn-lg"
                disabled
              >
                <i class="bi bi-clock-history me-2"></i>
                Deadline Passed
              </button>
              
              <button 
                v-else
                class="btn btn-secondary btn-lg"
                disabled
              >
                <i class="bi bi-lock me-2"></i>
                Not Eligible
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
                  <small class="text-muted d-block mb-1">Your CGPA</small>
                  <span class="badge" :class="drive.eligibility?.cgpa_eligible ? 'bg-success' : 'bg-danger'">
                    {{ studentProfile.cgpa }}
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
              
              <div class="mt-3">
                <small class="text-muted d-block mb-1">Your Branch</small>
                <span class="badge" :class="drive.eligibility?.branch_eligible ? 'bg-success' : 'bg-danger'">
                  {{ studentProfile.branch }}
                </span>
              </div>
            </div>

            <div v-if="drive.eligibility_criteria" class="mt-3 border rounded p-3">
              <small class="text-muted d-block mb-2">Additional Criteria</small>
              <p class="mb-0">{{ drive.eligibility_criteria }}</p>
            </div>
          </div>
        </div>

        <!-- Company Details -->
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-building me-2 text-primary"></i>
              About Company
            </h5>
          </div>
          <div class="card-body">
            <p class="mb-0">{{ drive.company?.description || 'No company description provided.' }}</p>
            
            <hr v-if="drive.company?.website || drive.company?.industry || drive.company?.location">
            
            <div v-if="drive.company?.website" class="mt-2">
              <i class="bi bi-globe me-2"></i>
              <a :href="drive.company.website" target="_blank">{{ drive.company.website }}</a>
            </div>
            <div v-if="drive.company?.industry" class="mt-1">
              <i class="bi bi-tag me-2"></i>
              Industry: {{ drive.company.industry }}
            </div>
            <div v-if="drive.company?.location" class="mt-1">
              <i class="bi bi-geo-alt me-2"></i>
              Location: {{ drive.company.location }}
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
import { studentAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const driveId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const applying = ref(false)
const drive = ref({})
const studentProfile = ref({})

// Computed
const eligibilityCardClass = computed(() => {
  if (drive.value.already_applied) return 'border-warning'
  if (drive.value.eligibility?.is_eligible) return 'border-success'
  return 'border-danger'
})

// Helper Functions
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
  switch(status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'closed': return 'bg-secondary'
    default: return 'bg-secondary'
  }
}

const getDaysLeft = (drive) => {
  if (!drive.application_deadline) return 'No deadline'
  
  const deadline = new Date(drive.application_deadline)
  const now = new Date()
  const diffTime = deadline - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'Expired'
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return '1 day left'
  return `${diffDays} days left`
}

const getDeadlineClass = (drive) => {
  if (!drive.application_deadline) return 'bg-secondary'
  
  const deadline = new Date(drive.application_deadline)
  const now = new Date()
  const diffDays = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return 'bg-danger'
  if (diffDays <= 3) return 'bg-warning text-dark'
  return 'bg-info'
}

// Fetch Student Profile
const fetchStudentProfile = async () => {
  try {
    const response = await studentAPI.getProfile()
    studentProfile.value = response.data.profile || {}
    console.log('Student profile loaded:', studentProfile.value)
  } catch (err) {
    console.error('Error fetching student profile:', err)
  }
}

// Fetch Drive Details
const fetchDriveDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching drive details for ID: ${driveId}`)
    const response = await studentAPI.getDrive(driveId)
    console.log('Drive details response:', response.data)
    
    drive.value = response.data.drive || {}
  } catch (err) {
    console.error('Error fetching drive details:', err)
    error.value = err.response?.data?.message || 'Failed to load drive details'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Apply to Drive
const applyToDrive = async () => {
  if (!drive.value.eligibility?.is_eligible) {
    messageStore.updateErrorMessages('You are not eligible for this drive')
    return
  }
  
  applying.value = true
  try {
    await studentAPI.applyToDrive(driveId)
    messageStore.updateSuccessMessages('Successfully applied to drive!')
    await fetchDriveDetails() // Refresh to update already_applied status
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to apply')
  } finally {
    applying.value = false
  }
}

const refreshData = () => {
  fetchDriveDetails()
}

onMounted(() => {
  fetchStudentProfile()
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

.btn-success {
  background: linear-gradient(135deg, #28a745, #20c997);
  border: none;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(40, 167, 69, 0.3);
}

.border-success {
  border: 2px solid #28a745 !important;
}

.border-warning {
  border: 2px solid #ffc107 !important;
}

.border-danger {
  border: 2px solid #dc3545 !important;
}
</style>