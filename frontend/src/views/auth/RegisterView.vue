<!-- frontend/src/views/auth/RegisterView.vue -->
<template>
  <div class="register-page">
    <div class="register-card">
      <div class="text-center mb-4">
        <h2 class="fw-bold" style="color: #1266f1;">Create Account</h2>
        <p class="text-muted">Join the Placement Portal</p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="alert alert-success">
        <i class="bi bi-check-circle-fill me-2"></i>
        {{ successMessage }}
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ errorMessage }}
      </div>

      <!-- Role Selection -->
      <div class="d-flex justify-content-center mb-4">
        <div class="btn-group" role="group">
          <input type="radio" class="btn-check" name="role" id="student" value="student" v-model="role" autocomplete="off">
          <label class="btn btn-outline-primary rounded-start-pill px-4 px-md-5 py-3" for="student">
            <i class="bi bi-mortarboard-fill me-2"></i>Student
          </label>

          <input type="radio" class="btn-check" name="role" id="company" value="company" v-model="role" autocomplete="off">
          <label class="btn btn-outline-primary rounded-end-pill px-4 px-md-5 py-3" for="company">
            <i class="bi bi-building me-2"></i>Company
          </label>
        </div>
      </div>

      <form @submit.prevent="handleRegister">
        <!-- Account Details -->
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="form-floating">
              <input 
                type="email" 
                class="form-control" 
                id="email" 
                v-model="email" 
                placeholder="name@example.com" 
                required
              >
              <label for="email">Email address</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                class="form-control" 
                id="password" 
                v-model="password" 
                placeholder="Password" 
                required
              >
              <label for="password">Password</label>
            </div>
            <small class="text-muted">8+ chars, 1 uppercase, 1 lowercase, 1 number</small>
          </div>
        </div>

        <!-- Student Fields -->
        <div v-if="role === 'student'" class="row g-3">
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" id="name" v-model="studentProfile.name" placeholder="Full Name" required>
              <label for="name">Full Name</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" id="roll" v-model="studentProfile.roll_number" placeholder="Roll Number" required>
              <label for="roll">Roll Number</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <select class="form-select" id="branch" v-model="studentProfile.branch" required>
                <option value="" disabled selected></option>
                <option value="Computer Science">Computer Science</option>
                <option value="Information Technology">Information Technology</option>
                <option value="Electronics">Electronics</option>
                <option value="Mechanical">Mechanical</option>
                <option value="Civil">Civil</option>
              </select>
              <label for="branch">Branch</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <input type="number" step="0.01" class="form-control" id="cgpa" v-model="studentProfile.cgpa" placeholder="CGPA" required>
              <label for="cgpa">CGPA</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <select class="form-select" id="year" v-model="studentProfile.graduation_year" required>
                <option value="" disabled selected></option>
                <option value="2026">2026</option>
                <option value="2027">2027</option>
                <option value="2028">2028</option>
              </select>
              <label for="year">Graduation Year</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="tel" class="form-control" id="phone" v-model="studentProfile.phone" placeholder="Phone (Optional)">
              <label for="phone">Phone (Optional)</label>
            </div>
          </div>
        </div>

        <!-- Company Fields -->
        <div v-if="role === 'company'" class="row g-3">
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" id="company_name" v-model="companyProfile.company_name" placeholder="Company Name" required>
              <label for="company_name">Company Name</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" id="industry" v-model="companyProfile.industry" placeholder="Industry">
              <label for="industry">Industry</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <input type="text" class="form-control" id="hr_name" v-model="companyProfile.hr_name" placeholder="HR Name" required>
              <label for="hr_name">HR Name</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <input type="email" class="form-control" id="hr_email" v-model="companyProfile.hr_email" placeholder="HR Email" required>
              <label for="hr_email">HR Email</label>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-floating">
              <input type="tel" class="form-control" id="hr_phone" v-model="companyProfile.hr_phone" placeholder="HR Phone">
              <label for="hr_phone">HR Phone</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="url" class="form-control" id="website" v-model="companyProfile.website" placeholder="Website">
              <label for="website">Website</label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-floating">
              <input type="text" class="form-control" id="location" v-model="companyProfile.location" placeholder="Location">
              <label for="location">Location</label>
            </div>
          </div>
        </div>

        <button 
          type="submit" 
          class="btn btn-primary w-100 py-3 mt-4" 
          :disabled="authStore.loading"
        >
          <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2"></span>
          <span v-else>Create Account</span>
        </button>

        <div class="text-center mt-3">
          <p class="mb-0">
            Already have an account? 
            <router-link to="/login" class="fw-bold text-decoration-none" style="color: #1266f1;">
              Sign in
            </router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()
const authStore = useAuthStore()
const messageStore = useMessageStore()

const email = ref('')
const password = ref('')
const role = ref('student')
const showPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Student profile
const studentProfile = ref({
  name: '',
  roll_number: '',
  branch: '',
  cgpa: '',
  graduation_year: '',
  phone: ''
})

// Company profile
const companyProfile = ref({
  company_name: '',
  hr_name: '',
  hr_email: '',
  hr_phone: '',
  website: '',
  industry: '',
  location: '',
  description: ''
})

const handleRegister = async () => {
  successMessage.value = ''
  errorMessage.value = ''
  
  const userData = {
    email: email.value,
    password: password.value,
    role: role.value,
    profile: role.value === 'student' ? studentProfile.value : companyProfile.value
  }
  
  console.log('📤 Submitting registration:', userData)
  
  const result = await authStore.register(userData)
  
  if (result.success) {
    successMessage.value = result.message
    messageStore.updateSuccessMessages(result.message)
    setTimeout(() => router.push('/login'), 2000)
  } else {
    errorMessage.value = result.error
    messageStore.updateErrorMessages(result.error)
  }
}
</script>

<style scoped>
.register-page {
  width: 100vw;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 1rem;
  padding: 2.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 900px;
}
</style>