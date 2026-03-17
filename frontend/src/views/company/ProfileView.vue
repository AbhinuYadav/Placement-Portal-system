<!-- frontend/src/views/company/ProfileView.vue -->
<template>
  <div class="profile">
    <h2 class="dashboard-title mb-4">Company Profile</h2>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading profile...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Profile Form -->
    <div v-else class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Company Information</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Company Name</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" v-model="form.company_name" required>
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Description</label>
                <div class="col-sm-9">
                  <textarea class="form-control" rows="3" v-model="form.company_description"></textarea>
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Website</label>
                <div class="col-sm-9">
                  <input type="url" class="form-control" v-model="form.website">
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Industry</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" v-model="form.industry">
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">Location</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" v-model="form.location">
                </div>
              </div>

              <hr>
              <h6 class="mb-3">HR Contact Information</h6>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">HR Name</label>
                <div class="col-sm-9">
                  <input type="text" class="form-control" v-model="form.hr_name" required>
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">HR Email</label>
                <div class="col-sm-9">
                  <input type="email" class="form-control" v-model="form.hr_email" required>
                </div>
              </div>

              <div class="row mb-3">
                <label class="col-sm-3 col-form-label">HR Phone</label>
                <div class="col-sm-9">
                  <input type="tel" class="form-control" v-model="form.hr_phone">
                </div>
              </div>

              <div class="row">
                <div class="col-sm-9 offset-sm-3">
                  <button type="submit" class="btn btn-success" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-check-lg me-2"></i>
                    Update Profile
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Status</h5>
          </div>
          <div class="card-body">
            <p><strong>Approval Status:</strong></p>
            <p>
              <span class="badge fs-6 px-3 py-2" :class="getStatusClass(profile)">
                {{ profile.approval_status }}
              </span>
            </p>
            <p class="text-muted small mt-3">
              <i class="bi bi-info-circle me-1"></i>
              Companies need admin approval to activate their drives.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'
import { companyAPI } from '@/services/api'

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const profile = ref({})
const form = ref({
  company_name: '',
  company_description: '',
  website: '',
  industry: '',
  location: '',
  hr_name: '',
  hr_email: '',
  hr_phone: ''
})

const getStatusClass = (profile) => {
  switch(profile.approval_status) {
    case 'approved': return 'bg-success'
    case 'pending': return 'bg-warning text-dark'
    case 'rejected': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const fetchProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await companyAPI.getProfile()
    profile.value = response.data.profile || {}
    
    // Populate form
    form.value = {
      company_name: profile.value.company_name || '',
      company_description: profile.value.company_description || '',
      website: profile.value.website || '',
      industry: profile.value.industry || '',
      location: profile.value.location || '',
      hr_name: profile.value.hr_name || '',
      hr_email: profile.value.hr_email || '',
      hr_phone: profile.value.hr_phone || ''
    }
    
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load profile'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  saving.value = true
  try {
    await companyAPI.updateProfile(form.value)
    messageStore.updateSuccessMessages('Profile updated successfully')
    await fetchProfile()
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProfile()
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

.badge {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-weight: 500;
}
</style>