<template>
  <div class="lg:p-2 max-w-[1400px] mx-auto">
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6 sm:mb-8">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Tekrarlayan Gelir ve Giderler</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Maaş, kira, fatura, abonelik ve taksitlerin her ay işlemlerine otomatik eklenir.
        </p>
      </div>
      <Button label="Ekle" icon="pi pi-plus" @click="openAddModal" class="shadow-sm shrink-0" />
    </div>

    <!-- Özet -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
      <div class="card p-4 sm:p-6 rounded-3xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Aylık gelir</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 tabular">{{ formatCurrency(monthlyIncome) }}</p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Aylık gider</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-gray-900 dark:text-white tabular">{{ formatCurrency(monthlyExpense) }}</p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Sabit net / ay</h3>
        <p class="text-xl sm:text-3xl font-extrabold tabular" :class="monthlyIncome - monthlyExpense >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">
          {{ formatCurrency(monthlyIncome - monthlyExpense) }}
        </p>
      </div>
      <div class="card p-4 sm:p-6 rounded-3xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
        <h3 class="text-gray-500 dark:text-gray-400 text-xs sm:text-sm font-bold uppercase tracking-wider mb-2">Kalan taksit borcu</h3>
        <p class="text-xl sm:text-3xl font-extrabold text-rose-600 dark:text-rose-400 tabular">{{ formatCurrency(installmentDebt) }}</p>
      </div>
    </div>

    <div class="card p-4 sm:p-6 rounded-3xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 min-h-[400px]">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <SelectButton
          v-model="filter"
          :options="filterOptions"
          optionLabel="label"
          optionValue="value"
          :allowEmpty="false"
          class="w-full sm:w-auto [&_.p-togglebutton]:grow [&_.p-togglebutton]:px-2 sm:[&_.p-togglebutton]:px-3 [&_.p-togglebutton-label]:text-xs sm:[&_.p-togglebutton-label]:text-sm"
        />
        <span class="text-sm text-gray-500 dark:text-gray-400">{{ visibleItems.length }} kayıt</span>
      </div>

      <div v-if="visibleItems.length === 0" class="text-center text-gray-500 flex flex-col items-center justify-center h-64">
        <i class="pi pi-calendar-times text-5xl mb-4 opacity-30"></i>
        <p class="font-medium text-lg">Henüz bir şey yok.</p>
        <p class="text-sm mt-1 max-w-sm">Maaşını, kiranı veya bir faturanı ekle; panelde ay sonu tahminini görürsün.</p>
        <Button label="Ekle" class="mt-6 p-button-outlined" @click="openAddModal" />
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="sub in visibleItems"
          :key="sub.id"
          class="flex flex-col p-4 sm:p-6 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all relative group"
          :class="{ 'opacity-60': !sub.isActive }"
        >
          <div class="absolute top-4 right-4 sm:opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
            <button @click="openEditModal(sub)" aria-label="Düzenle" class="text-gray-400 hover:text-emerald-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
              <i class="pi pi-pencil text-sm"></i>
            </button>
            <button @click="confirmDelete(sub)" aria-label="Sil" class="text-gray-400 hover:text-rose-500 bg-white dark:bg-gray-800 rounded-full w-8 h-8 flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700 transition-colors">
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
                  {{ RECURRING_KINDS[sub.kind]?.label || 'Diğer' }}
                </span>
                <span v-if="!sub.isActive" class="px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">
                  {{ sub.kind === 'INSTALLMENT' ? 'Tamamlandı' : 'Duraklatıldı' }}
                </span>
                <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-bold"
                  :class="sub.transactionType === 'EXPENSE' && getDaysLeft(sub.dueDate) <= 1 ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/30' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'">
                  <i class="pi pi-clock text-[10px]"></i> {{ getRelativeDateString(sub.dueDate) }}
                </span>
                <span v-if="!sub.autoPay" class="px-2 py-0.5 rounded-md text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">Elle</span>
              </div>
            </div>
          </div>

          <div v-if="sub.totalInstallments" class="mb-4">
            <div class="flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
              <span>{{ sub.installmentsPaid }} / {{ sub.totalInstallments }} ödendi</span>
              <span>{{ formatCurrency(sub.remainingAmount ?? ((sub.remainingInstallments || 0) * sub.amount)) }} kaldı</span>
            </div>
            <ProgressBar :value="Math.round((sub.installmentsPaid / sub.totalInstallments) * 100)" :showValue="false" class="h-2 rounded-full" />
          </div>

          <div class="mt-auto flex items-end justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
            <span class="text-sm text-gray-500 font-medium">{{ sub.transactionType === 'INCOME' ? 'Aylık gelir' : 'Aylık ödeme' }}</span>
            <span class="text-2xl font-extrabold tabular" :class="sub.transactionType === 'INCOME' ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-900 dark:text-white'">
              {{ sub.transactionType === 'INCOME' ? '+' : '' }}{{ formatCurrency(sub.amount) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Ekle / düzenle -->
    <Dialog
      v-model:visible="showModal"
      modal
      :draggable="false"
      :header="editingId ? 'Kaydı Düzenle' : 'Tekrarlayan Kayıt Ekle'"
      :style="{ width: '520px' }"
      :breakpoints="{ '640px': '95vw' }"
    >
      <form @submit.prevent="handleSave" class="flex flex-col gap-5 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Bu nedir?</label>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="(meta, key) in RECURRING_KINDS"
              :key="key"
              type="button"
              @click="selectKind(key)"
              class="flex flex-col items-center gap-1 p-3 rounded-xl border-2 text-sm font-semibold transition-colors"
              :class="form.kind === key
                ? 'border-emerald-500 bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
                : 'border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-gray-300'"
            >
              <i :class="['pi', meta.icon, 'text-lg']"></i>
              {{ meta.label }}
            </button>
          </div>
        </div>

        <div v-if="form.kind === 'OTHER'" class="flex flex-col gap-2">
          <label class="font-bold text-gray-700 dark:text-gray-300">Tür</label>
          <SelectButton v-model="form.transactionType" :options="typeOptions" optionLabel="label" optionValue="value" :allowEmpty="false" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-name" class="font-bold text-gray-700 dark:text-gray-300">Ad</label>
          <InputText id="rec-name" v-model="form.name" :placeholder="namePlaceholder" required class="w-full" />
        </div>

        <div v-if="form.kind === 'INSTALLMENT'" class="flex flex-col gap-2">
          <label for="rec-count" class="font-bold text-gray-700 dark:text-gray-300">Taksit sayısı</label>
          <InputNumber inputId="rec-count" v-model="form.totalInstallments" :min="1" :max="120" showButtons class="w-full" />
          <SelectButton v-model="form.amountMode" :options="amountModeOptions" optionLabel="label" optionValue="value" :allowEmpty="false" class="mt-1" />
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-amount" class="font-bold text-gray-700 dark:text-gray-300">
            {{ form.kind === 'INSTALLMENT' && form.amountMode === 'TOTAL' ? 'Toplam fiyat' : 'Aylık tutar' }}
          </label>
          <div class="flex gap-2">
            <Dropdown v-model="form.currency" :options="currencyOptions" optionLabel="short" optionValue="value" aria-label="Para birimi" class="w-32 shrink-0" />
            <InputNumber :key="form.currency" inputId="rec-amount" v-model="form.amount" mode="currency" :currency="form.currency" :min="0" :maxFractionDigits="2" required class="w-full" />
          </div>
          <p v-if="form.kind === 'INSTALLMENT' && form.amountMode === 'TOTAL' && monthlyPayment" class="text-xs text-gray-500 dark:text-gray-400">
            {{ form.totalInstallments }} × {{ formatIn(monthlyPayment, form.currency) }} (son taksit küsuratı kapatır)
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-date" class="font-bold text-gray-700 dark:text-gray-300">{{ dateLabel }}</label>
          <Calendar inputId="rec-date" v-model="form.dueDate" showIcon dateFormat="dd.mm.yy" class="w-full" required />
          <p v-if="form.kind === 'INSTALLMENT' && !editingId" class="text-xs text-gray-500 dark:text-gray-400">
            Bugünden önceki taksitler ödenmiş sayılır.
          </p>
        </div>

        <div class="flex flex-col gap-2">
          <label for="rec-category" class="font-bold text-gray-700 dark:text-gray-300">Kategori <span class="font-normal text-gray-400">(isteğe bağlı)</span></label>
          <Dropdown
            inputId="rec-category"
            v-model="form.category"
            :options="categoryItems"
            optionLabel="label"
            optionValue="value"
            showClear
            :placeholder="defaultCategory"
            class="w-full"
          />
        </div>

        <div class="flex items-center justify-between gap-4 p-3 rounded-xl bg-gray-50 dark:bg-gray-900/50">
          <div>
            <p class="font-bold text-gray-700 dark:text-gray-300 text-sm">İşlemlere otomatik ekle</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Kendin girmek istersen kapat.</p>
          </div>
          <ToggleSwitch v-model="form.autoPay" />
        </div>

        <div v-if="formError" class="bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 p-3 rounded-lg text-sm font-medium border border-rose-100 dark:border-rose-800/50">
          <i class="pi pi-exclamation-circle mr-1"></i> {{ formError }}
        </div>

        <div class="flex justify-end gap-3 mt-2">
          <Button type="button" label="Vazgeç" severity="secondary" text @click="showModal = false" />
          <Button type="submit" :label="editingId ? 'Güncelle' : 'Kaydet'" icon="pi pi-check" :loading="isSaving" />
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

// --- Liste ---
const filter = ref<'ALL' | 'INCOME' | 'EXPENSE' | 'INSTALLMENT'>('ALL')
const filterOptions = [
  { label: 'Tümü', value: 'ALL' },
  { label: 'Gelir', value: 'INCOME' },
  { label: 'Gider', value: 'EXPENSE' },
  { label: 'Taksit', value: 'INSTALLMENT' },
]

const visibleItems = computed(() => {
  const items = subscriptions.value.filter(s => {
    if (filter.value === 'INSTALLMENT') return s.kind === 'INSTALLMENT'
    if (filter.value === 'ALL') return true
    return s.transactionType === filter.value
  })
  // Aktifler önce, sonra sıradaki tarihe göre
  return [...items].sort((a, b) =>
    Number(b.isActive) - Number(a.isActive) || a.dueDate.getTime() - b.dueDate.getTime())
})

const active = computed(() => subscriptions.value.filter(s => s.isActive))
const monthlyIncome = computed(() => active.value.filter(s => s.transactionType === 'INCOME').reduce((t, s) => t + s.amount, 0))
const monthlyExpense = computed(() => active.value.filter(s => s.transactionType === 'EXPENSE').reduce((t, s) => t + s.amount, 0))
const installmentDebt = computed(() => active.value
  .filter(s => s.totalInstallments)
  .reduce((t, s) => t + (s.remainingAmount ?? (s.remainingInstallments || 0) * s.amount), 0))

const confirmDelete = async (sub: any) => {
  const ok = window.confirm(
    `"${sub.name}" silinsin mi?\n\nBu kayıt tarafından otomatik eklenen işlemler de silinir.`
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
  category: '' as string | null,
  autoPay: true,
})
const form = ref(emptyForm())

const typeOptions = [
  { label: 'Gelir', value: 'INCOME' },
  { label: 'Gider', value: 'EXPENSE' },
]
const amountModeOptions = [
  { label: 'Toplamı biliyorum', value: 'TOTAL' },
  { label: 'Aylığı biliyorum', value: 'MONTHLY' },
]
const categoryItems = categoryChoices(CATEGORY_KEYS)
const defaultCategoryByKind: Record<RecurringKind, string> = {
  SALARY: 'Salary', RENT: 'Rent', BILL: 'Bills', SUBSCRIPTION: 'Bills', INSTALLMENT: 'Installments', OTHER: 'Other',
}
const defaultCategory = computed(() => `Varsayılan: ${categoryLabel(defaultCategoryByKind[form.value.kind])}`)

const namePlaceholder = computed(() => ({
  SALARY: 'ör. Maaş, Burs',
  RENT: 'ör. Ev kirası',
  BILL: 'ör. Elektrik, İnternet',
  SUBSCRIPTION: 'ör. Netflix, Spotify, Spor salonu',
  INSTALLMENT: 'ör. Telefon, Çamaşır makinesi',
  OTHER: 'ör. Harçlık',
}[form.value.kind]))

const dateLabel = computed(() => ({
  SALARY: 'Sonraki maaş günü',
  INSTALLMENT: 'İlk taksit tarihi',
}[form.value.kind as string] || 'Sonraki ödeme tarihi'))

const monthlyPayment = computed(() => {
  const { amount, totalInstallments } = form.value
  if (!amount || !totalInstallments) return 0
  return Math.round((amount / totalInstallments) * 100) / 100
})

const formatIn = (value: number, currency: string) =>
  new Intl.NumberFormat(LOCALE, { style: 'currency', currency }).format(value)

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
  const hasTotal = !!sub.totalPrice
  form.value = {
    ...emptyForm(),
    kind: sub.kind,
    transactionType: sub.transactionType,
    name: sub.name,
    amount: fromUSD(hasTotal ? sub.totalPrice : sub.amount),
    amountMode: hasTotal ? 'TOTAL' : 'MONTHLY',
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
    formError.value = 'Lütfen ad, tutar ve tarihi doldur.'
    return
  }
  if (f.kind === 'INSTALLMENT' && !f.totalInstallments) {
    formError.value = 'Lütfen taksit sayısını gir.'
    return
  }

  // Tutarlar her yerde olduğu gibi USD olarak saklanır
  const isTotalMode = f.kind === 'INSTALLMENT' && f.amountMode === 'TOTAL'
  const totalUSD = isTotalMode ? toUSD(f.amount, f.currency) : null
  const monthlyUSD = isTotalMode
    ? Math.round((totalUSD! / f.totalInstallments!) * 100) / 100
    : toUSD(f.amount, f.currency)

  const payload = {
    name: f.name.trim(),
    amount: monthlyUSD,
    totalPrice: totalUSD,
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
    formError.value = (Array.isArray(first) ? first[0] : first) || 'Kaydedilemedi. Lütfen tekrar dene.'
  } finally {
    isSaving.value = false
  }
}
</script>
