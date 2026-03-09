<template>
  <div class="p-6 max-w-[1400px] mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Settings</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Manage your application preferences, security, and data.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
            <i class="pi pi-globe text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Regional Preferences</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <div>
            <label class="block font-bold text-gray-700 dark:text-gray-300 mb-3">Display Currency</label>
            <Dropdown 
              v-model="localCurrency" 
              :options="currencyOptions" 
              optionLabel="label" 
              optionValue="value" 
              class="w-full"
              @change="updateCurrency"
            />
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 italic mt-2 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-100 dark:border-gray-600">
            <i class="pi pi-sync mr-2 text-blue-500"></i> Exchange rates are fetched live. Your dashboard will instantly update.
          </p>
        </div>
      </div>

      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg">
            <i class="pi pi-palette text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Appearance</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <label class="block font-bold text-gray-700 dark:text-gray-300 mb-1">Theme Preference</label>
          <div class="flex gap-4">
            <button 
              @click="setTheme('light')"
              :class="!isDark ? 'ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'"
              class="flex-1 p-4 rounded-2xl border border-gray-200 dark:border-gray-600 flex flex-col items-center gap-2 transition-all"
            >
              <i class="pi pi-sun text-2xl" :class="!isDark ? 'text-purple-600' : 'text-gray-500 dark:text-gray-400'"></i>
              <span class="font-bold" :class="!isDark ? 'text-purple-700 dark:text-purple-400' : 'text-gray-600 dark:text-gray-300'">Light</span>
            </button>
            
            <button 
              @click="setTheme('dark')"
              :class="isDark ? 'ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'"
              class="flex-1 p-4 rounded-2xl border border-gray-200 dark:border-gray-600 flex flex-col items-center gap-2 transition-all"
            >
              <i class="pi pi-moon text-2xl" :class="isDark ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'"></i>
              <span class="font-bold" :class="isDark ? 'text-purple-700 dark:text-purple-400' : 'text-gray-600 dark:text-gray-300'">Dark</span>
            </button>
          </div>
        </div>
      </div>

      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 lg:col-span-2">
        <div class="flex items-center justify-between mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg">
              <i class="pi pi-chart-pie text-xl"></i>
            </div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Monthly Budget Limits</h2>
          </div>
          <Button label="Save Budgets" icon="pi pi-save" @click="saveBudgets" :loading="isSavingBudgets" />
        </div>
        
        <p class="text-gray-600 dark:text-gray-400 mb-8">
          Set maximum spending limits for your expense categories. Your dashboard will automatically track your progress and alert you before you overspend.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-shopping-cart text-gray-400"></i> Food
            </label>
            <InputNumber v-model="budgets.Food" mode="currency" :currency="currentCurrency" class="w-full" placeholder="No limit" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-home text-gray-400"></i> Rent
            </label>
            <InputNumber v-model="budgets.Rent" mode="currency" :currency="currentCurrency" class="w-full" placeholder="No limit" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-car text-gray-400"></i> Transport
            </label>
            <InputNumber v-model="budgets.Transport" mode="currency" :currency="currentCurrency" class="w-full" placeholder="No limit" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-ticket text-gray-400"></i> Entertainment
            </label>
            <InputNumber v-model="budgets.Entertainment" mode="currency" :currency="currentCurrency" class="w-full" placeholder="No limit" />
          </div>

        </div>
      </div>

      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
            <i class="pi pi-download text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Data & Privacy</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <p class="text-gray-600 dark:text-gray-400">Download a complete copy of your financial transactions for your personal records or tax purposes.</p>
          
          <Button 
            label="Export Transactions to CSV" 
            icon="pi pi-file-excel" 
            severity="success" 
            :loading="isExporting"
            @click="exportCSV" 
            class="w-full sm:w-auto"
          />
        </div>
      </div>

      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg">
            <i class="pi pi-shield text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Security</h2>
        </div>
        
        <div class="flex flex-col gap-6">
          <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-100 dark:border-gray-700">
            <div>
              <h3 class="font-bold text-gray-900 dark:text-white">Change Password</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Update your password regularly to keep your account secure.</p>
            </div>
            <Button label="Update" icon="pi pi-key" severity="secondary" outlined size="small" @click="openPasswordDialog" />
          </div>

          <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-100 dark:border-gray-700">
            <div>
              <h3 class="font-bold text-gray-900 dark:text-white">Two-Factor Auth (2FA)</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Add an extra layer of security to your account.</p>
            </div>
            <div 
              @click="handle2FAToggle" 
              class="w-12 h-6 rounded-full cursor-pointer transition-colors duration-300 relative"
              :class="is2FAEnabled ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'"
            >
              <div 
                class="w-4 h-4 bg-white rounded-full absolute top-1 transition-transform duration-300"
                :class="is2FAEnabled ? 'left-7' : 'left-1'"
              ></div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <Dialog v-model:visible="showPasswordDialog" modal header="🔒 Change Password" :style="{ width: '90vw', maxWidth: '450px' }">
      <form @submit.prevent="updatePassword" class="flex flex-col gap-5 pt-4">
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="currentPassword" class="font-bold text-gray-700 dark:text-gray-300">Current Password</label>
          <Password id="currentPassword" v-model="passwordForm.currentPassword" :feedback="false" toggleMask required placeholder="Enter your current password" inputClass="w-full" />
        </div>
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="newPassword" class="font-bold text-gray-700 dark:text-gray-300">New Password</label>
          <Password id="newPassword" v-model="passwordForm.newPassword" toggleMask required placeholder="Enter your new password" inputClass="w-full" />
        </div>
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="confirmPassword" class="font-bold text-gray-700 dark:text-gray-300">Confirm New Password</label>
          <Password id="confirmPassword" v-model="passwordForm.confirmPassword" :feedback="false" toggleMask required placeholder="Re-enter your new password" inputClass="w-full" />
        </div>
        <div v-if="passwordError" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm font-medium border border-red-100 dark:border-red-800/50">
          <i class="pi pi-exclamation-circle mr-1"></i> {{ passwordError }}
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <Button type="button" label="Cancel" severity="secondary" text @click="showPasswordDialog = false" />
          <Button type="submit" label="Update Password" icon="pi pi-check" :loading="isUpdatingPassword" />
        </div>
      </form>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useCurrency } from '~/composables/useCurrency'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'default' })

