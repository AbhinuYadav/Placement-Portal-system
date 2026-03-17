<!-- frontend/src/views/admin/StudentsView.vue -->
<template>
  <div class="students">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Students Management</h2>
      <div class="d-flex">
        <select v-model="filters.branch" class="form-select me-2" style="width: 150px;">
          <option value="">All Branches</option>
          <option value="Computer Science">Computer Science</option>
          <option value="Information Technology">Information Technology</option>
          <option value="Electronics">Electronics</option>
          <option value="Mechanical">Mechanical</option>
          <option value="Civil">Civil</option>
        </select>
        <select v-model="filters.year" class="form-select me-2" style="width: 120px;">
          <option value="">All Years</option>
          <option value="2026">2026</option>
          <option value="2027">2027</option>
          <option value="2028">2028</option>
        </select>
        <select v-model="filters.status" class="form-select me-2" style="width: 130px;">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="blacklisted">Blacklisted</option>
          <option value="placed">Placed</option>
        </select>
        <input 
          v-model="filters.search"
          type="text" 
          class="form-control me-2" 
          placeholder="Search by name or roll number..."
          style="width: 250px;"
          @keyup.enter="fetchStudents"
        >
        <button class="btn btn-primary" @click="fetchStudents" :disabled="loading">
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
            <small class="text-muted">Total Students</small>
            <h5>{{ totalCount }}</h5>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Active</small>
            <h5>{{ activeCount }}</h5>
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
      <div class="col-md-3">
        <div class="card bg-primary bg-opacity-10">
          <div class="card-body py-2">
            <small class="text-muted">Placed</small>
            <h5>{{ placedCount }}</h5>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading students...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchStudents">Retry</button>
    </div>

    <!-- Students Table -->
    <div v-else class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Roll Number</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Graduation Year</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.id">
                <td><span class="fw-medium">#{{ student.id }}</span></td>
                <td>
                  <strong>{{ student.name }}</strong>
                </td>
                <td>{{ student.roll_number }}</td>
                <td>{{ student.branch }}</td>
                <td>
                  <span class="badge" :class="getCGPAClass(student.cgpa)">
                    {{ student.cgpa }}
                  </span>
                </td>
                <td>{{ student.graduation_year }}</td>
                <td>
                  <a :href="'mailto:' + student.email" class="text-decoration-none">
                    {{ student.email }}
                  </a>
                </td>
                <td>{{ student.phone || '—' }}</td>
                <td>
                  <span class="badge fs-6 px-3 py-2" :class="getStatusClass(student)">
                    {{ getDisplayStatus(student) }}
                  </span>
                </td>
                <td>
                  <div class="d-flex gap-2 flex-wrap" style="min-width: 220px;">
                    <!-- Blacklist/Activate Actions -->
                    <button 
                      v-if="!student.is_blacklisted"
                      class="btn btn-dark" 
                      style="min-width: 95px;"
                      @click="blacklistStudent(student.id)"
                      :disabled="processingId === student.id"
                      title="Blacklist Student"
                    >
                      <span v-if="processingId === student.id" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-lock-fill me-1"></i>
                      Blacklist
                    </button>
                    <button 
                      v-if="student.is_blacklisted"
                      class="btn btn-warning" 
                      style="min-width: 95px;"
                      @click="activateStudent(student.id)"
                      :disabled="processingId === student.id"
                      title="Activate Student"
                    >
                      <span v-if="processingId === student.id" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-unlock-fill me-1"></i>
                      Activate
                    </button>

                    <!-- View Details Button -->
                    <button 
                      class="btn btn-info text-white" 
                      style="min-width: 110px;"
                      @click="viewDetails(student.id)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Details
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="students.length === 0">
                <td colspan="10" class="text-center py-5">
                  <i class="bi bi-people fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No students found</h5>
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
const allStudents = ref([])
const students = ref([])
const processingId = ref(null)

