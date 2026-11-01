// Everything the browser remembers about the signed-in person lives behind this one function.
// It is called when someone logs in or out, so one account can never see another account's data
// on a shared phone or computer. (Auto-imported by Nuxt.)

export const purgeLocalUserData = () => {
  // In-memory state (profile, recurring items, notification flags ...)
  try { clearNuxtState() } catch { /* nothing to clear */ }
  try { clearNuxtData() } catch { /* nothing to clear */ }

  if (!import.meta.client) return
  // Older app versions cached API answers in the browser; make sure none of that survives
  if ('caches' in window) caches.delete('sf-api').catch(() => {})
  for (const key of ['user', 'sf_user', 'budgetLimits']) {
    try { localStorage.removeItem(key) } catch { /* private mode */ }
  }
}
