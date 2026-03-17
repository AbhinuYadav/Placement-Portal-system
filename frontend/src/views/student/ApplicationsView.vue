<!-- frontend/src/views/student/ApplicationsView.vue -->
<template>
  <div class="applications">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">My Applications</h2>
      <router-link to="/student/drives" class="btn btn-primary">
        <i class="bi bi-plus-circle me-2"></i>
        Browse More Drives
      </router-link>
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
                <th>Company</th>
                <th>Drive</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Interview Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>
                  <i class="bi bi-building me-1 text-primary"></i>
                  {{ app.company_name }}
                </td>
                <td>{{ app.drive_name }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(app.status)">
                    {{ app.status }}
                  </span>
                </td>
                <td>
                  <span v-if="app.interview_date" class="badge bg-info">
                    <i class="bi bi-calendar me-1"></i>
                    {{ formatDateTime(app.interview_date) }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <!-- View Details Button - Large with text -->
                    <router-link 
                      :to="`/student/applications/${app.id}`" 
                      class="btn btn-outline-primary"
                      style="min-width: 100px;"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View
                    </router-link>
                    
                    <!-- Withdraw Button - Large with text (only for 'applied' status) -->
                    <button 
                      v-if="app.status === 'applied'"
                      class="btn btn-danger"
                      @click="withdrawApplication(app.id)"
                      :disabled="withdrawingId === app.id"
                      style="min-width: 100px;"
                    >
                      <span v-if="withdrawingId === app.id" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-trash me-1"></i>
                      Withdraw
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="applications.length === 0">
                <td colspan="6" class="text-center py-5">
                  <i class="bi bi-file-text fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No applications yet</h5>
                  <p class="text-muted mb-3">Start applying to drives to see them here</p>
                  <router-link to="/student/drives" class="btn btn-primary">
                    Browse Available Drives
                  </router-link>
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { studentAPI } from '@/services/api'

const router = useRouter()
const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const applications = ref([])
const withdrawingId = ref(null)

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
  switch(status?.toLowerCase()) {
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    case 'rejected': return 'bg-danger text-white'
    default: return 'bg-secondary'
  }
}

// Fetch Applications
const fetchApplications = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    const params = { page, per_page: pagination.per_page }
    const response = await studentAPI.getApplications(params)
    
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

// Change Page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  fetchApplications(page)
}

// Withdraw Application
const withdrawApplication = async (id) => {
  if (!confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) return
  
  withdrawingId.value = id
  try {
    await studentAPI.deleteApplication(id)
    messageStore.updateSuccessMessages('Application withdrawn successfully')
    await fetchApplications(pagination.current_page)
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to withdraw application')
  } finally {
    withdrawingId.value = null
  }
}

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
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
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

/* Button styling */
.btn {
  font-weight: 500;
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #fd7e14);
  border: none;
}

.btn-danger:hover {
  background: linear-gradient(135deg, #c82333, #e06b12);
}
</style>