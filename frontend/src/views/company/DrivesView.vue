<!-- frontend/src/views/company/DrivesView.vue -->
<template>
  <div class="drives">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">My Drives</h2>
      <router-link 
        v-if="canCreateDrive" 
        to="/company/drives/create" 
        class="btn btn-success"
      >
        <i class="bi bi-plus-circle me-2"></i>
        Create New Drive
      </router-link>
    </div>

    <!-- Status Warning -->
    <div v-if="!isApproved" class="alert alert-warning mb-4">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <strong>Pending Approval:</strong> Your company is awaiting admin approval. Your drives will be visible to students only after approval.
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
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
                <th>Job Title</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Applications</th>
                <th>Shortlisted</th>
                <th>Selected</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in drives" :key="drive.id">
                <td><span class="fw-medium">#{{ drive.id }}</span></td>
                <td>
                  <strong>{{ drive.drive_name }}</strong>
                </td>
                <td>{{ drive.job_title }}</td>
                <td>{{ formatDate(drive.application_deadline) }}</td>
                <td>
                  <span class="badge" :class="getStatusClass(drive.status)">
                    {{ drive.status }}
                  </span>
                </td>
                <td>{{ drive.application_count || 0 }}</td>
                <td>{{ drive.shortlisted_count || 0 }}</td>
                <td>{{ drive.selected_count || 0 }}</td>
                <td>
                  <div class="d-flex gap-2 flex-wrap" style="min-width: 200px;">
                    <!-- View Details Button -->
                    <router-link 
                      :to="`/company/drives/${drive.id}`" 
                      class="btn btn-info text-white"
                      style="min-width: 100px;"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View
                    </router-link>
                    
                    <!-- Edit Button (only for pending) -->
                    <router-link 
                      v-if="drive.status === 'pending'"
                      :to="`/company/drives/${drive.id}/edit`" 
                      class="btn btn-warning"
                      style="min-width: 100px;"
                    >
                      <i class="bi bi-pencil me-1"></i>
                      Edit
                    </router-link>
                    
                    <!-- Delete Button (only for pending) -->
                    <button 
                      v-if="drive.status === 'pending'"
                      class="btn btn-danger" 
                      @click="deleteDrive(drive.id)"
                      :disabled="processingId === drive.id"
                      style="min-width: 100px;"
                    >
                      <span v-if="processingId === drive.id" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-trash me-1"></i>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>

              <!-- No Data Row -->
              <tr v-if="drives.length === 0">
                <td colspan="9" class="text-center py-5">
                  <i class="bi bi-briefcase fs-1 text-muted d-block mb-3"></i>
                  <h5 class="text-muted">No drives found</h5>
                  <p class="text-muted mb-3">You haven't created any placement drives yet.</p>
                  <router-link 
                    v-if="canCreateDrive" 
                    to="/company/drives/create" 
                    class="btn btn-success"
                  >
                    <i class="bi bi-plus-circle me-2"></i>
                    Create Your First Drive
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const messageStore = useMessageStore()
const authStore = useAuthStore()

// State
const loading = ref(true)
const error = ref(null)
const drives = ref([])
const companyProfile = ref({})
const processingId = ref(null)

// Computed
const isApproved = computed(() => companyProfile.value?.approval_status === 'approved')
const isBlacklisted = computed(() => companyProfile.value?.is_blacklisted || false)
const canCreateDrive = computed(() => isApproved.value && !isBlacklisted.value)

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
  switch(status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    case 'closed': return 'bg-secondary'
    default: return 'bg-secondary'
  }
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

// Fetch drives
const fetchDrives = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await companyAPI.getDrives()
    drives.value = response.data.drives || []
  } catch (err) {
    console.error('Error fetching drives:', err)
    error.value = err.response?.data?.message || 'Failed to load drives'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Delete drive (only allowed for pending drives)
const deleteDrive = async (id) => {
  if (!confirm('Are you sure you want to delete this drive? This action cannot be undone.')) return
  
  processingId.value = id
  try {
    await companyAPI.deleteDrive(id)
    messageStore.updateSuccessMessages('Drive deleted successfully')
    await fetchDrives()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to delete drive')
  } finally {
    processingId.value = null
  }
}

onMounted(() => {
  fetchCompanyProfile()
  fetchDrives()
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
  padding: 1rem 0.5rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
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

.btn-warning {
  background: #ffc107;
  border: none;
  color: #212529;
}

.btn-danger {
  background: #dc3545;
  border: none;
}
</style>