<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6 text-surface-700 dark:text-surface-200">Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="card p-5 rounded-xl shadow-sm bg-white dark:bg-surface-800 border-l-4 border-green-500">
        <h3 class="text-surface-500 dark:text-surface-400 text-sm font-semibold mb-2">Total Income</h3>
        <p class="text-3xl font-bold text-green-600">{{ formatCurrency(totalIncome) }}</p>
      </div>
      <div class="card p-5 rounded-xl shadow-sm bg-white dark:bg-surface-800 border-l-4 border-red-500">
        <h3 class="text-surface-500 dark:text-surface-400 text-sm font-semibold mb-2">Total Expense</h3>
        <p class="text-3xl font-bold text-red-600">{{ formatCurrency(totalExpense) }}</p>
      </div>
      <div class="card p-5 rounded-xl shadow-sm bg-white dark:bg-surface-800 border-l-4 border-blue-500">
        <h3 class="text-surface-500 dark:text-surface-400 text-sm font-semibold mb-2">Net Balance</h3>
        <p class="text-3xl font-bold text-blue-600">{{ formatCurrency(balance) }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      
      <div class="card p-6 rounded-xl shadow-sm bg-white dark:bg-surface-800">
        <h3 class="text-lg font-bold mb-4 border-b pb-2 dark:border-surface-700">Income Breakdown</h3>
        <div v-if="incomeData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
          <Chart type="doughnut" :data="incomeData" :options="chartOptions" class="w-full max-w-[14rem]" />
        </div>
        <div v-else class="text-center text-surface-500 flex flex-col items-center justify-center h-64">
          <i class="pi pi-chart-pie text-4xl mb-3 opacity-50"></i>
          <p>No income data yet.</p>
        </div>
      </div>

      <div class="card p-6 rounded-xl shadow-sm bg-white dark:bg-surface-800">
        <h3 class="text-lg font-bold mb-4 border-b pb-2 dark:border-surface-700">Expense Breakdown</h3>
        <div v-if="expenseData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
          <Chart type="doughnut" :data="expenseData" :options="chartOptions" class="w-full max-w-[14rem]" />
        </div>
        <div v-else class="text-center text-surface-500 flex flex-col items-center justify-center h-64">
          <i class="pi pi-chart-pie text-4xl mb-3 opacity-50"></i>
          <p>No expense data yet.</p>
        </div>
      </div>

    </div>

    <div class="card p-6 rounded-xl shadow-sm bg-white dark:bg-surface-800">
      <h3 class="text-lg font-bold mb-4 border-b pb-2 dark:border-surface-700">Recent Transactions</h3>
      
      <ul v-if="recentTransactions.length > 0" class="space-y-4">
        <li v-for="tx in recentTransactions" :key="tx.id" class="flex justify-between items-center p-3 hover:bg-surface-50 dark:hover:bg-surface-700 rounded-lg transition-colors">
          <div class="flex items-center gap-4">
            <div :class="tx.transaction_type === 'INCOME' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'" class="p-3 rounded-full h-12 w-12 flex items-center justify-center">
              <i :class="tx.transaction_type === 'INCOME' ? 'pi pi-arrow-down-left' : 'pi pi-arrow-up-right'" class="text-xl"></i>
            </div>
            <div>
              <p class="font-semibold text-surface-800 dark:text-surface-100">{{ tx.title }}</p>
              <p class="text-sm text-surface-500">{{ tx.date }} • <span class="font-medium">{{ tx.category }}</span></p>
            </div>
          </div>
          <span :class="tx.transaction_type === 'INCOME' ? 'text-green-500' : 'text-red-500'" class="font-bold text-xl">
            {{ tx.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatCurrency(tx.amount) }}
          </span>
        </li>
      </ul>
      
      <div v-else class="text-center text-surface-500 flex flex-col items-center justify-center h-40">
        <i class="pi pi-receipt text-4xl mb-3 opacity-50"></i>
        <p>No transactions found.</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Chart from 'primevue/chart'

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

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
          if (context.parsed !== null) label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed);
          return label;
        }
      }
    }
  }
}

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
</script>