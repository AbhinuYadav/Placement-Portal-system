<!-- frontend/src/views/student/DrivesView.vue -->
<template>
  <div class="drives">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Available Drives</h2>
      <!--<div class="d-flex">
        <select v-model="filters.branch" class="form-select me-2" style="width: 150px;">
          <option value="">All Branches</option>
          <option value="Computer Science">Computer Science</option>
          <option value="Information Technology">Information Technology</option>
          <option value="Electronics">Electronics</option>
          <option value="Mechanical">Mechanical</option>
          <option value="Civil">Civil</option>
        </select>
        <select v-model="filters.eligibility" class="form-select me-2" style="width: 150px;">
          <option value="">All Drives</option>
          <option value="eligible">Eligible Only</option>
          <option value="applied">Applied Only</option>
        </select>
        <input 
          v-model="filters.search"
          type="text" 
          class="form-control me-2" 
          placeholder="Search drives..."
          style="width: 200px;"
          @keyup.enter="fetchDrives"
        >
        <button class="btn btn-primary" @click="fetchDrives" :disabled="loading">
          <i class="bi bi-search me-2"></i>Search
        </button>
        <button class="btn btn-outline-secondary ms-2" @click="resetFilters" title="Reset Filters">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
      </div>-->
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

    <!-- Drives Grid -->
    <div v-else class="row">
      <div v-if="filteredDrives.length === 0" class="col-12 text-center py-5">
        <i class="bi bi-briefcase fs-1 text-muted d-block mb-3"></i>
        <h5 class="text-muted">No drives available</h5>
        <p class="text-muted">Check back later for new opportunities</p>
      </div>

      <div v-for="drive in filteredDrives" :key="drive.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 drive-card" :class="getDriveCardClass(drive)">
          <!-- Status Ribbon -->
          <div v-if="drive.already_applied" class="ribbon ribbon-warning">
            <span>Applied</span>
          </div>
          <div v-else-if="drive.eligibility?.is_eligible" class="ribbon ribbon-success">
            <span>Eligible</span>
          </div>
          <div v-else-if="!drive.eligibility?.deadline_active" class="ribbon ribbon-danger">
            <span>Deadline Passed</span>
          </div>
          <div v-else-if="!drive.eligibility?.is_eligible" class="ribbon ribbon-secondary">
            <span>Not Eligible</span>
          </div>

          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h5 class="card-title mb-1">{{ drive.drive_name }}</h5>
                <h6 class="card-subtitle text-primary">{{ drive.company_name }}</h6>
              </div>
            </div>

            <p class="card-text mb-2">
              <i class="bi bi-briefcase me-2"></i>
              {{ drive.job_title }}
            </p>
            <p class="card-text mb-2">
              <i class="bi bi-calendar me-2"></i>
              Deadline: {{ formatDate(drive.application_deadline) }}
              <span class="badge ms-2" :class="getDeadlineClass(drive)">
                {{ getDaysLeft(drive) }}
              </span>
            </p>
            <p class="card-text mb-3">
              <i class="bi bi-mortarboard me-2"></i>
              CGPA Required: {{ drive.min_cgpa || 'No minimum' }}
            </p>

            <!-- Eligibility Status - Using backend data -->
            <div class="eligibility-status mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span>CGPA ({{ studentProfile.cgpa }})</span>
                <span :class="drive.eligibility?.cgpa_eligible ? 'text-success' : 'text-danger'">
                  <i :class="drive.eligibility?.cgpa_eligible ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                  {{ drive.eligibility?.cgpa_eligible ? 'Eligible' : 'Not Eligible' }}
                </span>
              </div>
              <div class="d-flex justify-content-between">
                <span>Branch ({{ studentProfile.branch }})</span>
                <span :class="drive.eligibility?.branch_eligible ? 'text-success' : 'text-danger'">
                  <i :class="drive.eligibility?.branch_eligible ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                  {{ drive.eligibility?.branch_eligible ? 'Eligible' : 'Not Eligible' }}
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2">
              <router-link 
                :to="`/student/drives/${drive.id}`" 
                class="btn btn-outline-primary"
              >
                <i class="bi bi-info-circle me-2"></i>
                View Details
              </router-link>
              
              <button 
                v-if="!drive.already_applied && drive.eligibility?.is_eligible"
                class="btn btn-success"
                @click="applyToDrive(drive.id)"
                :disabled="applyingId === drive.id"
              >
                <span v-if="applyingId === drive.id" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-send me-2"></i>
                Apply Now
              </button>
              
              <button 
                v-else-if="drive.already_applied"
                class="btn btn-warning"
                disabled
              >
                <i class="bi bi-check-circle me-2"></i>
                Already Applied
              </button>
              
              <button 
                v-else-if="!drive.eligibility?.deadline_active"
                class="btn btn-secondary"
                disabled
              >
                <i class="bi bi-clock-history me-2"></i>
                Deadline Passed
              </button>
              
              <button 
                v-else
                class="btn btn-secondary"
                disabled
              >
                <i class="bi bi-lock me-2"></i>
                Not Eligible
              </button>
            </div>

            <!-- Allowed Branches Info -->
            <div v-if="drive.allowed_branches" class="mt-3 small text-muted">
              <i class="bi bi-people me-1"></i>
              Allowed: {{ drive.allowed_branches }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.total > pagination.per_page" class="d-flex justify-content-center mt-4">
      <nav>
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: pagination.current_page === 1 }">
            <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page - 1)">
              Previous
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
              Next
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { studentAPI } from '@/services/api'

