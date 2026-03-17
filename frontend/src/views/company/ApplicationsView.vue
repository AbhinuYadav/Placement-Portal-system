<!-- frontend/src/views/company/ApplicationsView.vue -->
<template>
  <div class="applications">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Applications Management</h2>
      <div class="d-flex">
        <select v-model="filters.drive_id" class="form-select me-2" style="width: 200px;">
          <option value="">All Drives</option>
          <option v-for="drive in drives" :key="drive.id" :value="drive.id">
            {{ drive.drive_name }}
          </option>
        </select>
        <select v-model="filters.status" class="form-select me-2" style="width: 150px;">
          <option value="">All Status</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
        </select>
        <input 
          v-model="filters.search"
          type="text" 
          class="form-control me-2" 
          placeholder="Search by student..."
          style="width: 200px;"
          @keyup.enter="fetchApplications"
        >
        <button class="btn btn-success" @click="fetchApplications" :disabled="loading">
          <i class="bi bi-search me-2"></i>Search
        </button>
        <button class="btn btn-outline-secondary ms-2" @click="resetFilters" title="Reset Filters">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
      </div>
    </div>

    <!-- Status Warning -->
    <div v-if="!isApproved" class="alert alert-warning mb-4">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>Pending Approval:</strong> Your company is awaiting admin approval. You can view applications but cannot update status.
    </div>
    <div v-if="isBlacklisted" class="alert alert-danger mb-4">
      <i class="bi bi-lock-fill me-2"></i>
      <strong>Account Blacklisted:</strong> You cannot manage applications.
    </div>

    <!-- Summary Stats -->
    <div class="row mb-4">
      <div class="col-md-2" v-for="stat in stats" :key="stat.label">
        <div class="card" :class="stat.bgClass">
          <div class="card-body py-3">
            <small class="text-muted">{{ stat.label }}</small>
            <h4 class="mb-0">{{ stat.count }}</h4>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading applications...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchApplications">Retry</button>
    </div>

    <!-- Applications Table -->
    <div v-else class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Roll No</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Drive</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td><span class="fw-medium">#{{ app.id }}</span></td>
                <td>
                  <i class="bi bi-person-circle me-1 text-primary"></i>
                  {{ app.student_name }}
                </td>
                <td>{{ app.student_roll }}</td>
                <td>{{ app.student_branch }}</td>
                <td>
                  <span class="badge" :class="getCGPAClass(app.student_cgpa)">
                    {{ app.student_cgpa }}
                  </span>
                </td>
                <td>{{ app.drive_name }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2 flex-wrap" style="min-width: 250px;">
                    <!-- Status Update Actions - Only if approved -->
                    <template v-if="canManage">
                      <button 
                        v-if="app.status === 'applied'"
                        class="btn btn-info text-white" 
                        style="min-width: 100px;"
                        @click="updateStatus(app.id, 'shortlisted')"
                        :disabled="processingId === app.id"
                      >
                        <span v-if="processingId === app.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-star me-1"></i>
                        Shortlist
                      </button>
                      
                      <button 
                        v-if="app.status === 'shortlisted'"
                        class="btn btn-success" 
                        style="min-width: 100px;"
                        @click="updateStatus(app.id, 'selected')"
                        :disabled="processingId === app.id"
                      >
                        <span v-if="processingId === app.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-check-lg me-1"></i>
                        Select
                      </button>

                      <button 
                        v-if="app.status === 'applied' || app.status === 'shortlisted'"
                        class="btn btn-danger" 
                        style="min-width: 100px;"
                        @click="rejectApplication(app)"
                        :disabled="processingId === app.id"
                      >
                        <i class="bi bi-x-lg me-1"></i>
                        Reject
                      </button>

                      <button 
                        v-if="app.status === 'shortlisted' && !app.interview_date"
                        class="btn btn-warning" 
                        style="min-width: 120px;"
                        @click="scheduleInterview(app)"
                        :disabled="processingId === app.id"
                      >
                        <i class="bi bi-calendar-plus me-1"></i>
                        Schedule
                      </button>
                    </template>

                    <!-- View Details Button -->
                    <button 
                      class="btn btn-outline-primary" 
                      style="min-width: 100px;"
                      @click="viewDetails(app.id)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      Details
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="applications.length === 0">
                <td colspan="9" class="text-center py-5">
                  <i class="bi bi-file-text fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No applications found</h5>
                  <p class="text-muted mb-0">Try adjusting your search or filter criteria</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.total > pagination.per_page" class="d-flex justify-content-between align-items-center mt-4">
          <div class="text-muted">
            Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} entries
          </div>
          <nav>
            <ul class="pagination mb-0">
              <li class="page-item" :class="{ disabled: pagination.current_page === 1 }">
                <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page - 1)">
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              <li 
                v-for="page in pagination.last_page" 
                :key="page"
                class="page-item" 
                :class="{ active: page === pagination.current_page }"
              >
                <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
              </li>
              <li class="page-item" :class="{ disabled: pagination.current_page === pagination.last_page }">
                <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page + 1)">
                  <i class="bi bi-chevron-right"></i>
                </a>
              </li>
            </ul>
          </nav>
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
            <p>Schedule interview for <strong>{{ selectedApplication?.student_name }}</strong></p>
            
            <div class="mb-3">
              <label for="interviewDate" class="form-label">Interview Date & Time</label>
              <input 
                type="datetime-local" 
                class="form-control" 
                id="interviewDate" 
                v-model="interviewData.date"
                required
              >
            </div>
            
            <div class="mb-3">
              <label for="interviewMode" class="form-label">Interview Mode</label>
              <select class="form-select" id="interviewMode" v-model="interviewData.mode">
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            
            <div class="mb-3">
              <label for="interviewNotes" class="form-label">Notes / Instructions</label>
              <textarea 
                class="form-control" 
                id="interviewNotes" 
                rows="3"
                v-model="interviewData.notes"
                placeholder="Enter any special instructions..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-warning" 
              @click="confirmScheduleInterview"
              :disabled="!interviewData.date || scheduling"
            >
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const router = useRouter()
const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const applications = ref([])
const drives = ref([])
const companyProfile = ref({})
const processingId = ref(null)
const scheduling = ref(false)

