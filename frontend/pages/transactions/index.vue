<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-surface-700 dark:text-surface-200">
          Transactions
        </h1>
        <p class="mt-2 text-surface-600 dark:text-surface-400">
          Manage your income and expenses here.
        </p>
      </div>
      <Button label="Add New" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div v-if="error" class="mt-4 text-red-600">
      Error loading data: {{ error }}
    </div>

    <div class="mt-6 transactions-table-wrapper">
      <DataTable
        :value="tableData"
        dataKey="id"
        tableStyle="min-width: 50rem"
        :loading="pending"
        stripedRows
        class="p-datatable-sm p-datatable-striped p-datatable-hoverable"
      >
        <Column field="title" header="Title" />
        <Column field="amount" header="Amount">
          <template #body="{ data }">
            {{ formatCurrency(data.amount) }}
          </template>
        </Column>
        <Column field="category" header="Category" />
        <Column field="description" header="Description">
          <template #body="{ data }">
            <span class="text-surface-600 dark:text-surface-400 text-sm">
              {{ data.description || '—' }}
            </span>
          </template>
        </Column>
        <Column field="transaction_type" header="Type">
          <template #body="{ data }">
            <Tag
              :value="data.transaction_type"
              :severity="data.transaction_type === 'INCOME' ? 'success' : 'danger'"
            />
          </template>
        </Column>
        <Column field="date" header="Date" />
        <Column header="Actions" style="width: 100px">
          <template #body="{ data }">
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              v-tooltip.top="'Delete'"
              @click="confirmDelete(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog
      v-model:visible="showDialog"
      modal
      header="Add New Transaction"
      :style="{ width: '500px' }"
      @hide="resetForm"
    >
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-surface-200 dark:border-surface-700">
          <Button 
            type="button"
            label="Scan Receipt 📸" 
            icon="pi pi-camera"
            class="p-button-outlined p-button-success"
            :disabled="submitting || scanning"
            @click="showScanDialog = true"
          />
          <span v-if="scanning" class="text-sm font-medium text-green-600 dark:text-green-400 flex items-center gap-2">
            <i class="pi pi-spin pi-spinner"></i> AI is reading your receipt...
          </span>
        </div>
        <div>
          <label for="title" class="block text-sm font-medium mb-2">Title</label>
          <InputText id="title" v-model="form.title" class="w-full" required />
        </div>
        <div>
          <label for="amount" class="block text-sm font-medium mb-2">Amount</label>
          <InputNumber
            id="amount"
            v-model="form.amount"
            class="w-full"
            mode="decimal"
            :min="0"
            :maxFractionDigits="2"
            required
          />
        </div>
        <div>
          <label for="type" class="block text-sm font-medium mb-2">Type</label>
          <SelectButton
            id="type"
            v-model="form.transaction_type"
            :options="typeOptions"
            optionLabel="label"
            optionValue="value"
            required
          />
        </div>
        <div>
          <label for="category" class="block text-sm font-medium mb-2">Category</label>
          <Dropdown
            id="category"
            v-model="form.category"
            :options="categoryOptions"
            class="w-full"
            placeholder="Select category"
            required
          />
          <InputText
            v-if="form.category === 'Other'"
            v-model="form.customCategoryName"
            class="w-full mt-3"
            placeholder="Custom Category Name"
            :required="form.category === 'Other'"
          />
        </div>
        <div>
          <label for="date" class="block text-sm font-medium mb-2">Date</label>
          <Calendar id="date" v-model="form.date" class="w-full" dateFormat="yy-mm-dd" required />
        </div>
        <div>
          <label for="description" class="block text-sm font-medium mb-2">Description (optional)</label>
          <Textarea id="description" v-model="form.description" class="w-full" rows="3" />
        </div>
        <div v-if="submitError" class="text-red-600 text-sm">{{ submitError }}</div>
        <div class="flex gap-2 justify-end">
          <Button
            type="button"
            label="Cancel"
            severity="secondary"
            @click="showDialog = false"
          />
          <Button type="submit" label="Save" :loading="submitting" />
        </div>
      </form>
    </Dialog>

    <Dialog 
      v-model:visible="showScanDialog" 
      modal 
      header="Upload Receipt" 
      :style="{ width: '90vw', maxWidth: '350px' }"
    >
      <div class="flex flex-col gap-4 py-4">
        <p class="text-surface-600 dark:text-surface-400 text-center mb-2">How would you like to upload your receipt?</p>
        
        <Button 
          label="Take Photo 📸" 
          class="p-button-lg p-button-info w-full justify-center" 
          @click="triggerCamera"
        />
        
        <Button 
          label="Choose File 📁" 
          class="p-button-lg p-button-secondary w-full justify-center" 
          @click="triggerFile"
        />
      </div>
    </Dialog>

    <input 
      type="file" 
      ref="cameraInput" 
      accept="image/*" 
      capture="environment" 
      class="hidden" 
      @change="handleNativeFileUpload" 
    />
    <input 
      type="file" 
      ref="fileInput" 
      accept="image/*" 
      class="hidden" 
      @change="handleNativeFileUpload" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import SelectButton from 'primevue/selectbutton'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const confirm = useConfirm()

