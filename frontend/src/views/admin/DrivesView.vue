<!-- frontend/src/views/admin/DrivesView.vue -->
<template>
  <div class="drives">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Drives Management</h2>
      <div class="d-flex">
        <select v-model="filters.status" class="form-select me-2" style="width: 150px;">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="closed">Closed</option>
        </select>
        <select v-model="filters.company_id" class="form-select me-2" style="width: 180px;">
          <option value="">All Companies</option>
          <option v-for="company in companies" :key="company.id" :value="company.id">
            {{ company.company_name }}
          </option>
        </select>
        <input 
          v-model="filters.search"
          type="text" 
          class="form-control me-2" 
          placeholder="Search drives..."
          style="width: 250px;"
          @keyup.enter="fetchDrives"
        >
        <button class="btn btn-primary" @click="fetchDrives" :disabled="loading">
          <i class="bi bi-search me-2"></i>Search
        </button>
        <button class="btn btn-outline-secondary ms-2" @click="resetFilters" title="Reset Filters">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-light">
          <div class="card-body py-2">
            <small class="text-muted">Total Drives</small>
            <h5>{{ totalCount }}</h5>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Pending</small>
            <h5>{{ pendingCount }}</h5>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Approved</small>
            <h5>{{ approvedCount }}</h5>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-secondary bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Closed</small>
            <h5>{{ closedCount }}</h5>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading drives...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchDrives">Retry</button>
    </div>

    <!-- Drives Table -->
    <div v-else class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Drive Name</th>
                <th>Company</th>
                <th>Job Title</th>
                <th>Deadline</th>
                <th>Eligibility</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in drives" :key="drive.id">
                <td><span class="fw-medium">#{{ drive.id }}</span></td>
                <td>
                  <strong>{{ drive.drive_name }}</strong>
                </td>
                <td>
                  <router-link :to="`/admin/companies/${drive.company_id}`" class="text-decoration-none">
                    {{ drive.company_name }}
                  </router-link>
                </td>
                <td>{{ drive.job_title }}</td>
                <td>{{ formatDate(drive.application_deadline) }}</td>
                <td>
                  <div class="small">
                    <span v-if="drive.min_cgpa" class="badge bg-info me-1">CGPA: {{ drive.min_cgpa }}+</span>
                    <span v-if="drive.allowed_branches" class="badge bg-secondary">{{ drive.allowed_branches }}</span>
                  </div>
                </td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(drive)">
                    {{ formatStatus(drive.status) }}
                  </span>
                </td>
                <td>{{ formatDate(drive.created_at) }}</td>
                <td>
                  <div class="d-flex gap-2 flex-wrap" style="min-width: 280px;">
                    <!-- Pending Actions -->
                    <template v-if="drive.status === 'pending'">
                      <button 
                        class="btn btn-success" 
                        style="min-width: 85px;"
                        @click="approveDrive(drive.id)"
                        :disabled="processingId === drive.id"
                      >
                        <span v-if="processingId === drive.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-check-lg me-1"></i>
                        Approve
                      </button>
                      <button 
                        class="btn btn-danger" 
                        style="min-width: 85px;"
                        @click="rejectDrive(drive.id)"
                        :disabled="processingId === drive.id"
                      >
                        <i class="bi bi-x-lg me-1"></i>
                        Reject
                      </button>
                    </template>

                    <!-- Approved Drive Actions -->
                    <template v-else-if="drive.status === 'approved'">
                      <button 
                        class="btn btn-warning" 
                        style="min-width: 85px;"
                        @click="closeDrive(drive.id)"
                        :disabled="processingId === drive.id"
                      >
                        <span v-if="processingId === drive.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-stop-circle me-1"></i>
                        Close
                      </button>
                    </template>

                    <!-- Closed/Rejected - No actions except view -->
                    <template v-else>
                      <span class="text-muted small align-self-center">{{ drive.status }}</span>
                    </template>

                    <!-- View Details Button - Always Visible -->
                    <button 
                      class="btn btn-info text-white" 
                      style="min-width: 110px;"
                      @click="viewDetails(drive.id)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Details
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="drives.length === 0">
                <td colspan="9" class="text-center py-5">
                  <i class="bi bi-briefcase fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No drives found</h5>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { adminAPI } from '@/services/api'