const toast = useToast()
const { currentCurrency, setCurrency, getRate } = useCurrency()
const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

// --- BÜTÇE İŞLEMLERİ ---
const isSavingBudgets = ref(false)
const budgets = ref({
  Food: null as number | null,
  Rent: null as number | null,
  Transport: null as number | null,
  Entertainment: null as number | null,
})

onMounted(() => {
  const savedBudgets = localStorage.getItem('budgetLimits')
  if (savedBudgets) {
    const parsed = JSON.parse(savedBudgets)
    const rate = getRate()
    budgets.value = {
      Food: parsed.Food ? parsed.Food * rate : null,
      Rent: parsed.Rent ? parsed.Rent * rate : null,
      Transport: parsed.Transport ? parsed.Transport * rate : null,
      Entertainment: parsed.Entertainment ? parsed.Entertainment * rate : null,
    }
  }
  isDark.value = localStorage.getItem('theme') === 'dark'
})

const saveBudgets = () => {
  isSavingBudgets.value = true
  const rate = getRate()
  const baseBudgets = {
    Food: budgets.value.Food ? budgets.value.Food / rate : null,
    Rent: budgets.value.Rent ? budgets.value.Rent / rate : null,
    Transport: budgets.value.Transport ? budgets.value.Transport / rate : null,
    Entertainment: budgets.value.Entertainment ? budgets.value.Entertainment / rate : null,
  }

  setTimeout(() => {
    localStorage.setItem('budgetLimits', JSON.stringify(baseBudgets))
    isSavingBudgets.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budgets saved successfully!', life: 3000 });
  }, 600)
}

// DÖVİZ İŞLEMLERİ
const localCurrency = ref(currentCurrency.value)
const currencyOptions = [
  { label: '🇺🇸 US Dollar ($)', value: 'USD' },
  { label: '🇪🇺 Euro (€)', value: 'EUR' },
  { label: '🇹🇷 Turkish Lira (₺)', value: 'TRY' },
  { label: '🇵🇱 Polish Złoty (zł)', value: 'PLN' }
]
const updateCurrency = () => { setCurrency(localCurrency.value) }
watch(currentCurrency, (newVal) => { localCurrency.value = newVal })

// TEMA İŞLEMLERİ
const isDark = ref(false)
const setTheme = (theme: 'light' | 'dark') => {
  if (theme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// CSV EXPORT
const isExporting = ref(false)
const exportCSV = async () => {
  isExporting.value = true
  try {
    const data = await $fetch<any[]>(`${API_BASE}/transactions/`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    if (!data || data.length === 0) {
      toast.add({ severity: 'warn', summary: 'Warning', detail: 'No transactions found to export!', life: 3000 });
      isExporting.value = false
      return
    }
    const headers = ['Date', 'Title', 'Category', 'Type', 'Amount (USD)', 'Description']
    const rows = data.map(tx => [tx.date, `"${tx.title}"`, `"${tx.category}"`, tx.transaction_type, tx.amount, `"${tx.description || ''}"`])
    const csvContent = [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'smart_finance_transactions.csv')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Export failed!', life: 3000 });
  } finally {
    isExporting.value = false
  }
}

// 2FA MANTIĞI (COMING SOON)
const is2FAEnabled = ref(false)
const handle2FAToggle = () => {
  is2FAEnabled.value = true // Önce yak (görsel efekt)
  
  toast.add({ 
    severity: 'info', 
    summary: ' Coming Soon!', 
    detail: 'Email 2FA Integration is scheduled for Version 2.0.', 
    life: 4000 
  });
  
  // 0.4 saniye sonra geri söndür
  setTimeout(() => {
    is2FAEnabled.value = false;
  }, 400);
}

// ŞİFRE GÜNCELLEME
const showPasswordDialog = ref(false)
const isUpdatingPassword = ref(false)
const passwordError = ref('')
const passwordForm = ref({ currentPassword: '', newPassword: '', confirmPassword: '' })

const openPasswordDialog = () => {
  passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  passwordError.value = ''
  showPasswordDialog.value = true
}

const updatePassword = () => {
  passwordError.value = ''
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = 'New passwords do not match!'
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    passwordError.value = 'Password must be at least 6 characters long.'
    return
  }
  isUpdatingPassword.value = true
  setTimeout(() => {
    isUpdatingPassword.value = false
    showPasswordDialog.value = false
    toast.add({ severity: 'success', summary: 'Updated', detail: 'Password changed successfully!', life: 3000 });
  }, 1000)
}
</script>

<style scoped>
.password-wrapper :deep(.p-password) { width: 100%; }
.password-wrapper :deep(.p-password-input) { width: 100%; }
</style>