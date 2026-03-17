<!-- frontend/src/views/student/ProfileView.vue -->
<template>
  <div class="profile">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="dashboard-title">My Profile</h2>
      <button 
        class="btn btn-outline-primary" 
        @click="toggleEditMode"
        v-if="!editMode"
      >
        <i class="bi bi-pencil me-2"></i>
        Edit Profile
      </button>
      <div v-else>
        <button class="btn btn-success me-2" @click="saveProfile" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-check-lg me-2"></i>
          Save Changes
        </button>
        <button class="btn btn-outline-secondary" @click="cancelEdit">
          Cancel
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading profile...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button class="btn btn-sm btn-outline-danger ms-3" @click="fetchProfile">Retry</button>
    </div>

    <!-- Profile Content -->
    <div v-else class="row">
      <!-- Left Column - Profile Card -->
      <div class="col-md-4 mb-4">
        <div class="card text-center">
          <div class="card-body">
            <div class="profile-avatar bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 120px; height: 120px;">
              <span class="fs-1 fw-bold">{{ initials }}</span>
            </div>
            
            <h3>{{ profile.name }}</h3>
            <p class="text-muted mb-2">
              <i class="bi bi-envelope me-1"></i>
              {{ profile.email }}
            </p>
            <p class="text-muted mb-3">
              <i class="bi bi-telephone me-1"></i>
              {{ profile.phone || 'Not provided' }}
            </p>
            
            <div class="d-flex justify-content-center gap-2 mb-3">
              <span class="badge bg-primary">{{ profile.branch }}</span>
              <span class="badge bg-success">CGPA: {{ profile.cgpa }}</span>
              <span class="badge bg-info">Class of {{ profile.graduation_year }}</span>
            </div>

            <!-- Resume Status -->
            <div class="border-top pt-3 mt-3">
              <h6 class="mb-2">Resume</h6>
              <div v-if="profile.has_resume" class="d-flex align-items-center justify-content-center">
                <i class="bi bi-file-pdf text-danger fs-4 me-2"></i>
                <span>Resume uploaded</span>
              </div>
              <div v-else class="text-muted">
                <i class="bi bi-file-earmark me-1"></i>
                No resume uploaded
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column - Details -->
      <div class="col-md-8 mb-4">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Personal Information</h5>
          </div>
          <div class="card-body">
            <!-- View Mode -->
            <div v-if="!editMode" class="row">
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Full Name</label>
                <p class="fw-bold mb-0">{{ profile.name }}</p>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Roll Number</label>
                <p class="fw-bold mb-0">{{ profile.roll_number }}</p>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Email</label>
                <p class="fw-bold mb-0">{{ profile.email }}</p>
              </div>
              <div class="col-md-6 mb-3">
                <label class="text-muted small">Phone</label>
                <p class="fw-bold mb-0">{{ profile.phone || 'Not provided' }}</p>
              </div>
              <div class="col-md-4 mb-3">
                <label class="text-muted small">Branch</label>
                <p class="fw-bold mb-0">{{ profile.branch }}</p>
              </div>
              <div class="col-md-4 mb-3">
                <label class="text-muted small">CGPA</label>
                <p class="fw-bold mb-0">{{ profile.cgpa }}</p>
              </div>
              <div class="col-md-4 mb-3">
                <label class="text-muted small">Graduation Year</label>
                <p class="fw-bold mb-0">{{ profile.graduation_year }}</p>
              </div>
              <div class="col-12 mb-3">
                <label class="text-muted small">Alternate Email</label>
                <p class="fw-bold mb-0">{{ profile.alternate_email || 'Not provided' }}</p>
              </div>
            </div>

            <!-- Edit Mode -->
            <div v-else>
              <form @submit.prevent="saveProfile">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-control" v-model="editForm.name" required>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Roll Number</label>
                    <input type="text" class="form-control" v-model="editForm.roll_number" readonly disabled>
                    <small class="text-muted">Roll number cannot be changed</small>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" v-model="editForm.email" readonly disabled>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-control" v-model="editForm.phone">
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label">Branch</label>
                    <select class="form-select" v-model="editForm.branch" required>
                      <option value="Computer Science">Computer Science</option>
                      <option value="Information Technology">Information Technology</option>
                      <option value="Electronics">Electronics</option>
                      <option value="Mechanical">Mechanical</option>
                      <option value="Civil">Civil</option>
                    </select>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label">CGPA</label>
                    <input type="number" step="0.01" min="0" max="10" class="form-control" v-model="editForm.cgpa" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label">Graduation Year</label>
                    <select class="form-select" v-model="editForm.graduation_year" required>
                      <option value="2026">2026</option>
                      <option value="2027">2027</option>
                      <option value="2028">2028</option>
                    </select>
                  </div>
                  <div class="col-12 mb-3">
                    <label class="form-label">Alternate Email</label>
                    <input type="email" class="form-control" v-model="editForm.alternate_email">
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Resume Upload Card -->
        <div class="card mt-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">Resume</h5>
          </div>
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <div v-if="profile.has_resume" class="d-flex align-items-center">
                  <i class="bi bi-file-pdf text-danger fs-1 me-3"></i>
                  <div>
                    <h6 class="mb-1">Resume.pdf</h6>
                    <p class="text-muted small mb-0">Uploaded on {{ profile.resume_uploaded_at || 'N/A' }}</p>
                  </div>
                </div>
                <div v-else class="text-muted">
                  <i class="bi bi-file-earmark fs-1 d-block mb-2"></i>
                  <p class="mb-0">No resume uploaded yet</p>
                </div>
              </div>
              <div class="col-md-4 text-end">
                <button class="btn btn-outline-primary" @click="triggerFileUpload">
                  <i class="bi bi-upload me-2"></i>
                  Upload New
                </button>
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="d-none" 
                  accept=".pdf,.doc,.docx"
                  @change="uploadResume"
                >
              </div>
            </div>
            <small class="text-muted d-block mt-2">
              <i class="bi bi-info-circle me-1"></i>
              Accepted formats: PDF, DOC, DOCX. Max size: 5MB
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useMessageStore } from '@/stores/message'
import { studentAPI } from '@/services/api'

