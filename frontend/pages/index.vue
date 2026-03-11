<template>
  <div class="p-6 max-w-[1400px] mx-auto relative">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">
        Dashboard
      </h1>
      <Button label="Add Transaction" icon="pi pi-plus" class="shadow-sm" @click="$router.push('/transactions')" />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
      <div class="relative overflow-hidden rounded-3xl p-6 shadow-lg bg-gradient-to-br from-gray-900 to-gray-800 text-white transform hover:-translate-y-1 transition-all duration-300">
        <div class="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
        <div class="absolute bottom-0 left-0 -mb-4 -ml-4 w-20 h-20 bg-blue-500/20 rounded-full blur-lg"></div>
        <div class="relative z-10 flex flex-col h-full justify-between">
          <div class="flex justify-between items-start">
            <div class="flex items-center gap-2">
              <i class="pi pi-building text-blue-400 text-xl"></i>
              <span class="font-medium text-gray-300 tracking-wide">Main Account</span>
            </div>
            <i class="pi pi-wifi text-gray-400 rotate-90"></i>
          </div>
          <div class="mt-8 mb-4">
            <p class="text-sm text-gray-400 mb-1">Total Balance</p>
            <p class="text-4xl font-extrabold tracking-tight">{{ formatCurrency(balance) }}</p>
          </div>
          <div class="flex justify-between items-center text-sm font-medium text-gray-300">
            <span class="uppercase tracking-widest">{{ user?.first_name ? `${user.first_name} ${user.last_name || ''}` : 'Smart User' }}</span>
            <span class="font-mono text-gray-400">**42</span>
          </div>
        </div>
      </div>

      <div class="relative overflow-hidden rounded-3xl p-6 shadow-lg bg-gradient-to-br from-emerald-600 to-teal-800 text-white transform hover:-translate-y-1 transition-all duration-300">
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl transform translate-x-10 -translate-y-10"></div>
        <div class="relative z-10 flex flex-col h-full justify-between">
          <div class="flex justify-between items-start">
            <div class="flex items-center gap-2">
              <i class="pi pi-arrow-down-left text-green-300 text-xl"></i>
              <span class="font-medium text-emerald-100 tracking-wide">Total Income</span>
            </div>
            <div class="w-8 h-5 rounded bg-emerald-400/30 border border-emerald-300/30"></div>
          </div>
          <div class="mt-8 mb-4">
            <p class="text-4xl font-extrabold tracking-tight">{{ formatCurrency(totalIncome) }}</p>
          </div>
          <div class="flex justify-between items-center text-sm font-medium text-emerald-100">
            <span class="uppercase tracking-widest">Inflow</span>
            <span class="font-mono text-emerald-200">Visa</span>
          </div>
        </div>
      </div>

      <div class="relative overflow-hidden rounded-3xl p-6 shadow-lg bg-gradient-to-br from-orange-500 to-red-600 text-white transform hover:-translate-y-1 transition-all duration-300">
        <div class="absolute bottom-0 right-0 w-40 h-40 bg-yellow-500/20 rounded-full blur-2xl transform translate-x-10 translate-y-10"></div>
        <div class="relative z-10 flex flex-col h-full justify-between">
          <div class="flex justify-between items-start">
            <div class="flex items-center gap-2">
              <i class="pi pi-arrow-up-right text-orange-200 text-xl"></i>
              <span class="font-medium text-red-100 tracking-wide">Total Expense</span>
            </div>
            <div class="flex gap-1">
              <div class="w-4 h-4 rounded-full bg-red-400/50"></div>
              <div class="w-4 h-4 rounded-full bg-orange-400/50 -ml-2"></div>
            </div>
          </div>
          <div class="mt-8 mb-4">
            <p class="text-4xl font-extrabold tracking-tight">{{ formatCurrency(totalExpense) }}</p>
          </div>
          <div class="flex justify-between items-center text-sm font-medium text-red-100">
            <span class="uppercase tracking-widest">Outflow</span>
            <span class="font-mono text-red-200">Mastercard</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300 mb-8">
      <div class="flex items-center justify-between mb-6 border-b pb-3 border-gray-100 dark:border-gray-700">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">
          6-Month Cash Flow Trend
        </h3>
        <span class="text-sm font-medium text-gray-500 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full">Analytics</span>
      </div>
      <div class="h-80 w-full flex justify-center items-center">
        <Chart v-if="monthlyTrendData.datasets[0].data.length > 0" type="bar" :data="monthlyTrendData" :options="barChartOptions" class="w-full h-full" />
        <div v-else class="text-gray-400 flex flex-col items-center">
          <i class="pi pi-chart-bar text-4xl mb-2 opacity-50"></i>
          <p>Not enough data for trend analysis.</p>
        </div>
      </div>
    </div>

    <div v-if="budgetProgress.length > 0" class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300 mb-8">
      <div class="flex items-center justify-between mb-6 border-b pb-3 border-gray-100 dark:border-gray-700">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">
          Monthly Budget Limits
        </h3>
        <NuxtLink to="/settings" class="text-sm font-bold text-purple-600 dark:text-purple-400 hover:underline">
          Edit Limits
        </NuxtLink>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="budget in budgetProgress" :key="budget.category" class="flex flex-col gap-3 p-5 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-100 dark:border-gray-700 hover:shadow-sm transition-all">
          <div class="flex justify-between items-center mb-1">
            <div class="flex items-center gap-2 font-bold text-gray-700 dark:text-gray-300">
              <i :class="['pi', budget.icon, 'text-gray-400']"></i> {{ budget.category }}
            </div>
            <div class="text-sm">
              <span class="font-bold" :class="budget.status === 'danger' ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white'">
                {{ formatCurrency(budget.spent) }}
              </span>
              <span class="text-gray-400 font-medium text-xs"> / {{ formatCurrency(budget.limit) }}</span>
            </div>
          </div>
          <ProgressBar :value="budget.percentage" :showValue="false" class="h-3 rounded-full" :class="'budget-bar-' + budget.status"></ProgressBar>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <div class="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
          <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
            Income Breakdown
          </h3>
          <div v-if="incomeData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
            <Chart type="doughnut" :data="incomeData" :options="pieChartOptions" class="w-full max-w-[16rem]" />
          </div>
          <div v-else class="text-center text-gray-500 h-64 flex flex-col justify-center items-center"><i class="pi pi-chart-pie text-4xl mb-2 opacity-50"></i><p>No income data.</p></div>
        </div>

        <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
          <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
            Expense Breakdown
          </h3>
          <div v-if="expenseData.datasets[0].data.length > 0" class="flex justify-center items-center h-64">
            <Chart type="doughnut" :data="expenseData" :options="pieChartOptions" class="w-full max-w-[16rem]" />
          </div>
          <div v-else class="text-center text-gray-500 h-64 flex flex-col justify-center items-center"><i class="pi pi-chart-pie text-4xl mb-2 opacity-50"></i><p>No expense data.</p></div>
        </div>
      </div>

      <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300 flex flex-col h-full">
        <div class="flex items-center justify-between mb-6 border-b pb-3 border-gray-100 dark:border-gray-700">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Upcoming Bills</h3>
          <Button icon="pi pi-plus" rounded text severity="secondary" v-tooltip.top="'Add Bill'" @click="$router.push('/subscriptions')" />
        </div>

        <div class="flex-1 flex flex-col gap-4">
          <div v-if="subscriptions.length === 0" class="text-center text-gray-500 py-8">No upcoming bills!</div>
          
          <div v-for="sub in subscriptions.slice(0, 3)" :key="sub.id" class="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors border border-transparent dark:hover:border-gray-600">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg" :class="sub.colorClass">
                <i :class="['pi', sub.icon]"></i>
              </div>
              <div>
                <p class="font-bold text-gray-900 dark:text-white">{{ sub.name }}</p>
                <p class="text-xs font-bold" :class="getDaysLeft(sub.dueDate) <= 1 ? 'text-red-500' : 'text-gray-500 dark:text-gray-400'">
                  {{ getRelativeDateString(sub.dueDate) }}
                </p>
              </div>
            </div>
            <span class="font-bold text-gray-900 dark:text-white">{{ formatCurrency(sub.amount) }}</span>
          </div>
        </div>

        <Button label="View All Subscriptions" class="w-full mt-4 p-button-outlined p-button-secondary font-bold" @click="$router.push('/subscriptions')" />
      </div>
    </div>

    <div class="card p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 transition-colors duration-300">
      <h3 class="text-xl font-bold mb-6 border-b pb-3 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
        Recent Transactions
      </h3>
      
      <ul v-if="recentTransactions.length > 0" class="space-y-3">
        <li v-for="tx in recentTransactions" :key="tx.id" class="flex justify-between items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-2xl transition-all duration-300 border border-transparent dark:hover:border-gray-600">
          <div class="flex items-center gap-4">
            <div :class="tx.transaction_type === 'INCOME' ? 'bg-green-100 text-green-600 dark:bg-green-500/20 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400'" class="p-3 rounded-full h-12 w-12 flex items-center justify-center transition-colors duration-300">
              <i :class="tx.transaction_type === 'INCOME' ? 'pi pi-arrow-down-left' : 'pi pi-arrow-up-right'" class="text-xl font-bold"></i>
            </div>
            <div>
              <p class="font-bold text-gray-900 dark:text-white text-lg transition-colors duration-300">{{ tx.title }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400 transition-colors duration-300">{{ tx.date }} • <span class="font-medium">{{ tx.category }}</span></p>
            </div>
          </div>
          <span :class="tx.transaction_type === 'INCOME' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'" class="font-extrabold text-xl transition-colors duration-300">
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
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'primevue/chart'
import ProgressBar from 'primevue/progressbar'
import Button from 'primevue/button'
import { useCurrency } from '~/composables/useCurrency'
import { useAuth } from '~/composables/useAuth'
import { useSubscriptions } from '~/composables/useSubscriptions'

definePageMeta({ layout: 'default' })

const router = useRouter()
const { token, user } = useAuth()
const API_BASE = 'https://smart-finance-app-6lgi.onrender.com/api'
const { formatCurrency } = useCurrency()

const { loadSubscriptions, subscriptions, getDaysLeft, getRelativeDateString } = useSubscriptions()

const { data } = await useFetch(`${API_BASE}/transactions/`, {
  headers: { Authorization: computed(() => `Bearer ${token.value}`) },
})
const transactions = computed(() => (data.value && Array.isArray(data.value) ? data.value : []))

const savedBudgets = ref<Record<string, number>>({}) 

onMounted(() => {
  loadSubscriptions() 
  const stored = localStorage.getItem('budgetLimits')
  if (stored) {
    savedBudgets.value = JSON.parse(stored)
  }
})

//  GELİŞMİŞ ALGORİTMA (SON 6 AYIN HESAPLANMASI) 
const monthlyTrendData = computed(() => {
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const labels: string[] = [];
  const incomeData: number[] = [];
  const expenseData: number[] = [];

  // Geriye doğru 6 ayı dönüyoruz
  for (let i = 5; i >= 0; i--) {
    const d = new Date();
    d.setMonth(d.getMonth() - i);
    
    labels.push(`${monthNames[d.getMonth()]} ${d.getFullYear()}`);

    // İlgili ayın işlemlerini bul
    const monthTx = transactions.value.filter(t => {
      const txDate = new Date(t.date);
      return txDate.getMonth() === d.getMonth() && txDate.getFullYear() === d.getFullYear();
    });

    const inc = monthTx.filter(t => t.transaction_type === 'INCOME').reduce((sum, t) => sum + Number(t.amount), 0);
    const exp = monthTx.filter(t => t.transaction_type === 'EXPENSE').reduce((sum, t) => sum + Number(t.amount), 0);

    incomeData.push(inc);
    expenseData.push(exp);
  }

  return {
    labels,
    datasets: [
      {
        label: 'Income',
        backgroundColor: '#10B981', // Yeşil
        data: incomeData,
        borderRadius: 6 
      },
      {
        label: 'Expense',
        backgroundColor: '#EF4444', // Kırmızı
        data: expenseData,
        borderRadius: 6
      }
    ]
  };
});

// TREND GRAFİĞİ (BAR) AYARLARI
const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { usePointStyle: true, font: { family: 'Inter, sans-serif' } } },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)', padding: 12, cornerRadius: 8,
      callbacks: {
        label: function(context: any) {
          return context.dataset.label + ': ' + formatCurrency(context.raw);
        }
      }
    }
  },
  scales: {
    x: { grid: { display: false } },
    y: { border: { display: false }, grid: { color: 'rgba(156, 163, 175, 0.2)' } }
  }
};