// Filters
const filters = reactive({
  branch: '',
  year: '',
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
const totalCount = computed(() => allStudents.value.length)
const activeCount = computed(() => allStudents.value.filter(s => !s.is_blacklisted).length)
const blacklistedCount = computed(() => allStudents.value.filter(s => s.is_blacklisted).length)
const placedCount = computed(() => {
  // This depends on your backend - you might have a 'placed' field
  return allStudents.value.filter(s => s.is_placed).length || 0
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

const getCGPAClass = (cgpa) => {
  if (cgpa >= 9.0) return 'bg-success'
  if (cgpa >= 8.0) return 'bg-info'
  if (cgpa >= 7.0) return 'bg-warning text-dark'
  if (cgpa >= 6.0) return 'bg-secondary'
  return 'bg-danger'
}

const getDisplayStatus = (student) => {
  if (student.is_blacklisted) return 'Blacklisted'
  if (student.is_placed) return 'Placed'
  return 'Active'
}

const getStatusClass = (student) => {
  if (student.is_blacklisted) return 'bg-dark'
  if (student.is_placed) return 'bg-primary'
  return 'bg-success'
}

// Filter students based on selected filters
const applyFilters = () => {
  let filtered = [...allStudents.value]
  
  // Apply branch filter
  if (filters.branch) {
    filtered = filtered.filter(s => s.branch === filters.branch)
  }
  
  // Apply year filter
  if (filters.year) {
    filtered = filtered.filter(s => s.graduation_year == filters.year)
  }
  
  // Apply status filter
  if (filters.status) {
    switch(filters.status) {
      case 'active':
        filtered = filtered.filter(s => !s.is_blacklisted && !s.is_placed)
        break
      case 'blacklisted':
        filtered = filtered.filter(s => s.is_blacklisted)
        break
      case 'placed':
        filtered = filtered.filter(s => s.is_placed)
        break
    }
  }
  
  // Apply search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(s => 
      s.name?.toLowerCase().includes(searchLower) ||
      s.roll_number?.toLowerCase().includes(searchLower) ||
      s.email?.toLowerCase().includes(searchLower)
    )
  }
  
  students.value = filtered
  pagination.total = filtered.length
}

// Reset Filters
const resetFilters = () => {
  filters.branch = ''
  filters.year = ''
  filters.status = ''
  filters.search = ''
  applyFilters()
}

// Fetch all students
const fetchStudents = async () => {
  loading.value = true
  error.value = null
  
  try {
    const params = {}
    if (filters.search) {
      params.search = filters.search
    }
    if (filters.branch) {
      params.branch = filters.branch
    }
    if (filters.year) {
      params.year = filters.year
    }
    
    console.log('Fetching students with params:', params)
    const response = await adminAPI.getStudents(params)
    
    allStudents.value = response.data.students || []
    applyFilters()
    
    console.log(`Loaded ${allStudents.value.length} students`)
  } catch (err) {
    console.error('Error fetching students:', err)
    error.value = err.response?.data?.message || 'Failed to load students'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Change Page
const changePage = (page) => {
  if (page < 1 || page > pagination.last_page) return
  pagination.current_page = page
}

// Blacklist Student
const blacklistStudent = async (id) => {
  const reason = prompt('Please enter blacklist reason:')
  if (reason === null || !reason.trim()) return
  
  processingId.value = id
  try {
    await adminAPI.blacklistStudent(id, { reason })
    messageStore.updateSuccessMessages('Student blacklisted')
    await fetchStudents()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to blacklist student')
  } finally {
    processingId.value = null
  }
}

// Activate Student
const activateStudent = async (id) => {
  if (!confirm('Are you sure you want to activate this student?')) return
  
  processingId.value = id
  try {
    await adminAPI.activateStudent(id)
    messageStore.updateSuccessMessages('Student activated')
    await fetchStudents()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to activate student')
  } finally {
    processingId.value = null
  }
}

// View Student Details
const viewDetails = (id) => {
  router.push(`/admin/students/${id}`)
}

// Watch filters and re-apply
watch(filters, () => {
  applyFilters()
}, { deep: true })

// Initial load
onMounted(() => {
  fetchStudents()
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
</style>