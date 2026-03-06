<template>
  <div class="auth-page min-h-screen flex">
    <!-- Left: Gradient + branding -->
    <div class="auth-brand hidden lg:flex flex-col justify-center px-12 xl:px-20">
      <div class="auth-brand-inner">
        <div class="logo-placeholder">
          <i class="pi pi-wallet text-5xl text-white/90" />
        </div>
        <h1 class="auth-title">SmartFinance</h1>
        <p class="auth-subtitle">
          Take control of your money. Track income, expenses, and reach your goals.
        </p>
      </div>
    </div>

    <!-- Right: Form -->
    <div class="auth-form-wrapper flex-1 flex items-center justify-center p-6 sm:p-10">
      <div class="auth-card w-full max-w-md">
        <div class="text-center mb-8 lg:hidden">
          <div class="logo-placeholder inline-flex mb-4">
            <i class="pi pi-wallet text-4xl text-white/90" />
          </div>
          <h1 class="text-xl font-bold text-surface-800 dark:text-surface-100">SmartFinance</h1>
        </div>
        <h2 class="auth-heading">Welcome back</h2>
        <p class="auth-desc">Sign in to your account to continue.</p>

        <form @submit.prevent="handleLogin" class="auth-form mt-8">
          <div class="input-float-group">
            <InputText
              id="username"
              v-model="username"
              class="input-float w-full"
              :class="{ 'filled': username }"
              required
            />
            <label for="username" class="input-float-label">Username</label>
          </div>
          <div class="input-float-group mt-6" :class="{ 'filled': password }">
            <Password
              id="password"
              v-model="password"
              class="input-float w-full p-password-input"
              :feedback="false"
              toggleMask
              required
            />
            <label for="password" class="input-float-label">Password</label>
          </div>
          <div v-if="error" class="mt-4 text-red-600 text-sm font-medium">{{ error }}</div>
          <Button
            type="submit"
            label="Login"
            class="auth-btn w-full mt-8"
            :loading="loading"
          />
          <p class="auth-footer">
            Don't have an account?
            <NuxtLink to="/register" class="auth-link">Register</NuxtLink>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'

definePageMeta({
  layout: false,
})

const { login } = useAuth()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  const result = await login(username.value, password.value)
  loading.value = false

  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Login failed'
  }
}
</script>

<style scoped>
.auth-page {
  background: linear-gradient(135deg, #0f172a 0%, #0e7490 50%, #059669 100%);
  background-size: 400% 400%;
  animation: gradientShift 12s ease infinite;
}
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.auth-brand {
  flex: 1;
  max-width: 50%;
  min-height: 100vh;
}
.auth-brand-inner {
  max-width: 380px;
}
.logo-placeholder {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}
.auth-title {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
  margin-bottom: 0.75rem;
}
.auth-subtitle {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
}

.auth-form-wrapper {
  background: rgba(255, 255, 255, 0.97);
}
.dark .auth-form-wrapper {
  background: rgba(15, 23, 42, 0.97);
}

.auth-card {
  padding: 2.5rem;
}
.auth-heading {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--p-text-color);
  letter-spacing: -0.02em;
}
.auth-desc {
  margin-top: 0.5rem;
  color: var(--p-text-muted-color);
  font-size: 0.95rem;
}

/* Floating label inputs */
.input-float-group {
  position: relative;
}
.input-float {
  border: 1px solid var(--p-input-border-color);
  border-radius: 10px;
  padding: 1rem 1rem 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-float:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.2);
}
.input-float-label {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--p-text-muted-color);
  font-size: 1rem;
  pointer-events: none;
  transition: top 0.2s, font-size 0.2s, color 0.2s;
}
.input-float:focus + .input-float-label,
.input-float.filled + .input-float-label {
  top: 0.65rem;
  font-size: 0.75rem;
  color: #059669;
}
.input-float-group :deep(.p-password-input) {
  border: none;
  padding: 0;
  background: transparent;
}
.input-float-group :deep(.p-password) {
  border: 1px solid var(--p-input-border-color);
  border-radius: 10px;
  padding: 1rem 1rem 0.5rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-float-group :deep(.p-password:focus-within) {
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.2);
}
.input-float-group :deep(.p-password .p-icon-field) {
  width: 100%;
}
.input-float-group.filled .input-float-label {
  top: 0.65rem;
  font-size: 0.75rem;
  color: #059669;
}

.auth-btn {
  padding: 0.875rem 1.5rem;
  font-weight: 600;
  font-size: 1rem;
  border-radius: 10px;
  background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
  border: none !important;
  transition: transform 0.2s, box-shadow 0.2s;
}
.auth-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(5, 150, 105, 0.35);
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--p-text-muted-color);
}
.auth-link {
  color: #059669;
  font-weight: 600;
  margin-left: 0.25rem;
}
.auth-link:hover {
  text-decoration: underline;
}
</style>
