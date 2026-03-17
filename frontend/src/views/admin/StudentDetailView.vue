<!-- frontend/src/views/admin/StudentDetailView.vue -->
<template>
  <div class="student-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Student Details</h2>
      <div>
        <button class="btn btn-outline-secondary me-2" @click="goBack">
          <i class="bi bi-arrow-left me-2"></i>
          Back to Students
        </button>
        <button class="btn btn-outline-primary" @click="refreshData">
          <i class="bi bi-arrow-repeat me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading student details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchStudentDetails">Retry</button>
    </div>

    <!-- Student Details -->
    <div v-else class="row">
      <!-- Left Column - Student Info -->
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-person-circle me-2 text-primary"></i>
              Student Information
            </h5>
            <span class="badge fs-6 px-3 py-2" :class="getStatusClass(student)">
              {{ getDisplayStatus(student) }}
            </span>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="student-avatar bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 120px; height: 120px;">
                <i class="bi bi-person-circle fs-1 text-primary"></i>
              </div>
              <h3>{{ student.name }}</h3>
              <p class="text-muted mb-0">Student ID: #{{ student.id }}</p>
              <p class="text-muted">Roll Number: {{ student.roll_number }}</p>
            </div>

            <table class="table table-bordered">
              <tbody>
                <tr>
                  <th style="width: 40%; background-color: #f8f9fa;">Email</th>
                  <td>
                    <a :href="'mailto:' + student.email" class="text-decoration-none">
                      <i class="bi bi-envelope me-1"></i>
                      {{ student.email }}
                    </a>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Phone</th>
                  <td>
                    <a :href="'tel:' + student.phone" class="text-decoration-none" v-if="student.phone">
                      <i class="bi bi-telephone me-1"></i>
                      {{ student.phone }}
                    </a>
                    <span v-else>Not provided</span>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Branch</th>
                  <td>{{ student.branch }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">CGPA</th>
                  <td>
                    <span class="badge" :class="getCGPAClass(student.cgpa)">
                      {{ student.cgpa }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Graduation Year</th>
                  <td>{{ student.graduation_year }}</td>
                </tr>
                <tr>
                  <th style="background-color: #f8f9fa;">Registered On</th>
                  <td>{{ formatDate(student.created_at) }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Blacklist Reason (if blacklisted) -->
            <div v-if="student.is_blacklisted && student.blacklist_reason" class="alert alert-dark mt-3">
              <strong>Blacklist Reason:</strong>
              <p class="mb-0 mt-1">{{ student.blacklist_reason }}</p>
              <small class="text-muted">Blacklisted on: {{ formatDate(student.blacklisted_at) }}</small>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 mt-4">
              <button 
                v-if="!student.is_blacklisted"
                class="btn btn-dark btn-lg" 
                @click="blacklistStudent"
                :disabled="processingAction"
              >
                <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-lock-fill me-2"></i>
                Blacklist Student
              </button>
              <button 
                v-if="student.is_blacklisted"
                class="btn btn-warning btn-lg" 
                @click="activateStudent"
                :disabled="processingAction"
              >
                <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-unlock-fill me-2"></i>
                Activate Student
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Additional Info -->
      <div class="col-md-8 mb-4">
        <!-- Resume Card -->
        <div class="card mb-4">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-file-earmark-text me-2 text-info"></i>
              Resume
            </h5>
          </div>
          <div class="card-body">
            <div v-if="student.resume_path" class="text-center py-3">
              <i class="bi bi-file-pdf fs-1 text-danger mb-3"></i>
              <p class="mb-2">Resume uploaded</p>
              <a :href="student.resume_path" class="btn btn-outline-primary" target="_blank">
                <i class="bi bi-download me-2"></i>
                View/Download Resume
              </a>
            </div>
            <div v-else class="text-center py-4 text-muted">
              <i class="bi bi-file-earmark-x fs-1 d-block mb-3"></i>
              <p class="mb-0">No resume uploaded</p>
            </div>
          </div>
        </div>

        <!-- Application History -->
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-briefcase me-2 text-success"></i>
              Application History
            </h5>
            <span class="badge bg-primary fs-6 px-3 py-2">Total: {{ applications.length }}</span>
          </div>
          <div class="card-body">
            <div v-if="applications.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-inbox fs-1 d-block mb-3"></i>
              <p class="mb-0">No applications yet</p>
            </div>
            <div v-else>
              <!-- Stats Cards -->
              <div class="row g-3 mb-4">
                <div class="col-3">
                  <div class="card bg-warning bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Applied</div>
                      <div class="h4 mb-0">{{ applicationStats.applied }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-info bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Shortlisted</div>
                      <div class="h4 mb-0">{{ applicationStats.shortlisted }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-success bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Selected</div>
                      <div class="h4 mb-0">{{ applicationStats.selected }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-3">
                  <div class="card bg-danger bg-opacity-10 border-0">
                    <div class="card-body text-center py-2">
                      <div class="small text-muted">Rejected</div>
                      <div class="h4 mb-0">{{ applicationStats.rejected }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Applications Table -->
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Company</th>
                      <th>Drive</th>
                      <th>Applied On</th>
                      <th>Status</th>
                      <th>Interview Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="app in applications" :key="app.id">
                      <td>
                        <router-link :to="`/admin/companies/${app.company_id}`" class="text-decoration-none">
                          {{ app.company_name }}
                        </router-link>
                      </td>
                      <td>
                        <router-link :to="`/admin/drives/${app.drive_id}`" class="text-decoration-none">
                          {{ app.drive_name }}
                        </router-link>
                      </td>
                      <td>{{ formatDate(app.applied_at) }}</td>
                      <td>
                        <span class="badge" :class="getApplicationStatusClass(app.status)">
                          {{ app.status }}
                        </span>
                      </td>
                      <td>{{ formatDate(app.interview_date) || 'Not scheduled' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
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
import { adminAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const studentId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const processingAction = ref(false)
const student = ref({})
const applications = ref([])

// Computed
const applicationStats = computed(() => {
  const stats = { applied: 0, shortlisted: 0, selected: 0, rejected: 0 }
  applications.value.forEach(app => {
    if (app.status === 'applied') stats.applied++
    else if (app.status === 'shortlisted') stats.shortlisted++
    else if (app.status === 'selected') stats.selected++
    else if (app.status === 'rejected') stats.rejected++
  })
  return stats
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
  return 'Active'
}

const getStatusClass = (student) => {
  if (student.is_blacklisted) return 'bg-dark'
  return 'bg-success'
}

const getApplicationStatusClass = (status) => {
  switch(status?.toLowerCase()) {
    case 'applied': return 'bg-warning text-dark'
    case 'shortlisted': return 'bg-info text-white'
    case 'selected': return 'bg-success text-white'
    case 'rejected': return 'bg-danger text-white'
    default: return 'bg-secondary text-white'
  }
}

// Fetch Student Details
const fetchStudentDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`Fetching student details for ID: ${studentId}`)
    const response = await adminAPI.getStudentDetails(studentId)
    console.log('Student details response:', response.data)
    
    student.value = response.data.student || {}
    applications.value = response.data.applications || []
  } catch (err) {
    console.error('Error fetching student details:', err)
    error.value = err.response?.data?.message || 'Failed to load student details'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Refresh Data
const refreshData = () => {
  fetchStudentDetails()
}

// Blacklist Student
const blacklistStudent = async () => {
  const reason = prompt('Please enter blacklist reason:')
  if (reason === null || !reason.trim()) return
  
  processingAction.value = true
  try {
    await adminAPI.blacklistStudent(studentId, { reason })
    messageStore.updateSuccessMessages('Student blacklisted')
    await fetchStudentDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to blacklist student')
  } finally {
    processingAction.value = false
  }
}

// Activate Student
const activateStudent = async () => {
  if (!confirm('Are you sure you want to activate this student?')) return
  
  processingAction.value = true
  try {
    await adminAPI.activateStudent(studentId)
    messageStore.updateSuccessMessages('Student activated')
    await fetchStudentDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to activate student')
  } finally {
    processingAction.value = false
  }
}

const goBack = () => {
  router.push('/admin/students')
}

// Initial load
onMounted(() => {
  fetchStudentDetails()
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

.student-avatar {
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
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  border-radius: 1rem 1rem 0 0 !important;
  padding: 1rem 1.5rem;
}

.badge {
  font-weight: 500;
  border-radius: 2rem;
}

.btn {
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
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
</style>