const router = useRouter()
const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const allDrives = ref([])      // Store all fetched drives
const drives = ref([])          // Filtered drives for display
const companies = ref([])       // List of companies for filter dropdown
const processingId = ref(null)

// Filters
const filters = reactive({
  status: '',
  company_id: '',
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

// Computed stats
const totalCount = computed(() => allDrives.value.length)
const pendingCount = computed(() => allDrives.value.filter(d => d.status === 'pending').length)
const approvedCount = computed(() => allDrives.value.filter(d => d.status === 'approved').length)
const closedCount = computed(() => allDrives.value.filter(d => d.status === 'closed').length)

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

// Filter drives based on selected filters
const applyFilters = () => {
  let filtered = [...allDrives.value]
  
  // Apply status filter
  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }
  
  // Apply company filter
  if (filters.company_id) {
    filtered = filtered.filter(d => d.company_id == filters.company_id)
  }
  
  // Apply search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(d => 
      d.drive_name?.toLowerCase().includes(searchLower) ||
      d.job_title?.toLowerCase().includes(searchLower) ||
      d.company_name?.toLowerCase().includes(searchLower)
    )
  }
  
  drives.value = filtered
  pagination.total = filtered.length
}

// Reset Filters
const resetFilters = () => {
  filters.status = ''
  filters.company_id = ''
  filters.search = ''
  applyFilters()
}

// Fetch all drives
const fetchDrives = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {}
    if (filters.search) {
      params.search = filters.search
    }
    if (filters.company_id) {
      params.company_id = filters.company_id
    }
    if (filters.status) {
      params.status = filters.status
    }
    
    console.log('Fetching drives with params:', params)
    const response = await adminAPI.getDrives(params)
    
    allDrives.value = response.data.drives || []
    
    // Extract unique companies for filter
    const companyMap = new Map()
    allDrives.value.forEach(drive => {
      if (drive.company_id && drive.company_name && !companyMap.has(drive.company_id)) {
        companyMap.set(drive.company_id, {
          id: drive.company_id,
          company_name: drive.company_name
        })
      }
    })
    companies.value = Array.from(companyMap.values())
    
    applyFilters()
    
    console.log(`Loaded ${allDrives.value.length} drives`)
  } catch (err) {
    console.error('Error fetching drives:', err)
    error.value = err.response?.data?.message || 'Failed to load drives'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page (for future pagination implementation)
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  pagination.current_page = page
  // In a real implementation, you'd fetch the specific page
}

// Approve Drive
const approveDrive = async (id) => {
  if (!confirm('Are you sure you want to approve this drive?')) return
  
  processingId.value = id
  try {
    await adminAPI.approveDrive(id)
    messageStore.updateSuccessMessages('Drive approved successfully')
    await fetchDrives()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to approve drive')
  } finally {
    processingId.value = null
  }
}

// Reject Drive
const rejectDrive = async (id) => {
  if (!confirm('Are you sure you want to reject this drive?')) return
  
  processingId.value = id
  try {
    await adminAPI.rejectDrive(id)
    messageStore.updateSuccessMessages('Drive rejected')
    await fetchDrives()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to reject drive')
  } finally {
    processingId.value = null
  }
}

// Close Drive
const closeDrive = async (id) => {
  if (!confirm('Are you sure you want to close this drive?')) return
  
  processingId.value = id
  try {
    await adminAPI.closeDrive(id)
    messageStore.updateSuccessMessages('Drive closed')
    await fetchDrives()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to close drive')
  } finally {
    processingId.value = null
  }
}

// View Drive Details
const viewDetails = (id) => {
  router.push(`/admin/drives/${id}`)
}

// Watch filters and re-apply
watch(filters, () => {
  applyFilters()
}, { deep: true })

// Initial load
onMounted(() => {
  fetchDrives()
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
  margin-bottom: 0;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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

.btn-info {
  background: linear-gradient(135deg, #17a2b8, #0dcaf0);
  border: none;
}

.pagination .page-link {
  color: #667eea;
  padding: 0.5rem 0.9rem;
}

.pagination .active .page-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .d-flex.gap-2 {
    flex-direction: column;
    min-width: auto !important;
  }
  
  .btn {
    width: 100%;
  }
}
</style>