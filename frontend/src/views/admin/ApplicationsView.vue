<!-- frontend/src/views/admin/ApplicationsView.vue -->
<template>
  <div class="applications">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Applications Management</h2>
      <div class="d-flex">
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
          placeholder="Search by student or company..."
          style="width: 250px;"
          @keyup.enter="fetchApplications"
        >
        <button class="btn btn-primary" @click="fetchApplications" :disabled="loading">
          <i class="bi bi-search me-2"></i>Search
        </button>
        <button class="btn btn-outline-secondary ms-2" @click="resetFilters" title="Reset Filters">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
      </div>
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
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
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
                <th>Company</th>
                <th>Drive</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Interview Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td><span class="fw-medium">#{{ app.id }}</span></td>
                <td>
                  <i class="bi bi-person-circle me-1 text-primary"></i>
                  {{ app.student_name }}
                </td>
                <td>
                  <i class="bi bi-building me-1 text-success"></i>
                  {{ app.company_name }}
                </td>
                <td>
                  <i class="bi bi-briefcase me-1 text-warning"></i>
                  {{ app.drive_name }}
                </td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </td>
                <td>
                  <span v-if="app.interview_date" class="badge bg-info">
                    <i class="bi bi-calendar me-1"></i>
                    {{ formatDate(app.interview_date) }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="applications.length === 0">
                <td colspan="7" class="text-center py-5">
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useMessageStore } from '@/stores/message'
import { adminAPI } from '@/services/api'

const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const applications = ref([])

// Filters
const filters = reactive({
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

// Stats
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
    default: return 'bg-secondary text-white'
  }
}

// Reset Filters
const resetFilters = () => {
  filters.status = ''
  filters.search = ''
  fetchApplications()
}

// Fetch Applications
const fetchApplications = async (page = 1) => {
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
    if (filters.status) {
      params.status = filters.status
    }
    
    console.log('Fetching applications with params:', params)
    const response = await adminAPI.getApplications(params)
    
    applications.value = response.data.applications || []
    
    // Update pagination
    if (response.data.pagination) {
      pagination.current_page = response.data.pagination.current_page || 1
      pagination.last_page = response.data.pagination.last_page || 1
      pagination.total = response.data.pagination.total || 0
      pagination.from = response.data.pagination.from || 0
      pagination.to = response.data.pagination.to || 0
    }
    
    console.log(`Loaded ${applications.value.length} applications`)
  } catch (err) {
    console.error('Error fetching applications:', err)
    error.value = err.response?.data?.message || 'Failed to load applications'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  fetchApplications(page)
}

// Watch filters
watch(filters, () => {
  fetchApplications(1)
}, { deep: true })

// Initial load
onMounted(() => {
  fetchApplications()
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

.card {
  border: none;
  border-radius: 0.75rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
</style>