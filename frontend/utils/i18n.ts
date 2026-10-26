// Turkish labels. Stored values (categories, types) stay English keys; only the display is translated.
// Auto-imported by Nuxt.

export const LOCALE = 'tr-TR'

const CATEGORY_LABELS: Record<string, string> = {
  Food: 'Yemek',
  Rent: 'Kira',
  Salary: 'Maaş',
  Freelance: 'Serbest Gelir',
  Entertainment: 'Eğlence',
  Transport: 'Ulaşım',
  Bills: 'Faturalar',
  Installments: 'Taksitler',
  Savings: 'Birikim',
  Other: 'Diğer',
}

// Order shown in category pickers
export const CATEGORY_KEYS = ['Food', 'Rent', 'Bills', 'Transport', 'Entertainment', 'Salary', 'Freelance', 'Installments', 'Savings', 'Other']

export const categoryLabel = (key: string): string => CATEGORY_LABELS[key] || key

export const categoryChoices = (keys: string[] = CATEGORY_KEYS) =>
  keys.map(value => ({ value, label: categoryLabel(value) }))

export const MONTH_NAMES_SHORT = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']

// 'YYYY-MM-DD' or Date -> "24 Eki 2026"
export const formatDateTR = (value: string | Date): string => {
  const d = typeof value === 'string' ? fromApiDate(value) : value
  return d.toLocaleDateString(LOCALE, { day: 'numeric', month: 'short', year: 'numeric' })
}

export const formatDayMonthTR = (value: string | Date): string => {
  const d = typeof value === 'string' ? fromApiDate(value) : value
  return d.toLocaleDateString(LOCALE, { day: 'numeric', month: 'short' })
}

export const formatMonthYearTR = (year: number, monthIndex: number): string =>
  new Date(year, monthIndex, 1).toLocaleDateString(LOCALE, { month: 'long', year: 'numeric' })

// A few server messages come from libraries that only speak English
const API_ERRORS: Record<string, string> = {
  'Invalid password.': 'Şifre hatalı.',
  'Invalid token.': 'Oturum geçersiz. Lütfen tekrar giriş yap.',
  'Authentication credentials were not provided.': 'Oturum süresi doldu. Lütfen tekrar giriş yap.',
  'Request was throttled.': 'Çok fazla istek yapıldı. Biraz bekleyip tekrar dene.',
}

export const translateApiError = (message: unknown, fallback = 'Bir hata oluştu. Lütfen tekrar dene.'): string => {
  const text = String(message ?? '').trim()
  if (!text) return fallback
  const known = Object.keys(API_ERRORS).find(key => text.startsWith(key))
  if (known) return API_ERRORS[known]
  if (/^Expected available in \d+ second/i.test(text)) return 'Çok fazla istek yapıldı. Biraz bekleyip tekrar dene.'
  return text
}
