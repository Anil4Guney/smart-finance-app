<template>
  <div class="lg:p-2 max-w-[1400px] mx-auto">
    <div class="mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Ayarlar</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Uygulama tercihlerini, güvenliği ve verilerini yönet.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <div class="card p-5 sm:p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
            <i class="pi pi-globe text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Bölgesel Tercihler</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <div>
            <label class="block font-bold text-gray-700 dark:text-gray-300 mb-3">Gösterilen Para Birimi</label>
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
            <i class="pi pi-sync mr-2 text-blue-500"></i> Kurlar canlı alınır. Panelin anında güncellenir.
          </p>
        </div>
      </div>

      <div class="card p-5 sm:p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg">
            <i class="pi pi-palette text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Görünüm</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <label class="block font-bold text-gray-700 dark:text-gray-300 mb-1">Tema</label>
          <div class="flex gap-4">
            <button 
              @click="setTheme('light')"
              :class="!isDark ? 'ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'"
              class="flex-1 p-4 rounded-2xl border border-gray-200 dark:border-gray-600 flex flex-col items-center gap-2 transition-all"
            >
              <i class="pi pi-sun text-2xl" :class="!isDark ? 'text-purple-600' : 'text-gray-500 dark:text-gray-400'"></i>
              <span class="font-bold" :class="!isDark ? 'text-purple-700 dark:text-purple-400' : 'text-gray-600 dark:text-gray-300'">Açık</span>
            </button>
            
            <button 
              @click="setTheme('dark')"
              :class="isDark ? 'ring-2 ring-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'"
              class="flex-1 p-4 rounded-2xl border border-gray-200 dark:border-gray-600 flex flex-col items-center gap-2 transition-all"
            >
              <i class="pi pi-moon text-2xl" :class="isDark ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'"></i>
              <span class="font-bold" :class="isDark ? 'text-purple-700 dark:text-purple-400' : 'text-gray-600 dark:text-gray-300'">Koyu</span>
            </button>
          </div>
        </div>
      </div>

      <div class="card p-5 sm:p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 lg:col-span-2">
        <div class="flex items-center justify-between mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg">
              <i class="pi pi-chart-pie text-xl"></i>
            </div>
            <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Aylık Bütçe Limitleri</h2>
          </div>
          <Button label="Bütçeleri Kaydet" icon="pi pi-save" @click="saveBudgets" :loading="isSavingBudgets" />
        </div>
        
        <p class="text-gray-600 dark:text-gray-400 mb-8">
          Gider kategorilerin için aylık üst sınır belirle. Panelin ilerlemeni takip eder ve limiti aşmadan önce seni uyarır.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-shopping-cart text-gray-400"></i> Yemek
            </label>
            <InputNumber v-model="budgets.Food" mode="currency" :currency="currentCurrency" class="w-full" placeholder="Limit yok" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-home text-gray-400"></i> Kira
            </label>
            <InputNumber v-model="budgets.Rent" mode="currency" :currency="currentCurrency" class="w-full" placeholder="Limit yok" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-car text-gray-400"></i> Ulaşım
            </label>
            <InputNumber v-model="budgets.Transport" mode="currency" :currency="currentCurrency" class="w-full" placeholder="Limit yok" />
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <i class="pi pi-ticket text-gray-400"></i> Eğlence
            </label>
            <InputNumber v-model="budgets.Entertainment" mode="currency" :currency="currentCurrency" class="w-full" placeholder="Limit yok" />
          </div>

        </div>
      </div>

      <div class="card p-5 sm:p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
            <i class="pi pi-download text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Veri ve Gizlilik</h2>
        </div>
        
        <div class="flex flex-col gap-5">
          <p class="text-gray-600 dark:text-gray-400">Tüm işlemlerinin bir kopyasını kendi kayıtların için indir (Excel'de açılır).</p>
          
          <Button 
            label="İşlemleri CSV Olarak İndir" 
            icon="pi pi-file-excel" 
            severity="success" 
            :loading="isExporting"
            @click="exportCSV" 
            class="w-full sm:w-auto"
          />
        </div>
      </div>

      <div class="card p-5 sm:p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300">
        <div class="flex items-center gap-3 mb-6 border-b pb-4 border-gray-100 dark:border-gray-700">
          <div class="p-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg">
            <i class="pi pi-shield text-xl"></i>
          </div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Güvenlik</h2>
        </div>
        
        <div class="flex flex-col gap-6">
          <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-100 dark:border-gray-700">
            <div>
              <h3 class="font-bold text-gray-900 dark:text-white">Şifreyi Değiştir</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Hesabını güvende tutmak için şifreni düzenli güncelle.</p>
            </div>
            <Button label="Güncelle" icon="pi pi-key" severity="secondary" outlined size="small" @click="openPasswordDialog" />
          </div>

          <div class="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-100 dark:border-gray-700">
            <div>
              <h3 class="font-bold text-gray-900 dark:text-white">İki Adımlı Doğrulama (yakında)</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Hesabına ek bir güvenlik katmanı ekle.</p>
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

    <Dialog v-model:visible="showPasswordDialog" modal header="🔒 Şifreyi Değiştir" :style="{ width: '90vw', maxWidth: '450px' }">
      <form @submit.prevent="updatePassword" class="flex flex-col gap-5 pt-4">
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="currentPassword" class="font-bold text-gray-700 dark:text-gray-300">Mevcut şifre</label>
          <Password id="currentPassword" v-model="passwordForm.currentPassword" :feedback="false" toggleMask required placeholder="Mevcut şifren" inputClass="w-full" />
        </div>
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="newPassword" class="font-bold text-gray-700 dark:text-gray-300">Yeni şifre</label>
          <Password id="newPassword" v-model="passwordForm.newPassword" toggleMask required placeholder="Yeni şifren" inputClass="w-full" />
        </div>
        <div class="flex flex-col gap-2 password-wrapper">
          <label for="confirmPassword" class="font-bold text-gray-700 dark:text-gray-300">Yeni şifre (tekrar)</label>
          <Password id="confirmPassword" v-model="passwordForm.confirmPassword" :feedback="false" toggleMask required placeholder="Yeni şifreni tekrar yaz" inputClass="w-full" />
        </div>
        <div v-if="passwordError" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm font-medium border border-red-100 dark:border-red-800/50">
          <i class="pi pi-exclamation-circle mr-1"></i> {{ passwordError }}
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <Button type="button" label="Vazgeç" severity="secondary" text @click="showPasswordDialog = false" />
          <Button type="submit" label="Şifreyi Güncelle" icon="pi pi-check" :loading="isUpdatingPassword" />
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
const { currentCurrency, setCurrency, getRate, currencyOptions } = useCurrency()
const { token } = useAuth()
const { API_BASE, AUTH_BASE } = useApiBase()

// --- BÜTÇE İŞLEMLERİ ---
const isSavingBudgets = ref(false)
const budgets = ref({
  Food: null as number | null,
  Rent: null as number | null,
  Transport: null as number | null,
  Entertainment: null as number | null,
})

const { fetchBudgets, saveBudgets: saveBudgetsToServer } = useBudgets()

// Budgets are stored in USD; show them in the selected currency.
const showBudgets = (stored: Record<string, number>) => {
  const rate = getRate()
  budgets.value = {
    Food: stored.Food ? stored.Food * rate : null,
    Rent: stored.Rent ? stored.Rent * rate : null,
    Transport: stored.Transport ? stored.Transport * rate : null,
    Entertainment: stored.Entertainment ? stored.Entertainment * rate : null,
  }
}

onMounted(async () => {
  isDark.value = document.documentElement.classList.contains('dark')
  try {
    showBudgets(await fetchBudgets())
  } catch (error) {
    console.error('Budgets could not be loaded:', error)
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Bütçelerin yüklenemedi.', life: 3000 })
  }
})

const saveBudgets = async () => {
  isSavingBudgets.value = true
  const rate = getRate()
  const baseBudgets = {
    Food: budgets.value.Food ? budgets.value.Food / rate : null,
    Rent: budgets.value.Rent ? budgets.value.Rent / rate : null,
    Transport: budgets.value.Transport ? budgets.value.Transport / rate : null,
    Entertainment: budgets.value.Entertainment ? budgets.value.Entertainment / rate : null,
  }

  try {
    showBudgets(await saveBudgetsToServer(baseBudgets))
    toast.add({ severity: 'success', summary: 'Kaydedildi', detail: 'Bütçelerin kaydedildi.', life: 3000 })
  } catch (error) {
    console.error('Budgets could not be saved:', error)
    toast.add({ severity: 'error', summary: 'Hata', detail: 'Bütçeler kaydedilemedi.', life: 3000 })
  } finally {
    isSavingBudgets.value = false
  }
}

// DÖVİZ İŞLEMLERİ
const localCurrency = ref(currentCurrency.value)
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
      toast.add({ severity: 'warn', summary: 'Uyarı', detail: 'İndirilecek işlem bulunamadı.', life: 3000 });
      isExporting.value = false
      return
    }
    const headers = ['Tarih', 'Başlık', 'Kategori', 'Tür', 'Tutar (USD)', 'Açıklama']
    const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
    const rows = data.map(tx => [tx.date, esc(tx.title), esc(categoryLabel(tx.category)), tx.transaction_type === 'INCOME' ? 'Gelir' : 'Gider', tx.amount, esc(tx.description)])
    const csvContent = [headers.join(';'), ...rows.map(e => e.join(';'))].join('\r\n')
    // BOM so Excel reads Turkish characters correctly
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'smart_finance_transactions.csv')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Hata', detail: 'İndirme başarısız oldu.', life: 3000 });
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
    summary: 'Yakında!', 
    detail: 'İki adımlı doğrulama sonraki sürümde gelecek.', 
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

const updatePassword = async () => {
  passwordError.value = ''
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = 'Yeni şifreler eşleşmiyor.'
    return
  }
  if (passwordForm.value.newPassword.length < 8) {
    passwordError.value = 'Şifre en az 8 karakter olmalı.'
    return
  }
  isUpdatingPassword.value = true
  try {
    await $fetch(`${AUTH_BASE}/users/set_password/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` },
      body: {
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword,
      },
    })
    showPasswordDialog.value = false
    toast.add({ severity: 'success', summary: 'Güncellendi', detail: 'Şifren değiştirildi.', life: 3000 })
  } catch (error: any) {
    // Django returns field errors, e.g. { current_password: ["Invalid password."] }
    const data = error?.data || {}
    passwordError.value =
      data.current_password?.[0] ||
      data.new_password?.[0] ||
      data.non_field_errors?.[0] ||
      data.detail ||
      'Şifre değiştirilemedi. Lütfen tekrar dene.'
  } finally {
    isUpdatingPassword.value = false
  }
}
</script>

<style scoped>
.password-wrapper :deep(.p-password) { width: 100%; }
.password-wrapper :deep(.p-password-input) { width: 100%; }
</style>