// Modal
const scheduleModal = ref(null)
let modalInstance = null
const selectedApplication = ref(null)
const interviewData = ref({
  date: '',
  mode: 'online',
  notes: ''
})

// Filters
const filters = reactive({
  drive_id: '',
  status: '',
  search: ''
})

// Pagination
const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 10,
  total: 0,
  from: 0,
  to: 0
})

// Computed
const isApproved = computed(() => companyProfile.value?.approval_status === 'approved')
const isBlacklisted = computed(() => companyProfile.value?.is_blacklisted || false)
const canManage = computed(() => isApproved.value && !isBlacklisted.value)

const stats = computed(() => {
  const total = applications.value.length
  const applied = applications.value.filter(a => a.status === 'applied').length
  const shortlisted = applications.value.filter(a => a.status === 'shortlisted').length
  const selected = applications.value.filter(a => a.status === 'selected').length
  const rejected = applications.value.filter(a => a.status === 'rejected').length
  
  return [
    { label: 'Total', count: total, bgClass: 'bg-light' },
    { label: 'Applied', count: applied, bgClass: 'bg-warning bg-opacity-10' },
    { label: 'Shortlisted', count: shortlisted, bgClass: 'bg-info bg-opacity-10' },
    { label: 'Selected', count: selected, bgClass: 'bg-success bg-opacity-10' },
    { label: 'Rejected', count: rejected, bgClass: 'bg-danger bg-opacity-10' }
  ]
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

// Fetch drives for filter
const fetchDrives = async () => {
  try {
    const response = await companyAPI.getDrives()
    drives.value = response.data.drives || []
  } catch (err) {
    console.error('Error fetching drives:', err)
  }
}

// Fetch applications
const fetchApplications = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page,
      per_page: pagination.per_page,
      ...filters
    }
    
    const response = await companyAPI.getApplications(params)
    applications.value = response.data.applications || []
    
    if (response.data.pagination) {
      pagination.current_page = response.data.pagination.current_page || 1
      pagination.last_page = response.data.pagination.last_page || 1
      pagination.total = response.data.pagination.total || 0
      pagination.from = response.data.pagination.from || 0
      pagination.to = response.data.pagination.to || 0
    }
  } catch (err) {
    console.error('Error fetching applications:', err)
    error.value = err.response?.data?.message || 'Failed to load applications'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Reset filters
const resetFilters = () => {
  filters.drive_id = ''
  filters.status = ''
  filters.search = ''
  fetchApplications(1)
}

// Change page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  fetchApplications(page)
}

