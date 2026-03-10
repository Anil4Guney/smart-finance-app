<template>
  <div class="p-6 max-w-[1400px] mx-auto">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Subscriptions & Bills</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-300">Manage your recurring payments and never miss a due date.</p>
      </div>
      <Button label="Add New Bill" icon="pi pi-plus" @click="openAddModal" class="shadow-sm" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Total Monthly Cost</h3>
        <p class="text-3xl font-extrabold text-gray-900 dark:text-white">{{ formatCurrency(totalMonthlyCost) }}</p>
      </div>
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Active Subscriptions</h3>
        <p class="text-3xl font-extrabold text-blue-600 dark:text-blue-400">{{ subscriptions.length }}</p>
      </div>
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Notifications</h3>
        <p class="text-xl font-extrabold" :class="notifications.length > 0 ? 'text-red-600 dark:text-red-400' : 'text-green-500'">
          {{ notifications.length > 0 ? `${notifications.length} Action Needed` : 'All Good' }}
        </p>
      </div>
    </div>

    <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 min-h-[400px]">
      
      <div v-if="subscriptions.length === 0" class="text-center text-gray-500 flex flex-col items-center justify-center h-64">
        <i class="pi pi-calendar-times text-5xl mb-4 opacity-30"></i>
        <p class="font-medium text-lg">No active subscriptions found.</p>
        <Button label="Add Your First Bill" class="mt-6 p-button-outlined" @click="openAddModal" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="sub in subscriptions" 
          :key="sub.id" 
          class="flex flex-col p-6 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all relative group"
        >
          <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
            <button @click="openEditModal(sub)" class="text-gray-400 hover:text-blue-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
              <i class="pi pi-pencil text-sm"></i>
            </button>
            <button @click="deleteSubscription(sub.id)" class="text-gray-400 hover:text-red-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
              <i class="pi pi-trash text-sm"></i>
            </button>
          </div>

          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shadow-sm" :class="sub.colorClass">
              <i :class="['pi', sub.icon]"></i>
            </div>
            <div>
              <h3 class="font-bold text-xl text-gray-900 dark:text-white">{{ sub.name }}</h3>
              <span class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold mt-1" 
                :class="getDaysLeft(sub.dueDate) <= 1 ? 'bg-red-100 text-red-600 dark:bg-red-900/30' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'">
                <i class="pi pi-clock text-[10px]"></i> {{ getRelativeDateString(sub.dueDate) }}
              </span>
            </div>
          </div>
          
          <div class="mt-auto flex items-end justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
            <span class="text-sm text-gray-500 font-medium">Monthly Cost</span>
            <span class="text-2xl font-extrabold text-gray-900 dark:text-white">{{ formatCurrency(sub.amount) }}</span>
          </div>
        </div>
      </div>
    </div>

    <Dialog 
      v-model:visible="showModal" 
      modal 
      :draggable="false"
      :header="editingId ? '✏️ Edit Subscription' : '📅 Add New Subscription'" 
      :style="{ width: '450px' }"
    >
      <form @submit.prevent="handleSave" class="flex flex-col gap-5 pt-4">
        <div class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Service Name</label>
          <InputText v-model="formData.name" placeholder="e.g. Gym, Adobe, Apple Music" required class="w-full" />
        </div>
        
        <div class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Monthly Amount</label>
          <InputNumber v-model="formData.amount" mode="currency" :currency="currentCurrency" required class="w-full" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Select Due Date</label>
          <Calendar v-model="formData.dueDate" showIcon dateFormat="dd/mm/yy" class="w-full" required />
        </div>

        <div class="flex justify-end gap-3 mt-4">
          <Button type="button" label="Cancel" severity="secondary" text @click="showModal = false" />
          <Button type="submit" :label="editingId ? 'Update Subscription' : 'Save Subscription'" icon="pi pi-check" :loading="isSaving" />
        </div>
      </form>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import { useCurrency } from '~/composables/useCurrency'
import { useSubscriptions } from '~/composables/useSubscriptions'

definePageMeta({ layout: 'default' })

const { formatCurrency, currentCurrency } = useCurrency()
const { subscriptions, addSubscription, updateSubscription, deleteSubscription, getDaysLeft, getRelativeDateString, notifications, loadSubscriptions } = useSubscriptions()

onMounted(() => {
  loadSubscriptions()
})

const showModal = ref(false)
const isSaving = ref(false)
const editingId = ref<number | null>(null) 

const formData = ref({
  name: '',
  amount: null as number | null,
  dueDate: null as Date | null
})

const totalMonthlyCost = computed(() => {
  return subscriptions.value.reduce((total, sub) => total + sub.amount, 0)
})

const openAddModal = () => {
  editingId.value = null
  formData.value = { name: '', amount: null, dueDate: null }
  showModal.value = true
}

const openEditModal = (sub: any) => {
  editingId.value = sub.id
  formData.value = { 
    name: sub.name, 
    amount: sub.amount, 
    dueDate: new Date(sub.dueDate) 
  }
  showModal.value = true
}

const handleSave = async () => {
  if (!formData.value.name || !formData.value.amount || !formData.value.dueDate) return

  isSaving.value = true

  try {
    if (editingId.value) {
      await updateSubscription(editingId.value, formData.value)
    } else {
      let icon = 'pi-credit-card'
      let colorClass = 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'
      if (formData.value.name.toLowerCase().includes('gym')) { icon = 'pi-heart-fill'; colorClass = 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' }
      if (formData.value.name.toLowerCase().includes('internet') || formData.value.name.toLowerCase().includes('wifi')) { icon = 'pi-wifi'; colorClass = 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' }

      await addSubscription({
        ...formData.value,
        icon: icon,
        colorClass: colorClass
      })
    }
    
    showModal.value = false
  } finally {
    isSaving.value = false
  }
} 
</script>