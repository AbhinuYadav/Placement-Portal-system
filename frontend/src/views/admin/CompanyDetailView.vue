<!-- frontend/src/views/admin/CompanyDetailView.vue -->
<template>
  <div class="company-detail">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Company Details</h2>
      <button class="btn btn-outline-secondary" @click="goBack">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Companies
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading company details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchCompanyDetails">Retry</button>
    </div>

    <!-- Company Details -->
    <div v-else class="row">
      <!-- Left Column - Company Profile -->
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-building me-2"></i>
              Company Profile
            </h5>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <div class="company-logo bg-light rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 100px; height: 100px;">
                <i class="bi bi-building fs-1 text-secondary"></i>
              </div>
              <h4>{{ company.company_name }}</h4>
              <span class="badge fs-6 px-3 py-2" :class="getStatusClass(company)">
                {{ formatStatus(company.approval_status) }}
                <span v-if="company.is_blacklisted">(Blacklisted)</span>
              </span>
            </div>

            <table class="table table-sm">
              <tbody>  <!-- ✅ Added tbody -->
                <tr>
                  <th style="width: 40%;">Company ID</th>
                  <td>{{ company.id }}</td>
                </tr>
                <tr>
                  <th>Industry</th>
                  <td>{{ company.industry || 'N/A' }}</td>
                </tr>
                <tr>
                  <th>Location</th>
                  <td>{{ company.location || 'N/A' }}</td>
                </tr>
                <tr>
                  <th>Website</th>
                  <td>
                    <a v-if="company.website" :href="company.website" target="_blank" class="text-decoration-none">
                      {{ company.website }}
                    </a>
                    <span v-else>N/A</span>
                  </td>
                </tr>
                <tr>
                  <th>Registered On</th>
                  <td>{{ formatDate(company.created_at) }}</td>
                </tr>
              </tbody>
            </table>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 mt-3">
              <button 
                v-if="company.approval_status === 'pending'"
                class="btn btn-success" 
                @click="approveCompany"
                :disabled="processingAction"
              >
                <span v-if="processingAction" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-lg me-2"></i>
                Approve Company
              </button>
              <button 
                v-if="company.approval_status === 'pending'"
                class="btn btn-danger" 
                @click="rejectCompany"
                :disabled="processingAction"
              >
                <i class="bi bi-x-lg me-2"></i>
                Reject Company
              </button>
              <button 
                v-if="company.approval_status === 'approved' && !company.is_blacklisted"
                class="btn btn-dark" 
                @click="blacklistCompany"
                :disabled="processingAction"
              >
                <i class="bi bi-lock-fill me-2"></i>
                Blacklist Company
              </button>
              <button 
                v-if="company.is_blacklisted"
                class="btn btn-warning" 
                @click="activateCompany"
                :disabled="processingAction"
              >
                <i class="bi bi-unlock-fill me-2"></i>
                Activate Company
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Additional Info -->
      <div class="col-md-8 mb-4">
        <!-- HR Contact Card -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-person-badge me-2"></i>
              HR Contact Information
            </h5>
          </div>
          <div class="card-body">
            <table class="table">
              <tbody>  <!-- ✅ Added tbody -->
                <tr>
                  <th style="width: 30%;">HR Name</th>
                  <td>{{ company.hr_name }}</td>
                </tr>
                <tr>
                  <th>HR Email</th>
                  <td>
                    <a :href="'mailto:' + company.hr_email" class="text-decoration-none">
                      {{ company.hr_email }}
                    </a>
                  </td>
                </tr>
                <tr>
                  <th>HR Phone</th>
                  <td>{{ company.hr_phone || 'N/A' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Company Description -->
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">
              <i class="bi bi-file-text me-2"></i>
              Company Description
            </h5>
          </div>
          <div class="card-body">
            <p class="mb-0">{{ company.company_description || 'No description provided.' }}</p>
          </div>
        </div>

        <!-- Drives by this Company -->
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-briefcase me-2"></i>
              Placement Drives
              <span class="badge bg-primary ms-2">{{ drives.length }}</span>
            </h5>
          </div>
          <div class="card-body">
            <div v-if="drives.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-briefcase fs-1 d-block mb-3"></i>
              <p class="mb-0">No drives posted yet</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Drive Name</th>
                    <th>Job Title</th>
                    <th>Deadline</th>
                    <th>Status</th>
                    <th>Applications</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="drive in drives" :key="drive.id">
                    <td>{{ drive.drive_name }}</td>
                    <td>{{ drive.job_title }}</td>
                    <td>{{ formatDate(drive.application_deadline) }}</td>
                    <td>
                      <span class="badge" :class="getDriveStatusClass(drive.status)">
                        {{ formatStatus(drive.status) }}
                      </span>
                    </td>
                    <td>{{ drive.application_count || 0 }}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click="viewDrive(drive.id)">
                        <i class="bi bi-eye me-1"></i>
                        View
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { adminAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()
const messageStore = useMessageStore()

const companyId = route.params.id

// State
const loading = ref(true)
const error = ref(null)
const processingAction = ref(false)
const company = ref({})
const drives = ref([])

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

const getStatusClass = (company) => {
  if (company.is_blacklisted) return 'bg-dark'
  switch(company.approval_status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getDriveStatusClass = (status) => {
  switch(status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    case 'closed': return 'bg-secondary'
    default: return 'bg-secondary'
  }
}

// Fetch Company Details
const fetchCompanyDetails = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await adminAPI.getCompanyDetails(companyId)
    company.value = response.data.company || {}
    drives.value = response.data.drives || []
  } catch (err) {
    console.error('Error fetching company details:', err)
    error.value = err.response?.data?.message || 'Failed to load company details'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Actions
const approveCompany = async () => {
  if (!confirm('Approve this company?')) return
  
  processingAction.value = true
  try {
    await adminAPI.approveCompany(companyId)
    messageStore.updateSuccessMessages('Company approved')
    await fetchCompanyDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Approval failed')
  } finally {
    processingAction.value = false
  }
}

const rejectCompany = async () => {
  const reason = prompt('Enter rejection reason:')
  if (!reason) return
  
  processingAction.value = true
  try {
    await adminAPI.rejectCompany(companyId, { reason })
    messageStore.updateSuccessMessages('Company rejected')
    await fetchCompanyDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Rejection failed')
  } finally {
    processingAction.value = false
  }
}

const blacklistCompany = async () => {
  const reason = prompt('Enter blacklist reason:')
  if (!reason) return
  
  processingAction.value = true
  try {
    await adminAPI.blacklistCompany(companyId, { reason })
    messageStore.updateSuccessMessages('Company blacklisted')
    await fetchCompanyDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Blacklist failed')
  } finally {
    processingAction.value = false
  }
}

const activateCompany = async () => {
  if (!confirm('Activate this company?')) return
  
  processingAction.value = true
  try {
    await adminAPI.activateCompany(companyId)
    messageStore.updateSuccessMessages('Company activated')
    await fetchCompanyDetails()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Activation failed')
  } finally {
    processingAction.value = false
  }
}

const viewDrive = (driveId) => {
  router.push(`/admin/drives/${driveId}`)
}

const goBack = () => {
  router.push('/admin/companies')
}

onMounted(() => {
  fetchCompanyDetails()
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

.company-logo {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border: 2px solid #dee2e6;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  width: 40%;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-weight: 500;
  border-radius: 2rem;
}

.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  padding: 1rem 1.5rem;
  border-radius: 1rem 1rem 0 0 !important;
}

.btn {
  transition: all 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>