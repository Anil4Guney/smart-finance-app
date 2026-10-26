<template>
  <div class="lg:p-2 max-w-[1400px] mx-auto">
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6 sm:mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Recurring Income & Expenses</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-300">
          Salary, rent, bills, subscriptions and installments are added to your transactions automatically every month.
        </p>
      </div>
      <Button label="Add Recurring" icon="pi pi-plus" @click="openAddModal" class="shadow-sm shrink-0" />
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
      <div class="card p-4 sm:p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Monthly Income</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400">{{ formatCurrency(monthlyIncome) }}</p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Monthly Expenses</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-gray-900 dark:text-white">{{ formatCurrency(monthlyExpense) }}</p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Fixed Net / Month</h3>
        <p class="text-xl sm:text-3xl font-extrabold" :class="monthlyIncome - monthlyExpense >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'">
          {{ formatCurrency(monthlyIncome - monthlyExpense) }}
        </p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Installments Left</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-rose-600 dark:text-rose-400">{{ formatCurrency(installmentDebt) }}</p>
      </div>
    </div>

    <div class="card p-4 sm:p-6 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 min-h-[400px]">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <SelectButton
          v-model="filter"
          :options="filterOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          class="w-full sm:w-auto [&_.p-togglebutton]:grow [&_.p-togglebutton]:px-2 sm:[&_.p-togglebutton]:px-3 [&_.p-togglebutton-label]:text-xs sm:[&_.p-togglebutton-label]:text-sm"
        />
        <span class="text-sm text-gray-500 dark:text-gray-400">{{ visibleItems.length }} item(s)</span>
      </div>

      <div v-if="visibleItems.length === 0" class="text-center text-gray-500 flex flex-col items-center justify-center h-64">
        <i class="pi pi-calendar-times text-5xl mb-4 opacity-30"></i>
        <p class="font-medium text-lg">Nothing here yet.</p>
        <p class="text-sm mt-1">Add your salary, rent or a bill to see your month-end forecast on the dashboard.</p>
        <Button label="Add Recurring" class="mt-6 p-button-outlined" @click="openAddModal" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="sub in visibleItems"
          :key="sub.id"
          class="flex flex-col p-4 sm:p-6 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all relative group"
          :class="{ 'opacity-60': !sub.isActive }"
        >
          <div class="absolute top-4 right-4 sm:opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
            <button @click="openEditModal(sub)" aria-label="Edit" class="text-gray-400 hover:text-blue-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
              <i class="pi pi-pencil text-sm"></i>
            </button>
            <button @click="confirmDelete(sub)" aria-label="Delete" class="text-gray-400 hover:text-red-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
              <i class="pi pi-trash text-sm"></i>
            </button>
          </div>

          <div class="flex items-center gap-4 mb-5 pr-16">
            <div class="w-14 h-14 shrink-0 rounded-2xl flex items-center justify-center text-2xl shadow-sm" :class="sub.colorClass">
              <i :class="['pi', sub.icon]"></i>
            </div>
            <div class="min-w-0">
              <h3 class="font-bold text-xl text-gray-900 dark:text-white truncate">{{ sub.name }}</h3>
              <div class="flex flex-wrap gap-1 mt-1">
                <span class="px-2 py-0.5 rounded-md text-xs font-bold bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                  {{ RECURRING_KINDS[sub.kind]?.label || 'Other' }}
                </span>
                <span v-if="!sub.isActive" class="px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                  {{ sub.kind === 'INSTALLMENT' ? 'Paid off' : 'Paused' }}
                </span>
                <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold"
                  :class="sub.transactionType === 'EXPENSE' && getDaysLeft(sub.dueDate) <= 1 ? 'bg-red-100 text-red-600 dark:bg-red-900/30' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'">
                  <i class="pi pi-clock text-[10px]"></i> {{ getRelativeDateString(sub.dueDate) }}
                </span>
                <span v-if="!sub.autoPay" class="px-2 py-0.5 rounded-md text-xs font-bold bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">Manual</span>
              </div>
            </div>
          </div>

          <div v-if="sub.totalInstallments" class="mb-4">
            <div class="flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
              <span>{{ sub.installmentsPaid }} / {{ sub.totalInstallments }} paid</span>
              <span>{{ formatCurrency((sub.remainingInstallments || 0) * sub.amount) }} left</span>
            </div>
            <ProgressBar :value="Math.round((sub.installmentsPaid / sub.totalInstallments) * 100)" :showValue="false" class="h-2 rounded-full" />
          </div>

          <div class="mt-auto flex items-end justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
            <span class="text-sm text-gray-500 font-medium">{{ sub.transactionType === 'INCOME' ? 'Monthly income' : 'Monthly payment' }}</span>
            <span class="text-2xl font-extrabold" :class="sub.transactionType === 'INCOME' ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-900 dark:text-white'">
              {{ sub.transactionType === 'INCOME' ? '+' : '' }}{{ formatCurrency(sub.amount) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add / edit -->
    <Dialog
      v-model:visible="showModal"
      modal
      :draggable="false"
      :header="editingId ? 'Edit Recurring Item' : 'Add Recurring Item'"
      :style="{ width: '520px' }"
      :breakpoints="{ '640px': '95vw' }"
    >
      <form @submit.prevent="handleSave" class="flex flex-col gap-5 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">What is it?</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(meta, key) in RECURRING_KINDS"
              :key="key"
              type="button"
              @click="selectKind(key)"
              class="flex flex-col items-center gap-1 p-3 rounded-xl border-2 text-sm font-semibold transition-colors"
              :class="form.kind === key
                ? 'border-purple-500 bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-gray-300'"
            >
              <i :class="['pi', meta.icon, 'text-lg']"></i>
              {{ meta.label }}
            </button>
          </div>
        </div>

        <div v-if="form.kind === 'OTHER'" class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Type</label>
          <SelectButton v-model="form.transactionType" :options="typeOptions" optionLabel="label" optionValue="value" :allowEmpty="false" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-name" class="font-bold text-gray-700 dark:text-gray-300">Name</label>
          <InputText id="rec-name" v-model="form.name" :placeholder="namePlaceholder" required class="w-full" />
        </div>

        <div v-if="form.kind === 'INSTALLMENT'" class="flex flex-col gap-2">
          <label for="rec-count" class="font-bold text-gray-700 dark:text-gray-300">Number of installments</label>
          <InputNumber inputId="rec-count" v-model="form.totalInstallments" :min="1" :max="120" showButtons class="w-full" />
          <SelectButton v-model="form.amountMode" :options="amountModeOptions" optionLabel="label" optionValue="value" :allowEmpty="false" class="mt-1" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-amount" class="font-bold text-gray-700 dark:text-gray-300">
            {{ form.kind === 'INSTALLMENT' && form.amountMode === 'TOTAL' ? 'Total price' : 'Monthly amount' }}
          </label>
          <div class="flex gap-2">
            <Dropdown v-model="form.currency" :options="currencyOptions" optionLabel="short" optionValue="value" aria-label="Currency" class="w-32 shrink-0" />
            <InputNumber :key="form.currency" inputId="rec-amount" v-model="form.amount" mode="currency" :currency="form.currency" :min="0" :maxFractionDigits="2" required class="w-full" />
          </div>
          <p v-if="form.kind === 'INSTALLMENT' && form.amountMode === 'TOTAL' && monthlyPayment" class="text-xs text-gray-500 dark:text-gray-400">
            {{ form.totalInstallments }} × {{ formatIn(monthlyPayment, form.currency) }} per month
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-date" class="font-bold text-gray-700 dark:text-gray-300">{{ dateLabel }}</label>
          <Calendar inputId="rec-date" v-model="form.dueDate" showIcon dateFormat="dd/mm/yy" class="w-full" required />
          <p v-if="form.kind === 'INSTALLMENT' && !editingId" class="text-xs text-gray-500 dark:text-gray-400">
            Installments dated before today are counted as already paid.
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-category" class="font-bold text-gray-700 dark:text-gray-300">Category <span class="font-normal text-gray-400">(optional)</span></label>
          <Dropdown inputId="rec-category" v-model="form.category" :options="categoryOptions" editable :placeholder="defaultCategory" class="w-full" />
        </div>

        <div class="flex items-center justify-between gap-4 p-3 rounded-xl bg-gray-50 dark:bg-gray-900/50">
          <div>
            <p class="font-bold text-gray-700 dark:text-gray-300 text-sm">Add to transactions automatically</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Turn off if you prefer to record it yourself.</p>
          </div>
          <ToggleSwitch v-model="form.autoPay" />
        </div>

        <div v-if="formError" class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-3 rounded-lg text-sm font-medium border border-red-100 dark:border-red-800/50">
          <i class="pi pi-exclamation-circle mr-1"></i> {{ formError }}
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <Button type="button" label="Cancel" severity="secondary" text @click="showModal = false" />
          <Button type="submit" :label="editingId ? 'Update' : 'Save'" icon="pi pi-check" :loading="isSaving" />
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
import Dropdown from 'primevue/dropdown'
import SelectButton from 'primevue/selectbutton'
import ToggleSwitch from 'primevue/toggleswitch'
import ProgressBar from 'primevue/progressbar'
import { useCurrency } from '~/composables/useCurrency'
import { useSubscriptions, RECURRING_KINDS, type RecurringKind } from '~/composables/useSubscriptions'

definePageMeta({ layout: 'default' })

const { formatCurrency, currentCurrency, currencyOptions, toUSD, fromUSD } = useCurrency()
const { subscriptions, addSubscription, updateSubscription, deleteSubscription, getDaysLeft, getRelativeDateString, loadSubscriptions } = useSubscriptions()

onMounted(() => {
  loadSubscriptions()
})

// --- List ---
const filter = ref<'ALL' | 'INCOME' | 'EXPENSE' | 'INSTALLMENT'>('ALL')
const filterOptions = [
  { label: 'All', value: 'ALL' },
  { label: 'Income', value: 'INCOME' },
  { label: 'Expenses', value: 'EXPENSE' },
  { label: 'Installments', value: 'INSTALLMENT' },
]

const visibleItems = computed(() => {
  const items = subscriptions.value.filter(s => {
    if (filter.value === 'INSTALLMENT') return s.kind === 'INSTALLMENT'
    if (filter.value === 'ALL') return true
    return s.transactionType === filter.value
  })
  // Active first, then by next date
  return [...items].sort((a, b) =>
    Number(b.isActive) - Number(a.isActive) || a.dueDate.getTime() - b.dueDate.getTime())
})

const active = computed(() => subscriptions.value.filter(s => s.isActive))
const monthlyIncome = computed(() => active.value.filter(s => s.transactionType === 'INCOME').reduce((t, s) => t + s.amount, 0))
const monthlyExpense = computed(() => active.value.filter(s => s.transactionType === 'EXPENSE').reduce((t, s) => t + s.amount, 0))
const installmentDebt = computed(() => active.value
  .filter(s => s.totalInstallments)
  .reduce((t, s) => t + (s.remainingInstallments || 0) * s.amount, 0))

const confirmDelete = async (sub: any) => {
  const ok = window.confirm(
    `Delete "${sub.name}"?\n\nTransactions it added automatically will be deleted too.`
  )
  if (ok) await deleteSubscription(sub.id)
}

// --- Form ---
const showModal = ref(false)
const isSaving = ref(false)
const editingId = ref<number | null>(null)
const formError = ref('')

const emptyForm = () => ({
  kind: 'SUBSCRIPTION' as RecurringKind,
  transactionType: 'EXPENSE' as 'INCOME' | 'EXPENSE',
  name: '',
  amount: null as number | null,
  currency: currentCurrency.value,
  amountMode: 'TOTAL' as 'TOTAL' | 'MONTHLY',
  totalInstallments: 6 as number | null,
  dueDate: null as Date | null,
  category: '',
  autoPay: true,
})
const form = ref(emptyForm())

const typeOptions = [
  { label: 'Income', value: 'INCOME' },
  { label: 'Expense', value: 'EXPENSE' },
]
const amountModeOptions = [
  { label: 'I know the total', value: 'TOTAL' },
  { label: 'I know the monthly', value: 'MONTHLY' },
]
const categoryOptions = ['Food', 'Rent', 'Bills', 'Salary', 'Freelance', 'Entertainment', 'Transport', 'Installments', 'Other']
const defaultCategoryByKind: Record<RecurringKind, string> = {
  SALARY: 'Salary', RENT: 'Rent', BILL: 'Bills', SUBSCRIPTION: 'Bills', INSTALLMENT: 'Installments', OTHER: 'Other',
}
const defaultCategory = computed(() => `Default: ${defaultCategoryByKind[form.value.kind]}`)

const namePlaceholder = computed(() => ({
  SALARY: 'e.g. Salary, Scholarship',
  RENT: 'e.g. Apartment rent',
  BILL: 'e.g. Electricity, Internet',
  SUBSCRIPTION: 'e.g. Netflix, Spotify, Gym',
  INSTALLMENT: 'e.g. iPhone, Washing machine',
  OTHER: 'e.g. Pocket money',
}[form.value.kind]))

const dateLabel = computed(() => ({
  SALARY: 'Next payday',
  INSTALLMENT: 'First installment date',
}[form.value.kind as string] || 'Next payment date'))

const monthlyPayment = computed(() => {
  const { amount, totalInstallments } = form.value
  if (!amount || !totalInstallments) return 0
  return Math.round((amount / totalInstallments) * 100) / 100
})

const formatIn = (value: number, currency: string) =>
  new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(value)

const selectKind = (kind: RecurringKind) => {
  form.value.kind = kind
  const fixedType = RECURRING_KINDS[kind].type
  if (fixedType) form.value.transactionType = fixedType
}

const openAddModal = () => {
  editingId.value = null
  form.value = emptyForm()
  formError.value = ''
  showModal.value = true
}

const openEditModal = (sub: any) => {
  editingId.value = sub.id
  formError.value = ''
  form.value = {
    ...emptyForm(),
    kind: sub.kind,
    transactionType: sub.transactionType,
    name: sub.name,
    amount: fromUSD(sub.amount),
    amountMode: 'MONTHLY',
    totalInstallments: sub.totalInstallments,
    dueDate: new Date(sub.dueDate),
    category: sub.category,
    autoPay: sub.autoPay,
  }
  showModal.value = true
}

const handleSave = async () => {
  const f = form.value
  formError.value = ''
  if (!f.name.trim() || !f.amount || !f.dueDate) {
    formError.value = 'Please fill in the name, amount and date.'
    return
  }
  if (f.kind === 'INSTALLMENT' && !f.totalInstallments) {
    formError.value = 'Please enter the number of installments.'
    return
  }

  const monthly = f.kind === 'INSTALLMENT' && f.amountMode === 'TOTAL' ? monthlyPayment.value : f.amount
  const payload = {
    name: f.name.trim(),
    amount: toUSD(monthly, f.currency), // stored in USD like everything else
    kind: f.kind,
    transactionType: f.transactionType,
    category: f.category?.trim() || '',
    dueDate: f.dueDate,
    totalInstallments: f.totalInstallments,
    autoPay: f.autoPay,
  }

  isSaving.value = true
  try {
    if (editingId.value) {
      await updateSubscription(editingId.value, payload)
    } else {
      await addSubscription(payload)
    }
    showModal.value = false
  } catch (error: any) {
    const data = error?.data || {}
    const first = Object.values(data)[0]
    formError.value = (Array.isArray(first) ? first[0] : first) || 'Could not save. Please try again.'
  } finally {
    isSaving.value = false
  }
}
</script>
