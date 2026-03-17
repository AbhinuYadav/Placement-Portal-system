<!-- frontend/src/views/company/ApplicationDetailView.vue -->
<template>
  <div class="application-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Application Details</h2>
      <div>
        <router-link to="/company/applications" class="btn btn-outline-secondary me-2">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Applications
        </router-link>
        <button class="btn btn-outline-success" @click="refreshData">
          <i class="bi bi-arrow-repeat me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Status Warning -->
    <div v-if="!isApproved" class="alert alert-warning mb-4">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>Pending Approval:</strong> Your company is awaiting admin approval. You cannot update application status.
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
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
            <h5 class="mb-0">Application Information</h5>
            <span class="badge fs-6 px-3 py-2" :class="getStatusClass(application.status)">
              {{ formatStatus(application.status) }}
            </span>
          </div>
          <div class="card-body">
            <table class="table">
              <tbody> <!-- ✅ Added tbody -->
                <tr>
                  <th style="width: 40%;">Student</th>
                  <td>{{ application.student_name }}</td>
                </tr>
                <tr>
                  <th>Roll Number</th>
                  <td>{{ application.student_roll }}</td>
                </tr>
                <tr>
                  <th>Branch</th>
                  <td>{{ application.student_branch }}</td>
                </tr>
                <tr>
                  <th>CGPA</th>
                  <td>
                    <span class="badge" :class="getCGPAClass(application.student_cgpa)">
                      {{ application.student_cgpa }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <th>Email</th>
                  <td>
                    <a :href="'mailto:' + application.student_email">{{ application.student_email }}</a>
                  </td>
                </tr>
                <tr>
                  <th>Phone</th>
                  <td>{{ application.student_phone || 'N/A' }}</td>
                </tr>
                <tr>
                  <th>Applied On</th>
                  <td>{{ formatDateTime(application.applied_at) }}</td>
                </tr>
              </tbody> <!-- ✅ Added tbody -->
            </table>

            <!-- Action Buttons - Only if approved -->
            <div v-if="canManage" class="d-grid gap-2 mt-4">
              <template v-if="application.status === 'applied'">
                <button class="btn btn-info text-white btn-lg" @click="updateStatus('shortlisted')" :disabled="processingAction">
                  <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-star me-2"></i>
                  Shortlist Candidate
                </button>
                <button class="btn btn-danger btn-lg" @click="rejectApplication" :disabled="processingAction">
                  <i class="bi bi-x-lg me-2"></i>
                  Reject Application
                </button>
              </template>

              <template v-if="application.status === 'shortlisted'">
                <button class="btn btn-success btn-lg" @click="updateStatus('selected')" :disabled="processingAction">
                  <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-lg me-2"></i>
                  Select Candidate
                </button>
                <button class="btn btn-danger btn-lg" @click="rejectApplication" :disabled="processingAction">
                  <i class="bi bi-x-lg me-2"></i>
                  Reject Application
                </button>
                <button class="btn btn-warning btn-lg" @click="showScheduleModal" :disabled="processingAction">
                  <i class="bi bi-calendar-plus me-2"></i>
                  Schedule Interview
                </button>
              </template>

              <template v-if="application.status === 'selected'">
                <button class="btn btn-success btn-lg" disabled>
                  <i class="bi bi-check-circle me-2"></i>
                  Candidate Selected
                </button>
              </template>
            </div>

            <!-- Read-only message for pending companies -->
            <div v-else-if="!isApproved" class="alert alert-warning mt-4">
              <i class="bi bi-info-circle me-2"></i>
              Your company is pending approval. You can view but not update applications.
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Additional Info -->
      <div class="col-md-7 mb-4">
        <!-- Drive Details -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">Drive Details</h5>
          </div>
          <div class="card-body">
            <table class="table">
              <tbody> <!-- ✅ Added tbody -->
                <tr>
                  <th style="width: 30%;">Drive Name</th>
                  <td>{{ application.drive_name }}</td>
                </tr>
                <tr>
                  <th>Job Title</th>
                  <td>{{ application.job_title }}</td>
                </tr>
                <tr>
                  <th>Company</th>
                  <td>{{ application.company_name }}</td>
                </tr>
                <tr>
                  <th>Deadline</th>
                  <td>{{ formatDate(application.drive_deadline) }}</td>
                </tr>
              </tbody> <!-- ✅ Added tbody -->
            </table>
          </div>
        </div>

        <!-- Interview Details -->
        <div class="card mb-4">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Interview Details</h5>
            <button 
              v-if="application.status === 'shortlisted' && !application.interview_date && canManage"
              class="btn btn-warning btn-sm"
              @click="showScheduleModal"
            >
              <i class="bi bi-calendar-plus me-1"></i>
              Schedule
            </button>
          </div>
          <div class="card-body">
            <div v-if="application.interview_date" class="row">
              <div class="col-md-6">
                <div class="border rounded p-3">
                  <small class="text-muted">Date & Time</small>
                  <p class="mb-0 fw-bold">{{ formatDateTime(application.interview_date) }}</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="border rounded p-3">
                  <small class="text-muted">Mode</small>
                  <p class="mb-0 fw-bold">{{ application.interview_mode || 'Online' }}</p>
                </div>
              </div>
              <div v-if="application.interview_notes" class="col-12 mt-3">
                <div class="border rounded p-3">
                  <small class="text-muted">Notes</small>
                  <p class="mb-0">{{ application.interview_notes }}</p>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-3">
              <i class="bi bi-calendar-x fs-1 d-block mb-3"></i>
              <p class="mb-0">No interview scheduled yet</p>
            </div>
          </div>
        </div>

        <!-- Rejection Reason -->
        <div v-if="application.status === 'rejected' && application.rejection_reason" class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0 text-danger">Rejection Reason</h5>
          </div>
          <div class="card-body">
            <p class="mb-0">{{ application.rejection_reason }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule Interview Modal -->
    <div class="modal fade" id="scheduleModal" tabindex="-1" ref="scheduleModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-calendar-plus me-2 text-warning"></i>
              Schedule Interview
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Schedule interview for <strong>{{ application.student_name }}</strong></p>
            
            <div class="mb-3">
              <label class="form-label">Interview Date & Time</label>
              <input type="datetime-local" class="form-control" v-model="interviewData.date" required>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Interview Mode</label>
              <select class="form-select" v-model="interviewData.mode">
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Notes / Instructions</label>
              <textarea class="form-control" rows="3" v-model="interviewData.notes"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-warning" @click="confirmScheduleInterview" :disabled="!interviewData.date || scheduling">
              <span v-if="scheduling" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-check-lg me-2"></i>
              Schedule Interview
            </button>
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

const applicationId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const processingAction = ref(false)
const scheduling = ref(false)
const application = ref({})
const companyProfile = ref({})

// Modal
const scheduleModal = ref(null)
let modalInstance = null
const interviewData = ref({
  date: '',
  mode: 'online',
  notes: ''
})

// Computed
const isApproved = computed(() => companyProfile.value?.approval_status === 'approved')
const isBlacklisted = computed(() => companyProfile.value?.is_blacklisted || false)
const canManage = computed(() => isApproved.value && !isBlacklisted.value)

// Helper Functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
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

// Fetch application details
const fetchApplicationDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching application details for ID: ${applicationId}`)
    const response = await companyAPI.getApplication(applicationId)
    console.log('Application details response:', response.data)
    
    application.value = response.data.application || {}
  } catch (err) {
    console.error('Error fetching application details:', err)
    error.value = err.response?.data?.message || 'Failed to load application'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchApplicationDetails()
}

// Update status
const updateStatus = async (newStatus) => {
  if (!canManage.value) {
    messageStore.updateErrorMessages('You cannot update applications at this time.')
    return
  }
  
  processingAction.value = true
  try {
    if (newStatus === 'shortlisted') {
      await companyAPI.shortlistApplication(applicationId)
      messageStore.updateSuccessMessages('Candidate shortlisted successfully')
    } else if (newStatus === 'selected') {
      await companyAPI.selectApplication(applicationId)
      messageStore.updateSuccessMessages('Candidate selected successfully')
    }
    await fetchApplicationDetails()
  } catch (err) {
    console.error('Update status error:', err)
    messageStore.updateErrorMessages(err.response?.data?.message || `Failed to ${newStatus} application`)
  } finally {
    processingAction.value = false
  }
}

// Reject application
const rejectApplication = async () => {
  if (!canManage.value) {
    messageStore.updateErrorMessages('You cannot reject applications at this time.')
    return
  }
  
  const reason = prompt('Please enter rejection reason:')
  if (!reason || !reason.trim()) return
  
  processingAction.value = true
  try {
    await companyAPI.rejectApplication(applicationId, { reason })
    messageStore.updateSuccessMessages('Application rejected')
    await fetchApplicationDetails()
  } catch (err) {
    console.error('Reject error:', err)
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to reject application')
  } finally {
    processingAction.value = false
  }
}

// ===== INTERVIEW SCHEDULING =====
const showScheduleModal = () => {
  interviewData.value = {
    date: '',
    mode: 'online',
    notes: ''
  }
  
  if (!modalInstance) {
    modalInstance = new bootstrap.Modal(scheduleModal.value)
  }
  modalInstance.show()
}

const confirmScheduleInterview = async () => {
  if (!interviewData.value.date) {
    messageStore.updateErrorMessages('Please select interview date and time')
    return
  }
  
  scheduling.value = true
  try {
    // ✅ Send data with the correct field name expected by backend
    const payload = {
      interview_date: interviewData.value.date,  // Backend expects 'interview_date', not 'date'
      mode: interviewData.value.mode,
      notes: interviewData.value.notes
    }
    
    console.log('Sending interview payload:', payload)
    
    await companyAPI.scheduleInterview(applicationId, payload)
    messageStore.updateSuccessMessages('Interview scheduled successfully')
    modalInstance.hide()
    await fetchApplicationDetails()
  } catch (err) {
    console.error('Schedule error:', err.response?.data)
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to schedule interview')
  } finally {
    scheduling.value = false
  }
}

// Initial load
onMounted(() => {
  fetchCompanyProfile()
  fetchApplicationDetails()
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

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}

.btn-lg {
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.modal-content {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.modal-header {
  border-bottom: 1px solid #eff2f5;
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid #eff2f5;
  padding: 1.5rem;
}
</style>