import { useState } from '#app'
import { computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

// Recurring monthly income/expenses (salary, rent, bills, subscriptions, installments).
// Stored by the backend at /api/subscriptions/ (the name is kept for compatibility).
export type RecurringKind = 'SALARY' | 'RENT' | 'BILL' | 'SUBSCRIPTION' | 'INSTALLMENT' | 'OTHER'

export const RECURRING_KINDS: Record<RecurringKind, { label: string; icon: string; colorClass: string; type: 'INCOME' | 'EXPENSE' | null }> = {
  SALARY: { label: 'Salary', icon: 'pi-wallet', colorClass: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400', type: 'INCOME' },
  RENT: { label: 'Rent', icon: 'pi-home', colorClass: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400', type: 'EXPENSE' },
  BILL: { label: 'Bill', icon: 'pi-bolt', colorClass: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400', type: 'EXPENSE' },
  SUBSCRIPTION: { label: 'Subscription', icon: 'pi-play-circle', colorClass: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400', type: 'EXPENSE' },
  INSTALLMENT: { label: 'Installment', icon: 'pi-credit-card', colorClass: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400', type: 'EXPENSE' },
  OTHER: { label: 'Other', icon: 'pi-replay', colorClass: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300', type: null },
}

// Values the page form works with. amount is in USD (the stored base currency).
export interface RecurringInput {
  name: string
  amount: number
  kind: RecurringKind
  transactionType: 'INCOME' | 'EXPENSE'
  category?: string
  dueDate: Date
  totalInstallments?: number | null
  autoPay?: boolean
}

const fromApi = (sub: any) => {
  const kind = (sub.kind || 'SUBSCRIPTION') as RecurringKind
  const meta = RECURRING_KINDS[kind] || RECURRING_KINDS.OTHER
  return {
    id: sub.id,
    name: sub.name,
    amount: Number(sub.amount),
    kind,
    transactionType: sub.transaction_type as 'INCOME' | 'EXPENSE',
    category: sub.category || '',
    effectiveCategory: sub.effective_category,
    dueDate: fromApiDate(sub.due_date),
    totalInstallments: sub.total_installments as number | null,
    installmentsPaid: sub.installments_paid as number,
    remainingInstallments: sub.remaining_installments as number | null,
    isActive: sub.is_active as boolean,
    autoPay: sub.auto_pay as boolean,
    icon: meta.icon,
    colorClass: meta.colorClass,
  }
}

const toApi = (sub: RecurringInput) => ({
  name: sub.name,
  amount: sub.amount,
  kind: sub.kind,
  transaction_type: sub.transactionType,
  category: sub.category || '',
  due_date: toApiDate(sub.dueDate),
  total_installments: sub.kind === 'INSTALLMENT' ? sub.totalInstallments : null,
  auto_pay: sub.autoPay ?? true,
  icon: RECURRING_KINDS[sub.kind]?.icon,
})

export const useSubscriptions = () => {
  const { token } = useAuth()
  const { API_BASE } = useApiBase()
  const { formatCurrency } = useCurrency()
  const authHeaders = () => ({ Authorization: `Bearer ${token.value}` })

  const subscriptions = useState<ReturnType<typeof fromApi>[]>('global_subscriptions', () => [])
  const dismissedNotifs = useState<number[]>('dismissed_notifs', () => [])
  const readNotifs = useState<number[]>('read_notifs', () => [])

  const loadSubscriptions = async () => {
    if (!token.value) return
    try {
      const data = await $fetch<any[]>(`${API_BASE}/subscriptions/`, { headers: authHeaders() })
      subscriptions.value = data.map(fromApi)
    } catch (error) {
      console.error('Recurring items could not be loaded:', error)
    }
  }

  // add/update throw on failure so the page can show the server's message
  const addSubscription = async (sub: RecurringInput) => {
    const created = await $fetch<any>(`${API_BASE}/subscriptions/`, {
      method: 'POST',
      headers: authHeaders(),
      body: { ...toApi(sub), is_active: true },
    })
    // Reload: a plan whose first date is today gets billed right away
    await loadSubscriptions()
    return fromApi(created)
  }

  const updateSubscription = async (id: number, sub: RecurringInput) => {
    await $fetch<any>(`${API_BASE}/subscriptions/${id}/`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: toApi(sub),
    })
    await loadSubscriptions()
  }

  const deleteSubscription = async (id: number) => {
    try {
      await $fetch(`${API_BASE}/subscriptions/${id}/`, {
        method: 'DELETE',
        headers: authHeaders(),
      })
      subscriptions.value = subscriptions.value.filter(s => s.id !== id)
    } catch (error) {
      console.error('Recurring item could not be deleted:', error)
    }
  }

  const getDaysLeft = (targetDate: string | Date) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const target = new Date(targetDate)
    target.setHours(0, 0, 0, 0)
    const diffTime = target.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  const getRelativeDateString = (date: string | Date) => {
    const days = getDaysLeft(date)
    if (days === 0) return 'Due Today'
    if (days === 1) return 'Due Tomorrow'
    if (days < 0) return `Overdue by ${Math.abs(days)} days`
    return `In ${days} days`
  }

  const notifications = computed(() => {
    return subscriptions.value
      // Only upcoming payments need a reminder (not salary, not finished plans)
      .filter(sub => sub.isActive && sub.transactionType === 'EXPENSE')
      .filter(sub => getDaysLeft(sub.dueDate) <= 1)
      .filter(sub => !dismissedNotifs.value.includes(sub.id))
      .map(sub => ({
        id: sub.id,
        title: `${sub.name} Payment`,
        message: `${sub.name}: ${formatCurrency(sub.amount)} is ${getRelativeDateString(sub.dueDate).toLowerCase()}`,
        icon: sub.icon,
        colorClass: sub.colorClass,
        isRead: readNotifs.value.includes(sub.id)
      }))
  })

  const unreadCount = computed(() => notifications.value.filter(n => !n.isRead).length)

  const dismissNotification = (id: number) => {
    if (!dismissedNotifs.value.includes(id)) dismissedNotifs.value.push(id)
  }

  const markAllAsRead = () => {
    notifications.value.forEach(notif => {
      if (!readNotifs.value.includes(notif.id)) readNotifs.value.push(notif.id)
    })
  }

  return {
    subscriptions,
    notifications,
    unreadCount,
    getDaysLeft,
    getRelativeDateString,
    loadSubscriptions,
    addSubscription,
    updateSubscription, // DIŞARI AKTARDIK
    deleteSubscription,
    dismissNotification,
    markAllAsRead
  }
}