// Dates travel to/from the API as 'YYYY-MM-DD' calendar days.
// toISOString() would convert to UTC first and shift the day (e.g. in Turkey, UTC+3),
// so these helpers work in the user's local time zone. Auto-imported by Nuxt.

export const toApiDate = (date: Date): string => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export const fromApiDate = (value: string): Date => {
  const [y, m, d] = value.split('-').map(Number)
  return new Date(y, m - 1, d)
}
