<template>
  <div class="p-6 max-w-[1400px] mx-auto">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Savings Goals</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-300">Track your progress towards your financial dreams. 🎯</p>
      </div>
      <Button label="Add Goal" icon="pi pi-plus" @click="openAddDialog" class="shadow-sm" />
    </div>

    <div v-if="goals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="goal in goals" 
        :key="goal.id" 
        class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all duration-300 group"
      >
        
        <div class="flex justify-between items-start mb-6">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 p-3 rounded-2xl h-14 w-14 flex items-center justify-center transition-colors duration-300">
              <i class="pi pi-star-fill text-2xl"></i>
            </div>
            <div>
              <h3 class="font-bold text-xl text-gray-900 dark:text-white transition-colors duration-300">{{ goal.title }}</h3>
              <p class="text-sm font-medium text-gray-500 dark:text-gray-400 transition-colors duration-300">Target: {{ formatCurrency(goal.target_amount) }}</p>
            </div>
          </div>
          
          <div class="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
            <Button icon="pi pi-pencil" text rounded severity="info" size="small" v-tooltip.top="'Edit Goal'" @click="openEditDialog(goal)" />
            <Button icon="pi pi-trash" text rounded severity="danger" size="small" v-tooltip.top="'Delete Goal'" @click="deleteGoal(goal.id)" />
          </div>
        </div>

        <div class="mt-4">
          <div class="flex justify-between text-sm mb-2 font-bold">
            <span class="text-gray-900 dark:text-white transition-colors duration-300">{{ formatCurrency(goal.current_amount) }}</span>
            <span class="text-blue-600 dark:text-blue-400 transition-colors duration-300">{{ calculatePercentage(goal.current_amount, goal.target_amount) }}%</span>
          </div>
          <ProgressBar :value="calculatePercentage(goal.current_amount, goal.target_amount)" :showValue="false" class="h-3 rounded-full"></ProgressBar>
        </div>

        <div class="mt-8">
          <Button label="Add Funds" icon="pi pi-wallet" class="w-full p-button-outlined p-button-secondary font-bold" @click="openAddFundsDialog(goal)" />
        </div>
      </div>
    </div>

    <div v-else class="text-center p-16 bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 transition-colors duration-300 flex flex-col items-center justify-center">
       <i class="pi pi-star text-6xl text-gray-300 dark:text-gray-600 mb-6 transition-colors duration-300"></i>
       <h2 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">No goals yet!</h2>
       <p class="text-gray-500 dark:text-gray-400 mt-2 text-lg transition-colors duration-300">Create your first savings goal and start tracking your dreams.</p>
       <Button label="Create First Goal" icon="pi pi-plus" class="mt-8" size="large" @click="openAddDialog" />
    </div>

    <Dialog 
      v-model:visible="showAddDialog" 
      modal 
      :header="editingGoalId ? '✏️ Edit Goal' : '🎯 Create New Goal'" 
      :style="{ width: '90vw', maxWidth: '400px' }"
      @hide="resetForm"
    >
       <form @submit.prevent="saveGoal" class="flex flex-col gap-4 mt-2">
         <div class="flex flex-col gap-2">
            <label for="title" class="font-medium text-gray-700 dark:text-gray-300">Goal Name</label>
            <InputText id="title" v-model="newGoal.title" placeholder="e.g. New Car, Vacation" required autofocus />
         </div>
         <div class="flex flex-col gap-2">
            <label for="target" class="font-medium text-gray-700 dark:text-gray-300">
              Target Amount (in {{ currentCurrency }})
            </label>
            <InputNumber id="target" v-model="newGoal.displayTarget" mode="currency" :currency="currentCurrency" required />
         </div>
         <div class="flex justify-end gap-2 mt-6">
            <Button type="button" label="Cancel" severity="secondary" @click="showAddDialog = false" />
            <Button type="submit" :label="editingGoalId ? 'Update Goal' : 'Save Goal'" icon="pi pi-check" :loading="isSaving" />
         </div>
       </form>
    </Dialog>

    <Dialog v-model:visible="showAddFundsDialog" modal :header="`Add Funds to ${selectedGoal?.title}`" :style="{ width: '90vw', maxWidth: '400px' }">
       <form @submit.prevent="addFunds" class="flex flex-col gap-4 mt-2">
         <div class="flex flex-col gap-2">
            <label for="fundAmount" class="font-medium text-gray-700 dark:text-gray-300">
              Amount to Add (in {{ currentCurrency }})
            </label>
            <InputNumber id="fundAmount" v-model="displayAmountToAdd" mode="currency" :currency="currentCurrency" required autofocus />
         </div>
         <p class="text-sm text-gray-500 dark:text-gray-400 italic mt-2 bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg border border-gray-100 dark:border-gray-600">
           <i class="pi pi-info-circle mr-1"></i> This amount will also be recorded as an expense in your transactions.
         </p>
         <div class="flex justify-end gap-2 mt-6">
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
import { useCurrency } from '~/composables/useCurrency' 

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

