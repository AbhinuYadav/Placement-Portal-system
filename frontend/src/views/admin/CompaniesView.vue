<!-- frontend/src/views/admin/CompaniesView.vue -->
<template>
  <div class="companies">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Companies Management</h2>
      <div class="d-flex">
        <select v-model="filters.status" class="form-select me-2" style="width: 150px;">
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="blacklisted">Blacklisted</option>
        </select>
        <input 
          v-model="filters.search"
          type="text" 
          class="form-control me-2" 
          placeholder="Search companies..."
          style="width: 250px;"
          @keyup.enter="fetchCompanies"
        >
        <button class="btn btn-primary" @click="fetchCompanies" :disabled="loading">
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
            <small class="text-muted">Total Companies</small>
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
        <div class="card bg-dark bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Blacklisted</small>
            <h5>{{ blacklistedCount }}</h5>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading companies...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchCompanies">Retry</button>
    </div>

    <!-- Companies Table -->
    <div v-else class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Company Name</th>
                <th>HR Name</th>
                <th>HR Email</th>
                <th>HR Phone</th>
                <th>Status</th>
                <th>Registered</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in companies" :key="company.id">
                <td><span class="fw-medium">#{{ company.id }}</span></td>
                <td>
                  <strong>{{ company.company_name }}</strong>
                </td>
                <td>{{ company.hr_name }}</td>
                <td>
                  <a :href="'mailto:' + company.hr_email" class="text-decoration-none">
                    {{ company.hr_email }}
                  </a>
                </td>
                <td>{{ company.hr_phone || '—' }}</td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(company)">
                    {{ getDisplayStatus(company) }}
                  </span>
                </td>
                <td>{{ formatDate(company.created_at) }}</td>
                <td>
                  <div class="d-flex gap-2 flex-wrap" style="min-width: 280px;">
                    <!-- Pending Actions -->
                    <template v-if="company.approval_status === 'pending'">
                      <button 
                        class="btn btn-success" 
                        style="min-width: 85px;"
                        @click="approveCompany(company.id)"
                        :disabled="processingId === company.id"
                      >
                        <span v-if="processingId === company.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-check-lg me-1"></i>
                        Approve
                      </button>
                      <button 
                        class="btn btn-danger" 
                        style="min-width: 85px;"
                        @click="rejectCompany(company.id)"
                        :disabled="processingId === company.id"
                      >
                        <i class="bi bi-x-lg me-1"></i>
                        Reject
                      </button>
                    </template>

                    <!-- Approved Company Actions -->
                    <template v-else-if="company.approval_status === 'approved'">
                      <button 
                        v-if="!company.is_blacklisted"
                        class="btn btn-dark" 
                        style="min-width: 95px;"
                        @click="blacklistCompany(company.id)"
                        :disabled="processingId === company.id"
                      >
                        <span v-if="processingId === company.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-lock-fill me-1"></i>
                        Blacklist
                      </button>
                      <button 
                        v-if="company.is_blacklisted"
                        class="btn btn-warning" 
                        style="min-width: 95px;"
                        @click="activateCompany(company.id)"
                        :disabled="processingId === company.id"
                      >
                        <span v-if="processingId === company.id" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-unlock-fill me-1"></i>
                        Activate
                      </button>
                    </template>

                    <!-- Rejected Company - No actions except view -->
                    <template v-else-if="company.approval_status === 'rejected'">
                      <span class="text-muted small align-self-center">Rejected</span>
                    </template>

                    <!-- View Details Button - Always Visible -->
                    <button 
                      class="btn btn-info text-white" 
                      style="min-width: 110px;"
                      @click="viewDetails(company.id)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Details
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="companies.length === 0">
                <td colspan="8" class="text-center py-5">
                  <i class="bi bi-building fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No companies found</h5>
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
const allCompanies = ref([])  // Store all fetched companies
const companies = ref([])      // Filtered companies for display
const processingId = ref(null)

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

// Computed stats
const totalCount = computed(() => allCompanies.value.length)
const pendingCount = computed(() => allCompanies.value.filter(c => c.approval_status === 'pending').length)
const approvedCount = computed(() => allCompanies.value.filter(c => c.approval_status === 'approved' && !c.is_blacklisted).length)
const blacklistedCount = computed(() => allCompanies.value.filter(c => c.is_blacklisted).length)