// Update status
const updateStatus = async (id, newStatus) => {
  if (!canManage.value) {
    messageStore.updateErrorMessages('You cannot update applications at this time.')
    return
  }
  
  processingId.value = id
  try {
    if (newStatus === 'shortlisted') {
      await companyAPI.shortlistApplication(id)
    } else if (newStatus === 'selected') {
      await companyAPI.selectApplication(id)
    }
    messageStore.updateSuccessMessages(`Application ${newStatus} successfully`)
    await fetchApplications(pagination.current_page)
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || `Failed to ${newStatus} application`)
  } finally {
    processingId.value = null
  }
}

// Reject application
const rejectApplication = async (app) => {
  if (!canManage.value) {
    messageStore.updateErrorMessages('You cannot reject applications at this time.')
    return
  }
  
  const reason = prompt('Please enter rejection reason:')
  if (!reason) return
  
  processingId.value = app.id
  try {
    await companyAPI.rejectApplication(app.id, { reason })
    messageStore.updateSuccessMessages('Application rejected')
    await fetchApplications(pagination.current_page)
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to reject application')
  } finally {
    processingId.value = null
  }
}

// Schedule interview
const scheduleInterview = (app) => {
  if (!canManage.value) {
    messageStore.updateErrorMessages('You cannot schedule interviews at this time.')
    return
  }
  
  selectedApplication.value = app
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
    messageStore.updateErrorMessages('Please select interview date')
    return
  }
  
  scheduling.value = true
  try {
    await companyAPI.scheduleInterview(selectedApplication.value.id, interviewData.value)
    messageStore.updateSuccessMessages('Interview scheduled successfully')
    modalInstance.hide()
    await fetchApplications(pagination.current_page)
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to schedule interview')
  } finally {
    scheduling.value = false
  }
}

// View details
const viewDetails = (id) => {
  router.push(`/company/applications/${id}`)
}

// Watch filters
watch(filters, () => {
  fetchApplications(1)
}, { deep: true })

// Initial load
onMounted(() => {
  fetchCompanyProfile()
  fetchDrives()
  fetchApplications()
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
  font-size: 0.85rem;
  text-transform: uppercase;
  color: #495057;
}

.table td {
  vertical-align: middle;
  padding: 1rem 0.75rem;
}

.badge {
  font-weight: 500;
  border-radius: 2rem;
}

.btn {
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-info {
  background: #17a2b8;
  border: none;
}

.btn-success {
  background: #28a745;
  border: none;
}

.btn-danger {
  background: #dc3545;
  border: none;
}

.btn-warning {
  background: #ffc107;
  border: none;
  color: #212529;
}

.btn-outline-primary {
  border: 2px solid #17a2b8;
  color: #17a2b8;
}

.btn-outline-primary:hover {
  background: #17a2b8;
  color: white;
}

.pagination .page-link {
  color: #198754;
}

.pagination .active .page-link {
  background: #198754;
  border-color: #198754;
  color: white;
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