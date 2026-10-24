// Monthly category budget limits, stored on the backend (/api/budgets/).
// Amounts are in the base currency (USD), like transactions.
type BudgetMap = Record<string, number>

const LEGACY_STORAGE_KEY = 'budgetLimits'

export const useBudgets = () => {
  const { token } = useAuth()
  const { API_BASE } = useApiBase()
  const authHeaders = () => ({ Authorization: `Bearer ${token.value}` })

  const toMap = (rows: { category: string; limit_amount: string | number }[]): BudgetMap =>
    Object.fromEntries(rows.map(r => [r.category, Number(r.limit_amount)]))

  const saveBudgets = async (limits: Record<string, number | null>): Promise<BudgetMap> => {
    const rows = await $fetch<any[]>(`${API_BASE}/budgets/sync/`, {
      method: 'PUT',
      headers: authHeaders(),
      body: { limits },
    })
    return toMap(rows)
  }

  // Older versions kept budgets only in this browser. Move them to the server once.
  const migrateLegacyBudgets = async (): Promise<BudgetMap | null> => {
    if (!import.meta.client) return null
    let legacy: Record<string, number | null> | null = null
    try {
      const raw = localStorage.getItem(LEGACY_STORAGE_KEY)
      legacy = raw ? JSON.parse(raw) : null
    } catch {
      legacy = null
    }
    if (!legacy || !Object.values(legacy).some(v => v && v > 0)) return null
    const saved = await saveBudgets(legacy)
    localStorage.removeItem(LEGACY_STORAGE_KEY)
    return saved
  }

  const fetchBudgets = async (): Promise<BudgetMap> => {
    if (!token.value) return {}
    const rows = await $fetch<any[]>(`${API_BASE}/budgets/`, { headers: authHeaders() })
    if (rows.length === 0) {
      const migrated = await migrateLegacyBudgets().catch(() => null)
      if (migrated) return migrated
    }
    return toMap(rows)
  }

  return { fetchBudgets, saveBudgets }
}