// Helper Functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getDisplayStatus = (company) => {
  if (company.is_blacklisted) return 'Blacklisted'
  if (!company.approval_status) return 'Unknown'
  return company.approval_status.charAt(0).toUpperCase() + company.approval_status.slice(1)
}

const getStatusClass = (company) => {
  if (company.is_blacklisted) return 'bg-dark'
  switch(company.approval_status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

// Filter companies based on selected status
const applyFilters = () => {
  let filtered = [...allCompanies.value]
  
  // Apply status filter
  if (filters.status) {
    switch(filters.status) {
      case 'pending':
        filtered = filtered.filter(c => c.approval_status === 'pending')
        break
      case 'approved':
        filtered = filtered.filter(c => c.approval_status === 'approved' && !c.is_blacklisted)
        break
      case 'rejected':
        filtered = filtered.filter(c => c.approval_status === 'rejected')
        break
      case 'blacklisted':
        filtered = filtered.filter(c => c.is_blacklisted === true)
        break
    }
  }
  
  // Apply search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(c => 
      c.company_name?.toLowerCase().includes(searchLower) ||
      c.hr_name?.toLowerCase().includes(searchLower) ||
      c.hr_email?.toLowerCase().includes(searchLower)
    )
  }
  
  companies.value = filtered
  pagination.total = filtered.length
}

// Reset Filters
const resetFilters = () => {
  filters.status = ''
  filters.search = ''
  applyFilters()
}

// Fetch all companies
const fetchCompanies = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {}
    if (filters.search) {
      params.search = filters.search
    }
    
    console.log('Fetching all companies...')
    const response = await adminAPI.getCompanies(params)
    
    allCompanies.value = response.data.companies || []
    applyFilters()
    
    console.log(`Loaded ${allCompanies.value.length} companies`)
  } catch (err) {
    console.error('Error fetching companies:', err)
    error.value = err.response?.data?.message || 'Failed to load companies'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page (for future pagination implementation)
const changePage = (page) => {
  pagination.current_page = page
  // In a real implementation, you'd fetch the specific page
}

// Approve Company
const approveCompany = async (id) => {
  if (!confirm('Are you sure you want to approve this company?')) return
  
  processingId.value = id
  try {
    await adminAPI.approveCompany(id)
    messageStore.updateSuccessMessages('Company approved successfully')
    await fetchCompanies()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to approve company')
  } finally {
    processingId.value = null
  }
}

// Reject Company
const rejectCompany = async (id) => {
  const reason = prompt('Please enter rejection reason:')
  if (reason === null || !reason.trim()) return
  
  processingId.value = id
  try {
    await adminAPI.rejectCompany(id, { reason })
    messageStore.updateSuccessMessages('Company rejected')
    await fetchCompanies()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to reject company')
  } finally {
    processingId.value = null
  }
}

// Blacklist Company
const blacklistCompany = async (id) => {
  const reason = prompt('Please enter blacklist reason:')
  if (reason === null || !reason.trim()) return
  
  processingId.value = id
  try {
    await adminAPI.blacklistCompany(id, { reason })
    messageStore.updateSuccessMessages('Company blacklisted')
    await fetchCompanies()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to blacklist company')
  } finally {
    processingId.value = null
  }
}

// Activate Company (Remove from blacklist)
const activateCompany = async (id) => {
  if (!confirm('Are you sure you want to activate this company?')) return
  
  processingId.value = id
  try {
    await adminAPI.activateCompany(id)
    messageStore.updateSuccessMessages('Company activated')
    await fetchCompanies()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to activate company')
  } finally {
    processingId.value = null
  }
}

// View Company Details
const viewDetails = (id) => {
  router.push(`/admin/companies/${id}`)
}

// Watch filters and re-apply
watch(filters, () => {
  applyFilters()
}, { deep: true })

// Initial load
onMounted(() => {
  fetchCompanies()
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

.btn-dark {
  background: linear-gradient(135deg, #343a40, #495057);
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