const router = useRouter()
const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const drives = ref([])
const studentProfile = ref({})
const applyingId = ref(null)

// Filters
const filters = reactive({
  branch: '',
  eligibility: '',
  search: ''
})

// Pagination
const pagination = reactive({
  current_page: 1,
  last_page: 1,
  per_page: 9,
  total: 0,
  from: 0,
  to: 0
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
  if (diffDays <= 7) return 'bg-info'
  return 'bg-success'
}

// Card styling based on status
const getDriveCardClass = (drive) => {
  if (drive.already_applied) return 'border-warning'
  if (drive.eligibility?.is_eligible) return 'border-success'
  if (!drive.eligibility?.deadline_active) return 'border-danger'
  if (!drive.eligibility?.is_eligible) return 'border-secondary'
  return ''
}

// Filtered drives based on user selection
const filteredDrives = computed(() => {
  let filtered = drives.value
  
  if (filters.eligibility === 'eligible') {
    filtered = filtered.filter(d => d.eligibility?.is_eligible && !d.already_applied)
  } else if (filters.eligibility === 'applied') {
    filtered = filtered.filter(d => d.already_applied)
  }
  
  if (filters.branch) {
    filtered = filtered.filter(d => {
      if (!d.allowed_branches) return true
      const allowedBranches = d.allowed_branches.split(',').map(b => b.trim())
      return allowedBranches.includes(filters.branch)
    })
  }
  
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(d => 
      d.drive_name?.toLowerCase().includes(searchLower) ||
      d.company_name?.toLowerCase().includes(searchLower) ||
      d.job_title?.toLowerCase().includes(searchLower)
    )
  }
  
  return filtered
})

// Reset Filters
const resetFilters = () => {
  filters.branch = ''
  filters.eligibility = ''
  filters.search = ''
  fetchDrives(1)
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

// Fetch Drives
const fetchDrives = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const params = {
      page,
      per_page: pagination.per_page
    }
    
    if (filters.search) {
      params.search = filters.search
    }
    
    console.log('Fetching drives with params:', params)
    const response = await studentAPI.getDrives(params)
    console.log('Drives response:', response.data)
    
    drives.value = response.data.drives || []
    
    if (response.data.pagination) {
      pagination.current_page = response.data.pagination.current_page || 1
      pagination.last_page = response.data.pagination.last_page || 1
      pagination.total = response.data.pagination.total || 0
      pagination.from = response.data.pagination.from || 0
      pagination.to = response.data.pagination.to || 0
    }
  } catch (err) {
    console.error('Error fetching drives:', err)
    error.value = err.response?.data?.message || 'Failed to load drives'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  fetchDrives(page)
}

// Apply to Drive
const applyToDrive = async (driveId) => {
  applyingId.value = driveId
  try {
    await studentAPI.applyToDrive(driveId)
    messageStore.updateSuccessMessages('Successfully applied to drive!')
    await fetchDrives(pagination.current_page)
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to apply')
  } finally {
    applyingId.value = null
  }
}

// Watch filters
watch(filters, () => {
  fetchDrives(1)
}, { deep: true })

onMounted(() => {
  fetchStudentProfile()
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
}

.drive-card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.drive-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.drive-card.border-success {
  border: 2px solid #28a745 !important;
}

.drive-card.border-warning {
  border: 2px solid #ffc107 !important;
}

.drive-card.border-danger {
  border: 2px solid #dc3545 !important;
}

.drive-card.border-secondary {
  border: 2px solid #6c757d !important;
}

/* Ribbon */
.ribbon {
  position: absolute;
  top: 0;
  right: 0;
  width: 120px;
  height: 120px;
  overflow: hidden;
  z-index: 2;
}

.ribbon span {
  position: absolute;
  top: 25px;
  right: -25px;
  transform: rotate(45deg);
  width: 150px;
  padding: 5px;
  text-align: center;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.ribbon-success span {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.ribbon-warning span {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
}

.ribbon-danger span {
  background: linear-gradient(135deg, #dc3545, #fd7e14);
}

.ribbon-secondary span {
  background: linear-gradient(135deg, #6c757d, #495057);
}

.eligibility-status {
  background: #f8f9fa;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}

.pagination .page-link {
  color: #667eea;
}

.pagination .active .page-link {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.btn-success {
  background: linear-gradient(135deg, #28a745, #20c997);
  border: none;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(40, 167, 69, 0.3);
}

.btn-warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
  border: none;
  color: #212529;
}
</style>