const messageStore = useMessageStore()

// State
const loading = ref(true)
const error = ref(null)
const saving = ref(false)
const editMode = ref(false)
const profile = ref({})
const editForm = ref({})

// File upload
const fileInput = ref(null)

// Computed
const initials = computed(() => {
  if (!profile.value.name) return '?'
  return profile.value.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// Fetch Profile
const fetchProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await studentAPI.getProfile()
    profile.value = response.data.profile || {}
    editForm.value = { ...profile.value }
  } catch (err) {
    console.error('Error fetching profile:', err)
    error.value = err.response?.data?.message || 'Failed to load profile'
    messageStore.updateErrorMessages(error.value)
  } finally {
    loading.value = false
  }
}

// Edit Mode
const toggleEditMode = () => {
  editForm.value = { ...profile.value }
  editMode.value = true
}

const cancelEdit = () => {
  editMode.value = false
}

// Save Profile
const saveProfile = async () => {
  saving.value = true
  try {
    await studentAPI.updateProfile(editForm.value)
    messageStore.updateSuccessMessages('Profile updated successfully')
    profile.value = { ...editForm.value }
    editMode.value = false
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

// Resume Upload
const triggerFileUpload = () => {
  fileInput.value.click()
}

const uploadResume = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    messageStore.updateErrorMessages('File size must be less than 5MB')
    return
  }
  
  // Validate file type
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  if (!allowedTypes.includes(file.type)) {
    messageStore.updateErrorMessages('Only PDF and DOC files are allowed')
    return
  }
  
  const formData = new FormData()
  formData.append('resume', file)
  
  try {
    await studentAPI.uploadResume(formData)
    messageStore.updateSuccessMessages('Resume uploaded successfully')
    await fetchProfile() // Refresh profile
  } catch (err) {
    messageStore.updateErrorMessages(err.response?.data?.message || 'Failed to upload resume')
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile-avatar {
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 3px solid white;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
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

.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.25rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
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
</style>