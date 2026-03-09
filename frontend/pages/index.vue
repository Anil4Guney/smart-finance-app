<template>
  <div class="p-6 max-w-[1400px] mx-auto">
    <h1 class="text-3xl font-bold mb-8 text-gray-900 dark:text-white transition-colors duration-300">
      Dashboard
    </h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border-l-4 border-green-500 hover:shadow-md transition-all duration-300">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2 transition-colors duration-300">Total Income</h3>
        <p class="text-3xl font-extrabold text-green-600 dark:text-green-400 transition-colors duration-300">
          {{ formatCurrency(totalIncome) }}
        </p>
      </div>
      
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border-l-4 border-red-500 hover:shadow-md transition-all duration-300">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2 transition-colors duration-300">Total Expense</h3>
        <p class="text-3xl font-extrabold text-red-600 dark:text-red-400 transition-colors duration-300">
          {{ formatCurrency(totalExpense) }}
        </p>
      </div>
      
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border-l-4 border-blue-500 hover:shadow-md transition-all duration-300">
        <h3 class="text-gray-500 dark:text-gray-400 text-sm font-bold uppercase tracking-wider mb-2 transition-colors duration-300">Net Balance</h3>
        <p class="text-3xl font-extrabold text-blue-600 dark:text-blue-400 transition-colors duration-300">
          {{ formatCurrency(balance) }}
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      
      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
        <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
          Income Breakdown
        </h3>
        <div v-if="incomeData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
          <Chart type="doughnut" :data="incomeData" :options="chartOptions" class="w-full max-w-[16rem]" />
        </div>
        <div v-else class="text-center text-gray-500 dark:text-gray-400 flex flex-col items-center justify-center h-64 transition-colors duration-300">
          <i class="pi pi-chart-pie text-5xl mb-4 opacity-30 dark:opacity-20"></i>
          <p class="font-medium">No income data yet.</p>
        </div>
      </div>

      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
        <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
          Expense Breakdown
        </h3>
        <div v-if="expenseData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
          <Chart type="doughnut" :data="expenseData" :options="chartOptions" class="w-full max-w-[16rem]" />
        </div>
        <div v-else class="text-center text-gray-500 dark:text-gray-400 flex flex-col items-center justify-center h-64 transition-colors duration-300">
          <i class="pi pi-chart-pie text-5xl mb-4 opacity-30 dark:opacity-20"></i>
          <p class="font-medium">No expense data yet.</p>
        </div>
      </div>

    </div>

    <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
      <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
        Recent Transactions
      </h3>
      
      <ul v-if="recentTransactions.length > 0" class="space-y-3">
        <li 
          v-for="tx in recentTransactions" 
          :key="tx.id" 
          class="flex justify-between items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-2xl transition-all duration-300 border border-transparent dark:hover:border-gray-600"
        >
          <div class="flex items-center gap-4">
            <div 
              :class="tx.transaction_type === 'INCOME' ? 'bg-green-100 text-green-600 dark:bg-green-500/20 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400'" 
              class="p-3 rounded-full h-12 w-12 flex items-center justify-center transition-colors duration-300"
            >
              <i :class="tx.transaction_type === 'INCOME' ? 'pi pi-arrow-down-left' : 'pi pi-arrow-up-right'" class="text-xl font-bold"></i>
            </div>
            <div>
              <p class="font-bold text-gray-900 dark:text-white text-lg transition-colors duration-300">{{ tx.title }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400 transition-colors duration-300">
                {{ tx.date }} • <span class="font-medium">{{ tx.category }}</span>
              </p>
            </div>
          </div>
          <span 
            :class="tx.transaction_type === 'INCOME' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'" 
            class="font-extrabold text-xl transition-colors duration-300"
          >
            {{ tx.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatCurrency(tx.amount) }}
          </span>
        </li>
      </ul>
      
      <div v-else class="text-center text-gray-500 dark:text-gray-400 flex flex-col items-center justify-center h-40 transition-colors duration-300">
        <i class="pi pi-receipt text-5xl mb-4 opacity-30 dark:opacity-20"></i>
        <p class="font-medium">No transactions found.</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Chart from 'primevue/chart'
import { useCurrency } from '~/composables/useCurrency' // DÖVİZ BEYNİ BAĞLANDI

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

// Döviz Araçlarını Al
const { formatCurrency } = useCurrency()

// Veriyi Çek
const { data } = await useFetch(`${API_BASE}/transactions/`, {
  headers: { Authorization: computed(() => `Bearer ${token.value}`) },
})
const transactions = computed(() => (data.value && Array.isArray(data.value) ? data.value : []))

// --- HESAPLAMALAR ---
const totalIncome = computed(() => transactions.value.filter(t => t.transaction_type === 'INCOME').reduce((sum, t) => sum + Number(t.amount), 0))
const totalExpense = computed(() => transactions.value.filter(t => t.transaction_type === 'EXPENSE').reduce((sum, t) => sum + Number(t.amount), 0))
const balance = computed(() => totalIncome.value - totalExpense.value)

const recentTransactions = computed(() => [...transactions.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 5))

// --- GELİR PASTASI VERİSİ ---
const incomeData = computed(() => {
  const incomes = transactions.value.filter(t => t.transaction_type === 'INCOME')
  const totals = incomes.reduce((acc, curr) => {
    acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount)
    return acc
  }, {} as Record<string, number>)

  return {
    labels: Object.keys(totals),
    datasets: [{
      data: Object.values(totals),
      backgroundColor: ['#3B82F6', '#14B8A6', '#10B981', '#F59E0B', '#8B5CF6'],
      hoverBackgroundColor: ['#2563EB', '#0D9488', '#059669', '#D97706', '#7C3AED'],
      borderWidth: 0, hoverOffset: 4
    }]
  }
})

// --- GİDER PASTASI VERİSİ ---
const expenseData = computed(() => {
  const expenses = transactions.value.filter(t => t.transaction_type === 'EXPENSE')
  const totals = expenses.reduce((acc, curr) => {
    acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount)
    return acc
  }, {} as Record<string, number>)

  return {
    labels: Object.keys(totals),
    datasets: [{
      data: Object.values(totals),
      backgroundColor: ['#EF4444', '#EC4899', '#F97316', '#6366F1', '#6B7280', '#06B6D4'],
      hoverBackgroundColor: ['#DC2626', '#DB2777', '#EA580C', '#4F46E5', '#4B5563', '#0891B2'],
      borderWidth: 0, hoverOffset: 4
    }]
  }
})

// --- GRAFİK AYARLARI ---
const chartOptions = {
  cutout: '70%',
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, padding: 15, font: { family: 'Inter, sans-serif', size: 12 } } },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)', padding: 12, cornerRadius: 8,
      callbacks: {
        label: function(context: any) {
          let label = context.label || '';
          if (label) label += ': ';
          // DİNAMİK KUR: Grafiğin içindeki yazılar da canlı kura göre formatlanır
          if (context.parsed !== null) label += formatCurrency(context.parsed);
          return label;
        }
      }
    }
  }
}
</script>