const { formatCurrency, currentCurrency, getRate } = useCurrency()

const showAddDialog = ref(false)
const isSaving = ref(false)

const editingGoalId = ref<number | null>(null)

const newGoal = ref({ title: '', displayTarget: null as number | null })

const showAddFundsDialog = ref(false)
const isAddingFunds = ref(false)
const selectedGoal = ref<any>(null)
const displayAmountToAdd = ref<number | null>(null)

const { data: rawData, refresh } = await useFetch(`${API_BASE}/savings-goals/`, {
  headers: { Authorization: computed(() => `Bearer ${token.value}`) },
})
const goals = computed(() => (rawData.value && Array.isArray(rawData.value) ? rawData.value : []))

const getTodayDate = () => {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

const resetForm = () => {
  editingGoalId.value = null;
  newGoal.value = { title: '', displayTarget: null };
}

const openAddDialog = () => {
  resetForm();
  showAddDialog.value = true;
}

const openEditDialog = (goal: any) => {
  editingGoalId.value = goal.id;
  const rate = getRate();
  
  newGoal.value = {
    title: goal.title,
    displayTarget: Number(goal.target_amount) * rate
  };
  showAddDialog.value = true;
}

const saveGoal = async () => {
  if (!newGoal.value.title || !newGoal.value.displayTarget) return;
  isSaving.value = true;
  
  try {
    const rate = getRate()
    const targetInUSD = newGoal.value.displayTarget / rate

    if (editingGoalId.value) {
      await $fetch(`${API_BASE}/savings-goals/${editingGoalId.value}/`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
        body: { title: newGoal.value.title, target_amount: targetInUSD }
      });
    } else {
      await $fetch(`${API_BASE}/savings-goals/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
        body: { title: newGoal.value.title, target_amount: targetInUSD, current_amount: 0 }
      });
    }
    
    showAddDialog.value = false;
    resetForm();
    await refresh();
  } catch (error) { 
    console.error(error); 
  } finally { 
    isSaving.value = false; 
  }
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
  displayAmountToAdd.value = null; 
  showAddFundsDialog.value = true;
}

const addFunds = async () => {
  if (!selectedGoal.value || !displayAmountToAdd.value || displayAmountToAdd.value <= 0) return;
  isAddingFunds.value = true;
  
  try {
    const rate = getRate()
    const amountToAddInUSD = displayAmountToAdd.value / rate

    const newTotalInUSD = Number(selectedGoal.value.current_amount) + amountToAddInUSD;
    
    await $fetch(`${API_BASE}/savings-goals/${selectedGoal.value.id}/`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
      body: { current_amount: newTotalInUSD }
    });

    await $fetch(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}`, 'Content-Type': 'application/json' },
      body: {
        title: `Transfer to Goal: ${selectedGoal.value.title}`,
        amount: amountToAddInUSD,
        transaction_type: 'EXPENSE',
        category: 'Savings', 
        date: getTodayDate()
      }
    });
    
    showAddFundsDialog.value = false;
    await refresh();
  } catch (error) { 
    console.error("Para eklenirken hata oluştu:", error); 
  } finally { 
    isAddingFunds.value = false; 
  }
}

const calculatePercentage = (current: number, target: number) => {
  const numCurrent = Number(current) || 0;
  const numTarget = Number(target) || 0;
  if (numTarget <= 0) return 0;
  const percent = Math.round((numCurrent / numTarget) * 100);
  return percent > 100 ? 100 : percent;
}
</script>

<style scoped>
:deep(.p-progressbar-value) { 
  background-color: #3B82F6 !important; 
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); 
}
:deep(.p-progressbar) { 
  background-color: #f3f4f6;
}
.dark :deep(.p-progressbar) { 
  background-color: #374151;
}
</style>