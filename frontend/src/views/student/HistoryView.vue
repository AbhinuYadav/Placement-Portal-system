<!-- frontend/src/views/student/HistoryView.vue -->
<template>
  <div class="history">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Placement History</h2>
      <div class="d-flex">
        <select v-model="filters.year" class="form-select me-2" style="width: 120px;">
          <option value="">All Years</option>
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        <select v-model="filters.status" class="form-select me-2" style="width: 150px;">
          <option value="">All Status</option>
          <option value="applied">Applied</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="selected">Selected</option>
          <option value="rejected">Rejected</option>
        </select>
        <button class="btn btn-primary" @click="fetchHistory" :disabled="loading">
          <i class="bi bi-funnel me-2"></i>
          Filter
        </button>
        <button class="btn btn-outline-secondary ms-2" @click="resetFilters" title="Reset Filters">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h6 class="card-title text-white-50">Total Applications</h6>
            <h2 class="mb-0">{{ summary.total_applications }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h6 class="card-title text-white-50">Selected</h6>
            <h2 class="mb-0">{{ summary.selections }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <h6 class="card-title text-white-50">Shortlisted</h6>
            <h2 class="mb-0">{{ summary.shortlisted }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-white">
          <div class="card-body">
            <h6 class="card-title text-white-50">Success Rate</h6>
            <h2 class="mb-0">{{ successRate }}%</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading placement history...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchHistory">Retry</button>
    </div>

    <!-- History Content -->
    <div v-else>
      <!-- Applications Table (Replaces Timeline and Company Summary) -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-building me-2 text-primary"></i>
                All Applications
              </h5>
              <span class="badge bg-primary">{{ filteredHistory.length }} Total</span>
            </div>
            <div class="card-body">
              <div v-if="filteredHistory.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1 d-block mb-3"></i>
                <p class="mb-0">No applications found</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead>
                    <tr>
                      <th>S.No</th>
                      <th>Company Name</th>
                      <th>Drive / Job Title</th>
                      <th>Applied Date</th>
                      <th>Status</th>
                      <th>Interview Date</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(app, index) in paginatedApplications" :key="app.id">
                      <td>{{ (pagination.current_page - 1) * pagination.per_page + index + 1 }}</td>
                      <td>
                        <strong>
                          <i class="bi bi-building me-1 text-primary"></i>
                          {{ app.company_name }}
                        </strong>
                      </td>
                      <td>
                        <div>{{ app.drive_name }}</div>
                        <small class="text-muted">{{ app.job_title }}</small>
                      </td>
                      <td>{{ formatDate(app.applied_at) }}</td>
                      <td>
                        <span class="badge fs-6 px-3 py-2" :class="getStatusClass(app.final_status)">
                          {{ app.final_status }}
                        </span>
                      </td>
                      <td>
                        <span v-if="app.interview_date" class="badge bg-info">
                          <i class="bi bi-calendar me-1"></i>
                          {{ formatDate(app.interview_date) }}
                        </span>
                        <span v-else class="text-muted">—</span>
                      </td>
                      <td>
                        <router-link 
                          :to="`/student/applications/${app.id}`" 
                          class="btn btn-sm btn-outline-primary"
                          title="View Details"
                        >
                          <i class="bi bi-eye me-1"></i>
                          View
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <div v-if="filteredHistory.length > pagination.per_page" class="d-flex justify-content-between align-items-center mt-4">
                <div class="text-muted">
                  Showing {{ pagination.from }} to {{ pagination.to }} of {{ pagination.total }} entries
                </div>
                <nav>
                  <ul class="pagination mb-0">
                    <li class="page-item" :class="{ disabled: pagination.current_page === 1 }">
                      <a class="page-link" href="#" @click.prevent="changePage(pagination.current_page - 1)">
                        <i class="bi bi-chevron-left"></i> Previous
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
                        Next <i class="bi bi-chevron-right"></i>
                      </a>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useMessageStore } from '@/stores/message'
import { studentAPI } from '@/services/api'

const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const history = ref([])
const filters = reactive({
  year: '',
  status: ''
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
const availableYears = computed(() => {
  const years = new Set()
  history.value.forEach(item => {
    if (item.applied_at) {
      const year = new Date(item.applied_at).getFullYear()
      years.add(year)
    }
  })
  return Array.from(years).sort().reverse()
})

const filteredHistory = computed(() => {
  let filtered = history.value
  
  if (filters.year) {
    filtered = filtered.filter(item => {
      const itemYear = new Date(item.applied_at).getFullYear()
      return itemYear === parseInt(filters.year)
    })
  }
  
  if (filters.status) {
    filtered = filtered.filter(item => 
      item.final_status?.toLowerCase() === filters.status.toLowerCase()
    )
  }
  
  return filtered
})

const paginatedApplications = computed(() => {
  const start = (pagination.current_page - 1) * pagination.per_page
  const end = start + pagination.per_page
  return filteredHistory.value.slice(start, end)
})

const summary = computed(() => {
  const total = filteredHistory.value.length
  const selected = filteredHistory.value.filter(h => h.final_status === 'selected').length
  const shortlisted = filteredHistory.value.filter(h => h.final_status === 'shortlisted').length
  const rejected = filteredHistory.value.filter(h => h.final_status === 'rejected').length
  const applied = filteredHistory.value.filter(h => h.final_status === 'applied').length
  
  return {
    total_applications: total,
    selections: selected,
    shortlisted: shortlisted,
    rejected: rejected,
    applied: applied
  }
})

const successRate = computed(() => {
  if (summary.value.total_applications === 0) return 0
  return Math.round((summary.value.selections / summary.value.total_applications) * 100)
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

const getStatusClass = (status) => {
  switch(status?.toLowerCase()) {
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    case 'rejected': return 'bg-danger text-white'
    default: return 'bg-secondary'
  }
}

// Fetch History
const fetchHistory = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {}
    if (filters.year) params.year = filters.year
    if (filters.status) params.status = filters.status
    
    const response = await studentAPI.getHistory(params)
    history.value = response.data.history || []
    
    // Update pagination
    pagination.total = filteredHistory.value.length
    pagination.last_page = Math.ceil(pagination.total / pagination.per_page)
    pagination.from = (pagination.current_page - 1) * pagination.per_page + 1
    pagination.to = Math.min(pagination.current_page * pagination.per_page, pagination.total)
    
  } catch (err) {
    console.error('Error fetching history:', err)
    error.value = err.response?.data?.message || 'Failed to load history'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  pagination.current_page = page
  pagination.from = (page - 1) * pagination.per_page + 1
  pagination.to = Math.min(page * pagination.per_page, pagination.total)
}

// Reset Filters
const resetFilters = () => {
  filters.year = ''
  filters.status = ''
  pagination.current_page = 1
  fetchHistory()
}

// Watch filters
watch(filters, () => {
  pagination.current_page = 1
  fetchHistory()
}, { deep: true })

// Watch filtered history to update pagination
watch(filteredHistory, (newVal) => {
  pagination.total = newVal.length
  pagination.last_page = Math.ceil(pagination.total / pagination.per_page)
  pagination.from = (pagination.current_page - 1) * pagination.per_page + 1
  pagination.to = Math.min(pagination.current_page * pagination.per_page, pagination.total)
})

onMounted(() => {
  fetchHistory()
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

.btn-outline-primary {
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-outline-primary:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

.pagination .page-link {
  color: #667eea;
}

.pagination .active .page-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

/* Card Colors */
.bg-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-success {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.bg-info {
  background: linear-gradient(135deg, #17a2b8, #0dcaf0);
}

.bg-warning {
  background: linear-gradient(135deg, #ffc107, #fd7e14);
}

.text-white-50 {
  color: rgba(255, 255, 255, 0.7) !important;
}
</style>