// Monthly category budget limits, stored on the backend (/api/budgets/).
// Amounts are in the base currency (USD), like transactions.
type BudgetMap = Record<string, number>

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

  const fetchBudgets = async (): Promise<BudgetMap> => {
    if (!token.value) return {}
    const rows = await $fetch<any[]>(`${API_BASE}/budgets/`, { headers: authHeaders() })
    return toMap(rows)
  }

  return { fetchBudgets, saveBudgets }
}
