<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold text-surface-700 dark:text-surface-200">Savings Goals</h1>
        <p class="mt-2 text-surface-600 dark:text-surface-400">Track your progress towards your financial dreams. 🎯</p>
      </div>
      <Button label="Add Goal" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <div v-if="goals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="goal in goals" :key="goal.id" class="card p-6 rounded-2xl shadow-sm bg-white dark:bg-surface-800 border border-surface-100 dark:border-surface-700 hover:shadow-md transition-shadow">
        
        <div class="flex justify-between items-start mb-6">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 dark:bg-blue-900/30 text-blue-500 p-3 rounded-xl h-12 w-12 flex items-center justify-center">
              <i class="pi pi-star-fill text-xl"></i>
            </div>
            <div>
              <h3 class="font-bold text-lg text-surface-800 dark:text-surface-100">{{ goal.title }}</h3>
              <p class="text-sm font-medium text-surface-500">Target: {{ formatCurrency(goal.target_amount) }}</p>
            </div>
          </div>
          <Button icon="pi pi-trash" text rounded severity="danger" v-tooltip.top="'Delete Goal'" @click="deleteGoal(goal.id)" />
        </div>

        <div class="mt-4">
          <div class="flex justify-between text-sm mb-2 font-bold">
            <span class="text-surface-800 dark:text-surface-200">{{ formatCurrency(goal.current_amount) }}</span>
            <span class="text-blue-500">{{ calculatePercentage(goal.current_amount, goal.target_amount) }}%</span>
          </div>
          <ProgressBar :value="calculatePercentage(goal.current_amount, goal.target_amount)" :showValue="false" class="h-3 rounded-full"></ProgressBar>
        </div>

        <div class="mt-6">
          <Button label="Add Funds" icon="pi pi-wallet" class="w-full p-button-outlined p-button-secondary font-semibold" @click="openAddFundsDialog(goal)" />
        </div>
      </div>
    </div>

    <div v-else class="text-center p-12 bg-white dark:bg-surface-800 rounded-2xl shadow-sm border border-surface-100 dark:border-surface-700">
       <i class="pi pi-star text-6xl text-surface-300 mb-4"></i>
       <h2 class="text-xl font-bold text-surface-700 dark:text-surface-200">No goals yet!</h2>
       <p class="text-surface-500 mt-2">Create your first savings goal and start tracking your dreams.</p>
       <Button label="Create First Goal" icon="pi pi-plus" class="mt-6" @click="showAddDialog = true" />
    </div>

    <Dialog v-model:visible="showAddDialog" modal header="Create New Goal" :style="{ width: '400px' }">
       <form @submit.prevent="saveGoal" class="flex flex-col gap-4 mt-2">
         <div class="flex flex-col gap-2">
            <label for="title" class="font-medium text-surface-700 dark:text-surface-200">Goal Name</label>
            <InputText id="title" v-model="newGoal.title" placeholder="e.g. New Car, Vacation" required />
         </div>
         <div class="flex flex-col gap-2">
            <label for="target" class="font-medium text-surface-700 dark:text-surface-200">Target Amount</label>
            <InputNumber id="target" v-model="newGoal.target_amount" mode="currency" currency="USD" locale="en-US" required />
         </div>
         <div class="flex justify-end gap-2 mt-4">
            <Button type="button" label="Cancel" severity="secondary" @click="showAddDialog = false" />
            <Button type="submit" label="Save Goal" icon="pi pi-check" :loading="isSaving" />
         </div>
       </form>
    </Dialog>

    <Dialog v-model:visible="showAddFundsDialog" modal :header="`Add Funds to ${selectedGoal?.title}`" :style="{ width: '400px' }">
       <form @submit.prevent="addFunds" class="flex flex-col gap-4 mt-2">
         <div class="flex flex-col gap-2">
            <label for="fundAmount" class="font-medium text-surface-700 dark:text-surface-200">Amount to Add</label>
            <InputNumber id="fundAmount" v-model="amountToAdd" mode="currency" currency="USD" locale="en-US" required autofocus />
         </div>
         <p class="text-xs text-surface-500 italic mt-1">
           <i class="pi pi-info-circle"></i> This amount will also be recorded as an expense in your transactions.
         </p>
         <div class="flex justify-end gap-2 mt-4">
            <Button type="button" label="Cancel" severity="secondary" @click="showAddFundsDialog = false" />
            <Button type="submit" label="Add & Record" icon="pi pi-plus" :loading="isAddingFunds" />
         </div>
       </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