// ESKİ HESAPLAMALAR 
const currentMonthExpenses = computed(() => {
  const currentMonth = new Date().getMonth()
  const currentYear = new Date().getFullYear()
  const monthlyExpenses = transactions.value.filter(t => {
    if (t.transaction_type !== 'EXPENSE') return false
    const txDate = new Date(t.date)
    return txDate.getMonth() === currentMonth && txDate.getFullYear() === currentYear
  })
  const totals: Record<string, number> = {}
  monthlyExpenses.forEach(tx => {
    totals[tx.category] = (totals[tx.category] || 0) + Number(tx.amount)
  })
  return totals
})

const budgetProgress = computed(() => {
  const result: any[] = []
  const categories = ['Food', 'Rent', 'Transport', 'Entertainment']
  const icons: Record<string, string> = { Food: 'pi-shopping-cart', Rent: 'pi-home', Transport: 'pi-car', Entertainment: 'pi-ticket' }

  categories.forEach(cat => {
    const limit = savedBudgets.value[cat]
    if (limit && limit > 0) {
      const spent = currentMonthExpenses.value[cat] || 0
      const percentage = Math.min(Math.round((spent / limit) * 100), 100)
      
      let status = 'success'
      if (percentage >= 90) status = 'danger'
      else if (percentage >= 70) status = 'warning'

      result.push({ category: cat, icon: icons[cat] || 'pi-tag', limit: limit, spent: spent, percentage: percentage, status: status })
    }
  })
  return result
})

