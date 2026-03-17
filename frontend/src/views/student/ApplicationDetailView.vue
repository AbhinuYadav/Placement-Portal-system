<!-- frontend/src/views/student/ApplicationDetailView.vue -->
<template>
  <div class="application-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Application Details</h2>
      <div>
        <router-link to="/student/applications" class="btn btn-outline-secondary me-2">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Applications
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
      <p class="mt-3 text-muted">Loading application details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchApplicationDetails">Retry</button>
    </div>

    <!-- Application Details -->
    <div v-else class="row">
      <!-- Left Column - Application Info -->
      <div class="col-md-5 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-file-text me-2 text-primary"></i>
              Application Information
            </h5>
            <span class="badge fs-6 px-3 py-2" :class="getStatusClass(application.status)">
              {{ formatStatus(application.status) }}
            </span>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="application-icon bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 100px; height: 100px;">
                <i class="bi bi-file-text-fill fs-1 text-primary"></i>
              </div>
              <h4>Application #{{ application.id }}</h4>
              <p class="text-muted">Applied on: {{ formatDateTime(application.applied_at) }}</p>
            </div>

            <table class="table table-bordered">
              <tbody>
                <tr>
                  <th style="width: 40%; background-color: #f8f9fa;">Company</th>
                  <td>
                    <strong>{{ application.company_name }}</strong>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Drive</th>
                  <td>{{ application.drive_name }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Job Title</th>
                  <td>{{ application.job_title }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Applied On</th>
                  <td>{{ formatDateTime(application.applied_at) }}</td>
                </tr>
                <tr v-if="application.updated_at">
                  <th style="background-color: #f8f9fa;">Last Updated</th>
                  <td>{{ formatDateTime(application.updated_at) }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Status Timeline -->
            <div class="mt-4">
              <h6 class="mb-3">Application Timeline</h6>
              <div class="timeline">
                <div class="timeline-item">
                  <div class="timeline-marker bg-success"></div>
                  <div class="timeline-content">
                    <p class="mb-0"><strong>Applied</strong></p>
                    <small class="text-muted">{{ formatDateTime(application.applied_at) }}</small>
                  </div>
                </div>
                
                <div v-if="application.shortlisted_at" class="timeline-item">
                  <div class="timeline-marker bg-info"></div>
                  <div class="timeline-content">
                    <p class="mb-0"><strong>Shortlisted</strong></p>
                    <small class="text-muted">{{ formatDateTime(application.shortlisted_at) }}</small>
                  </div>
                </div>
                
                <div v-if="application.interview_date" class="timeline-item">
                  <div class="timeline-marker bg-warning"></div>
                  <div class="timeline-content">
                    <p class="mb-0"><strong>Interview Scheduled</strong></p>
                    <small class="text-muted">{{ formatDateTime(application.interview_date) }}</small>
                    <p v-if="application.interview_notes" class="small text-muted mt-1">
                      <i class="bi bi-info-circle me-1"></i>
                      {{ application.interview_notes }}
                    </p>
                  </div>
                </div>
                
                <div v-if="application.selected_at" class="timeline-item">
                  <div class="timeline-marker bg-success"></div>
                  <div class="timeline-content">
                    <p class="mb-0"><strong>Selected</strong></p>
                    <small class="text-muted">{{ formatDateTime(application.selected_at) }}</small>
                  </div>
                </div>
                
                <div v-if="application.rejected_at" class="timeline-item">
                  <div class="timeline-marker bg-danger"></div>
                  <div class="timeline-content">
                    <p class="mb-0"><strong>Rejected</strong></p>
                    <small class="text-muted">{{ formatDateTime(application.rejected_at) }}</small>
                    <p v-if="application.rejection_reason" class="small text-danger mt-1">
                      <i class="bi bi-exclamation-circle me-1"></i>
                      {{ application.rejection_reason }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Withdraw Button (only if still applied) -->
            <div v-if="application.status === 'applied'" class="d-grid gap-2 mt-4">
              <button 
                class="btn btn-danger btn-lg"
                @click="withdrawApplication"
                :disabled="withdrawing"
              >
                <span v-if="withdrawing" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-trash me-2"></i>
                Withdraw Application
              </button>
              <p class="small text-muted text-center mt-2">
                <i class="bi bi-info-circle me-1"></i>
                You can withdraw your application until it's shortlisted by the company.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Additional Info -->
      <div class="col-md-7 mb-4">
        <!-- Drive Details -->
        <div class="card mb-4">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-briefcase me-2 text-success"></i>
              Drive Details
            </h5>
            <router-link :to="`/student/drives/${application.drive_id}`" class="btn btn-sm btn-outline-primary">
              View Drive
            </router-link>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <table class="table table-sm">
                  <tr>
                    <th>Drive Name</th>
                    <td>{{ application.drive_name }}</td>
                  </tr>
                  <tr>
                    <th>Job Title</th>
                    <td>{{ application.job_title }}</td>
                  </tr>
                  <tr>
                    <th>Min CGPA</th>
                    <td>{{ application.drive_min_cgpa || 'Not specified' }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <table class="table table-sm">
                  <tr>
                    <th>Deadline</th>
                    <td>{{ formatDate(application.drive_deadline) }}</td>
                  </tr>
                  <tr>
                    <th>Allowed Branches</th>
                    <td>{{ application.drive_branches || 'All' }}</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Company Details -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-building me-2 text-primary"></i>
              Company Details
            </h5>
          </div>
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="company-logo bg-light rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 60px; height: 60px;">
                <i class="bi bi-building fs-2 text-secondary"></i>
              </div>
              <div>
                <h5 class="mb-1">{{ application.company_name }}</h5>
                <p class="mb-0 text-muted small">{{ application.company_industry || 'Company' }}</p>
              </div>
            </div>
            
            <table class="table table-sm">
              <tr v-if="application.company_website">
                <th style="width: 30%;">Website</th>
                <td>
                  <a :href="application.company_website" target="_blank">{{ application.company_website }}</a>
                </td>
              </tr>
              <tr v-if="application.company_location">
                <th>Location</th>
                <td>{{ application.company_location }}</td>
              </tr>
              <tr v-if="application.hr_name">
                <th>HR Contact</th>
                <td>{{ application.hr_name }}</td>
              </tr>
              <tr v-if="application.hr_email">
                <th>HR Email</th>
                <td>
                  <a :href="'mailto:' + application.hr_email">{{ application.hr_email }}</a>
                </td>
              </tr>
            </table>
          </div>
        </div>

        <!-- Interview Details (if scheduled) -->
        <div v-if="application.interview_date" class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-calendar-event me-2 text-warning"></i>
              Interview Details
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="border rounded p-3">
                  <small class="text-muted d-block mb-1">Date & Time</small>
                  <p class="mb-0 fw-bold">{{ formatDateTime(application.interview_date) }}</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="border rounded p-3">
                  <small class="text-muted d-block mb-1">Mode</small>
                  <p class="mb-0 fw-bold">{{ application.interview_mode || 'Online' }}</p>
                </div>
              </div>
              <div v-if="application.interview_notes" class="col-12 mt-3">
                <div class="border rounded p-3">
                  <small class="text-muted d-block mb-1">Notes / Instructions</small>
                  <p class="mb-0">{{ application.interview_notes }}</p>
                </div>
              </div>
            </div>
            
            <!-- Countdown -->
            <div class="mt-3 p-3 bg-light rounded">
              <small class="text-muted d-block mb-1">Time until interview</small>
              <p class="mb-0 fw-bold" :class="getCountdownClass(application.interview_date)">
                {{ getCountdown(application.interview_date) }}
              </p>
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

const applicationId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const withdrawing = ref(false)
const application = ref({})

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

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  return status.charAt(0).toUpperCase() + status.slice(1)
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

const getCountdown = (interviewDate) => {
  if (!interviewDate) return ''
  
  const interview = new Date(interviewDate)
  const now = new Date()
  const diffMs = interview - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (diffMs < 0) return 'Interview passed'
  if (diffDays > 0) return `${diffDays} days ${diffHours} hours remaining`
  if (diffHours > 0) return `${diffHours} hours ${diffMins} minutes remaining`
  return `${diffMins} minutes remaining`
}

const getCountdownClass = (interviewDate) => {
  if (!interviewDate) return ''
  
  const interview = new Date(interviewDate)
  const now = new Date()
  const diffHours = (interview - now) / (1000 * 60 * 60)
  
  if (diffHours < 0) return 'text-danger'
  if (diffHours < 24) return 'text-warning'
  return 'text-success'
}

// Fetch Application Details
const fetchApplicationDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await studentAPI.getApplication(applicationId)
    application.value = response.data.application || {}
  } catch (err) {
    console.error('Error fetching application details:', err)
    error.value = err.response?.data?.message || 'Failed to load application details'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Withdraw Application
const withdrawApplication = async () => {
  if (!confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) return
  
  withdrawing.value = true
  try {
    await studentAPI.deleteApplication(applicationId)
    messageStore.updateSuccessMessages('Application withdrawn successfully')
    router.push('/student/applications')
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to withdraw application')
  } finally {
    withdrawing.value = false
  }
}

const refreshData = () => {
  fetchApplicationDetails()
}

onMounted(() => {
  fetchApplicationDetails()
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

.application-icon {
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
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  border-radius: 1rem 1rem 0 0 !important;
  padding: 1rem 1.5rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-marker {
  position: absolute;
  left: -30px;
  top: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.timeline-item:not(:last-child):before {
  content: '';
  position: absolute;
  left: -23px;
  top: 16px;
  bottom: -4px;
  width: 2px;
  background: #e9ecef;
}

.timeline-content {
  padding-bottom: 5px;
}

.company-logo {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 2px solid #dee2e6;
}
</style>