const showAddDialog = ref(false)
const isSaving = ref(false)
const newGoal = ref({ title: '', target_amount: null as number | null })

const showAddFundsDialog = ref(false)
const isAddingFunds = ref(false)
const selectedGoal = ref<any>(null)
const amountToAdd = ref<number | null>(null)

// API'den Veri Çek
const { data: rawData, refresh } = await useFetch(`${API_BASE}/savings-goals/`, {
  headers: { Authorization: computed(() => `Bearer ${token.value}`) },
})
const goals = computed(() => (rawData.value && Array.isArray(rawData.value) ? rawData.value : []))

// Bugünün tarihini YYYY-MM-DD formatında almak için yardımcı fonksiyon
const getTodayDate = () => {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

// Yeni Hedef Kaydet
const saveGoal = async () => {
  if (!newGoal.value.title || !newGoal.value.target_amount) return;
  isSaving.value = true;
  try {
    await $fetch(`${API_BASE}/savings-goals/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
      body: { title: newGoal.value.title, target_amount: newGoal.value.target_amount, current_amount: 0 }
    });
    newGoal.value = { title: '', target_amount: null };
    showAddDialog.value = false;
    await refresh();
  } catch (error) { console.error(error); } finally { isSaving.value = false; }
}

const deleteGoal = async (id: number) => {
  if(!confirm('Are you sure you want to delete this goal?')) return;
  try {
    await $fetch(`${API_BASE}/savings-goals/${id}/`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token.value}` }
    });
    await refresh();
  } catch(error) { console.error(error); }
}

const openAddFundsDialog = (goal: any) => {
  selectedGoal.value = goal;
  amountToAdd.value = null; 
  showAddFundsDialog.value = true;
}

// YENİ: HEM HEDEFİ GÜNCELLE HEM DE İŞLEM (TRANSACTION) EKLE
const addFunds = async () => {
  if (!selectedGoal.value || !amountToAdd.value || amountToAdd.value <= 0) return;
  isAddingFunds.value = true;
  
  try {
    // 1. Hedefin içindeki parayı güncelle
    const newTotal = Number(selectedGoal.value.current_amount) + Number(amountToAdd.value);
    
    await $fetch(`${API_BASE}/savings-goals/${selectedGoal.value.id}/`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
      body: { current_amount: newTotal }
    });

    // 2. Senin harika fikrin: Ana işlemlere (Transactions) bunu bir "Gider" olarak kaydet
    await $fetch(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
      body: {
        title: `Transfer to Goal: ${selectedGoal.value.title}`,
        amount: amountToAdd.value,
        transaction_type: 'EXPENSE',
        category: 'Savings', // Giderin kategorisi "Birikim" olacak
        date: getTodayDate()
      }
    });
    
    showAddFundsDialog.value = false;
    await refresh(); // Mavi bar dolsun diye ekranı yenile
  } catch (error) { 
    console.error("Para eklenirken hata oluştu:", error); 
  } finally { 
    isAddingFunds.value = false; 
  }
}

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value) || 0)
const calculatePercentage = (current: number, target: number) => {
  const numCurrent = Number(current) || 0;
  const numTarget = Number(target) || 0;
  if (numTarget <= 0) return 0;
  const percent = Math.round((numCurrent / numTarget) * 100);
  return percent > 100 ? 100 : percent;
}
</script>

<style scoped>
:deep(.p-progressbar-value) { background-color: #3B82F6 !important; transition: width 0.5s ease-in-out; }
:deep(.p-progressbar) { background-color: var(--p-surface-200); }
.dark :deep(.p-progressbar) { background-color: var(--p-surface-700); }
</style>