const showDialog = ref(false)

// YENİ: Seçim penceresi ve input referansları
const showScanDialog = ref(false)
const cameraInput = ref<HTMLInputElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const form = ref({
  title: '',
  amount: null as number | null,
  transaction_type: 'INCOME' as 'INCOME' | 'EXPENSE',
  category: '',
  customCategoryName: '',
  date: null as Date | null,
  description: '',
})

const typeOptions = [
  { label: 'Income', value: 'INCOME' },
  { label: 'Expense', value: 'EXPENSE' },
]

const categoryOptions = ['Food', 'Rent', 'Salary', 'Freelance', 'Entertainment', 'Transport', 'Other']

const submitError = ref('')
const submitting = ref(false)
const scanning = ref(false)

const API_BASE = 'http://127.0.0.1:8000/api'

const {
  data,
  pending,
  error,
  refresh,
} = await useFetch(`${API_BASE}/transactions/`, {
  headers: {
    Authorization: computed(() => `Bearer ${token.value}`),
  },
})

const tableData = computed(() => (data.value && Array.isArray(data.value) ? data.value : []))

const formatCurrency = (value: number | string) => {
  const num = typeof value === 'number' ? value : Number(value)
  if (Number.isNaN(num)) return value
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(num)
}

const resetForm = () => {
  form.value = {
    title: '',
    amount: null,
    transaction_type: 'INCOME',
    category: '',
    customCategoryName: '',
    date: null,
    description: '',
  }
  submitError.value = ''
}

const getCategoryToSend = () => {
  if (form.value.category === 'Other' && form.value.customCategoryName?.trim()) {
    return form.value.customCategoryName.trim()
  }
  return form.value.category
}

// YENİ: Kamera tetikleyici
const triggerCamera = () => {
  showScanDialog.value = false
  cameraInput.value?.click()
}

// YENİ: Dosya tetikleyici
const triggerFile = () => {
  showScanDialog.value = false
  fileInput.value?.click()
}

// YENİ: Gizli inputlardan gelen dosyayı yakalayan fonksiyon
const handleNativeFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // Dosyayı asıl yükleme fonksiyonuna gönder
  await onReceiptUpload({ files: [file] })

  // Aynı dosyayı tekrar seçebilmek için inputu temizle
  target.value = ''
}

// MEVCUT: Fişi Backend'e gönderip AI sonucunu alan fonksiyon
async function onReceiptUpload(event: { files: File[] }) {
  const file = event.files?.[0]
  if (!file) return

  scanning.value = true
  submitError.value = ''

  try {
    const formData = new FormData()
    formData.append('image', file)

    const result = await $fetch<{ title: string; amount: number; date: string; category: string }>(
      `${API_BASE}/scan-receipt/`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token.value}`,
        },
        body: formData,
      }
    )

    form.value.title = result.title || form.value.title
    form.value.amount = result.amount ?? form.value.amount
    form.value.category = result.category || form.value.category
    form.value.transaction_type = 'EXPENSE'
    
    if (result.date) {
      const [y, m, d] = result.date.split('-').map(Number)
      form.value.date = new Date(y, m - 1, d)
    }
  } catch (err: any) {
    submitError.value = err.data?.detail || 'Failed to analyze receipt. Please try again.'
  } finally {
    scanning.value = false
  }
}

const handleSubmit = async () => {
  const categoryToSend = getCategoryToSend()
  if (!form.value.date || form.value.amount === null || !form.value.category) {
    submitError.value = 'Please fill all required fields'
    return
  }
  if (form.value.category === 'Other' && !form.value.customCategoryName?.trim()) {
    submitError.value = 'Please enter a custom category name'
    return
  }

  submitting.value = true
  submitError.value = ''

  try {
    await $fetch(`${API_BASE}/transactions/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token.value}`,
        'Content-Type': 'application/json',
      },
      body: {
        title: form.value.title,
        amount: form.value.amount,
        transaction_type: form.value.transaction_type,
        category: categoryToSend,
        date: form.value.date.toISOString().split('T')[0],
        description: form.value.description || '',
      },
    })

    showDialog.value = false
    resetForm()
    await refresh()
  } catch (err: any) {
    submitError.value = err.data?.detail || 'Failed to create transaction'
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (row: { id: number; title?: string }) => {
  confirm.require({
    message: `Are you sure you want to delete "${row.title ?? 'this transaction'}"?`,
    header: 'Delete Transaction',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancel',
    acceptLabel: 'Delete',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await $fetch(`${API_BASE}/transactions/${row.id}/`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token.value}` },
        })
        await refresh()
      } catch (e) {
        console.error('Delete failed', e)
      }
    },
  })
}
</script>

<style scoped>
.transactions-table-wrapper :deep(.p-datatable-tbody > tr:hover) {
  background: var(--p-surface-hover);
}
.transactions-table-wrapper :deep(.p-datatable-tbody > tr:nth-child(even)) {
  background: var(--p-surface-50);
}
.dark .transactions-table-wrapper :deep(.p-datatable-tbody > tr:nth-child(even)) {
  background: var(--p-surface-800);
}
</style>