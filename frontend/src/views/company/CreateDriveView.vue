<!-- frontend/src/views/company/CreateDriveView.vue -->
<template>
  <div class="create-drive">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">Create New Drive</h2>
      <router-link to="/company/drives" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Drives
      </router-link>
    </div>

    <!-- Access Denied for Unapproved or Blacklisted -->
    <div v-if="!canCreateDrive" class="alert" :class="accessAlertClass">
      <i class="bi" :class="accessIconClass" fs-1 d-block mb-3></i>
      <h3 class="mb-3">{{ accessTitle }}</h3>
      <p class="lead mb-4">{{ accessMessage }}</p>
      <router-link to="/company/dashboard" class="btn" :class="accessButtonClass">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Dashboard
      </router-link>
    </div>

    <!-- Create Drive Form - Only show if approved -->
    <div v-else class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Drive Details</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm">
              <!-- Basic Details -->
              <div class="mb-3">
                <label for="driveName" class="form-label">Drive Name <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="driveName" v-model="form.drive_name" required>
              </div>

              <div class="mb-3">
                <label for="jobTitle" class="form-label">Job Title <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="jobTitle" v-model="form.job_title" required>
              </div>

              <div class="mb-3">
                <label for="jobDescription" class="form-label">Job Description <span class="text-danger">*</span></label>
                <textarea class="form-control" id="jobDescription" rows="5" v-model="form.job_description" required></textarea>
              </div>

              <!-- Eligibility -->
              <h6 class="mt-4 mb-3">Eligibility Criteria</h6>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="minCGPA" class="form-label">Minimum CGPA</label>
                  <input type="number" step="0.1" min="0" max="10" class="form-control" id="minCGPA" v-model="form.min_cgpa">
                </div>
                <div class="col-md-6">
                  <label for="allowedBranches" class="form-label">Allowed Branches</label>
                  <input type="text" class="form-control" id="allowedBranches" v-model="form.allowed_branches" placeholder="e.g., CSE, IT, ECE">
                  <small class="text-muted">Comma separated values</small>
                </div>
              </div>

              <div class="mb-3">
                <label for="eligibilityCriteria" class="form-label">Additional Eligibility Criteria</label>
                <textarea class="form-control" id="eligibilityCriteria" rows="3" v-model="form.eligibility_criteria"></textarea>
              </div>

              <!-- Dates -->
              <h6 class="mt-4 mb-3">Important Dates</h6>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="applicationDeadline" class="form-label">Application Deadline <span class="text-danger">*</span></label>
                  <input type="datetime-local" class="form-control" id="applicationDeadline" v-model="form.application_deadline" required>
                </div>
                <div class="col-md-6">
                  <label for="driveDate" class="form-label">Drive Date</label>
                  <input type="datetime-local" class="form-control" id="driveDate" v-model="form.drive_date">
                </div>
              </div>

              <div class="mt-4">
                <button type="submit" class="btn btn-success" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-check-lg me-2"></i>
                  Create Drive
                </button>
                <router-link to="/company/drives" class="btn btn-outline-secondary ms-2">
                  Cancel
                </router-link>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Important Notes</h5>
          </div>
          <div class="card-body">
            <ul class="list-unstyled">
              <li class="mb-2">
                <i class="bi bi-check-circle-fill text-success me-2"></i>
                Drives need admin approval before students can see them
              </li>
              <li class="mb-2">
                <i class="bi bi-info-circle-fill text-info me-2"></i>
                Fill all required fields marked with *
              </li>
              <li class="mb-2">
                <i class="bi bi-clock-fill text-warning me-2"></i>
                Set appropriate deadlines
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

const submitting = ref(false)
const companyProfile = ref({})

// Check if company can create drive
const canCreateDrive = computed(() => {
  return companyProfile.value?.approval_status === 'approved' && !companyProfile.value?.is_blacklisted
})

// Access denied messages
const accessTitle = computed(() => {
  if (companyProfile.value?.is_blacklisted) return 'Account Blacklisted'
  return 'Pending Approval'
})

const accessMessage = computed(() => {
  if (companyProfile.value?.is_blacklisted) {
    return 'Your company account has been blacklisted. You cannot create drives.'
  }
  return 'Your company is awaiting admin approval. You can create drives only after approval.'
})

const accessAlertClass = computed(() => {
  if (companyProfile.value?.is_blacklisted) return 'alert-danger'
  return 'alert-warning'
})

const accessIconClass = computed(() => {
  if (companyProfile.value?.is_blacklisted) return 'bi-lock-fill'
  return 'bi-clock-history'
})

const accessButtonClass = computed(() => {
  if (companyProfile.value?.is_blacklisted) return 'btn-danger'
  return 'btn-warning'
})

// Form data
const form = ref({
  drive_name: '',
  job_title: '',
  job_description: '',
  eligibility_criteria: '',
  min_cgpa: '',
  allowed_branches: '',
  application_deadline: '',
  drive_date: ''
})

// Fetch company profile to check status
const fetchCompanyProfile = async () => {
  try {
    const response = await companyAPI.getProfile()
    companyProfile.value = response.data.profile || {}
  } catch (err) {
    console.error('Error fetching company profile:', err)
  }
}

// Submit form
const submitForm = async () => {
  if (!canCreateDrive.value) {
    messageStore.updateErrorMessages('You cannot create drives at this time.')
    return
  }

  submitting.value = true
  try {
    await companyAPI.createDrive(form.value)
    messageStore.updateSuccessMessages('Drive created successfully. Pending admin approval.')
    router.push('/company/drives')
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to create drive')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCompanyProfile()
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

.card {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid #eff2f5;
  border-radius: 1rem 1rem 0 0 !important;
}

.form-label {
  font-weight: 500;
  color: #495057;
}

.form-control:focus {
  border-color: #198754;
  box-shadow: 0 0 0 0.2rem rgba(25, 135, 84, 0.25);
}
</style>