const totalIncome = computed(() => transactions.value.filter(t => t.transaction_type === 'INCOME').reduce((sum, t) => sum + Number(t.amount), 0))
const totalExpense = computed(() => transactions.value.filter(t => t.transaction_type === 'EXPENSE').reduce((sum, t) => sum + Number(t.amount), 0))
const balance = computed(() => totalIncome.value - totalExpense.value)
const recentTransactions = computed(() => [...transactions.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 5))

// PASTA GRAFİĞİ AYARLARI
const pieChartOptions = {
  cutout: '70%',
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, padding: 15, font: { family: 'Inter, sans-serif', size: 12 } } },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.9)', padding: 12, cornerRadius: 8,
      callbacks: {
        label: function(context: any) {
          let label = context.label || '';
          if (label) label += ': ';
          if (context.parsed !== null) label += formatCurrency(context.parsed);
          return label;
        }
      }
    }
  }
}

const incomeData = computed(() => {
  const incomes = transactions.value.filter(t => t.transaction_type === 'INCOME')
  const totals = incomes.reduce((acc, curr) => { acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount); return acc }, {} as Record<string, number>)
  return {
    labels: Object.keys(totals),
    datasets: [{ data: Object.values(totals), backgroundColor: ['#3B82F6', '#14B8A6', '#10B981', '#F59E0B', '#8B5CF6'], borderWidth: 0, hoverOffset: 4 }]
  }
})

const expenseData = computed(() => {
  const expenses = transactions.value.filter(t => t.transaction_type === 'EXPENSE')
  const totals = expenses.reduce((acc, curr) => { acc[curr.category] = (acc[curr.category] || 0) + Number(curr.amount); return acc }, {} as Record<string, number>)
  return {
    labels: Object.keys(totals),
    datasets: [{ data: Object.values(totals), backgroundColor: ['#EF4444', '#EC4899', '#F97316', '#6366F1', '#6B7280', '#06B6D4'], borderWidth: 0, hoverOffset: 4 }]
  }
})
</script>

<style scoped>
:deep(.budget-bar-success .p-progressbar-value) { background-color: #10B981 !important; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
:deep(.budget-bar-warning .p-progressbar-value) { background-color: #F59E0B !important; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
:deep(.budget-bar-danger .p-progressbar-value) { background-color: #EF4444 !important; transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
:deep(.p-progressbar) { background-color: #e5e7eb; }
.dark :deep(.p-progressbar) { background-color: #374151; }
</style>