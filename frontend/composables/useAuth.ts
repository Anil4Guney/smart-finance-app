// Session handling.
// - auth_token: short-lived access token (30 min), sent with every API request
// - refresh_token: used silently to get a new access token (14 days, rotated on every use)
// The api-auth plugin does the silent refresh; this file owns the cookies and login/logout.

const SESSION_SECONDS = 60 * 60 * 24 * 14

const sessionCookieOptions = () => ({
  default: () => null,
  maxAge: SESSION_SECONDS,
  path: '/',
  sameSite: 'lax' as const,
  // Only sent over HTTPS in production (localhost development uses plain http)
  secure: import.meta.client && location.protocol === 'https:',
})

// One refresh at a time, and one profile request at a time, even if many components ask together
let refreshing: Promise<string | null | undefined> | null = null
let loadingUser: Promise<void> | null = null

export const useAuth = () => {
  // The cookie outlives the access token on purpose: when the access token has expired the
  // app refreshes it silently instead of throwing the user back to the login page.
  const token = useCookie<string | null>('auth_token', sessionCookieOptions())
  const refreshToken = useCookie<string | null>('refresh_token', sessionCookieOptions())

  const user = useState<any>('auth_user', () => null)
  const isAuthenticated = computed(() => !!token.value || !!refreshToken.value)

  const { AUTH_BASE } = useApiBase()

  /**
   * Gets a new access token. Resolves to:
   *  - the new token on success
   *  - null when the session is really over (refresh token rejected)
   *  - undefined when we just could not reach the server (offline): keep the session
   */
  const refreshAccessToken = (): Promise<string | null | undefined> => {
    if (!refreshToken.value) return Promise.resolve(null)
    refreshing ??= (async () => {
      try {
        const response = await $fetch<{ access: string; refresh?: string }>(`${AUTH_BASE}/jwt/refresh/`, {
          method: 'POST',
          body: { refresh: refreshToken.value },
        })
        token.value = response.access
        if (response.refresh) refreshToken.value = response.refresh
        return response.access
      } catch (error: any) {
        const status = error?.response?.status
        return status === 400 || status === 401 ? null : undefined
      } finally {
        refreshing = null
      }
    })()
    return refreshing
  }

  const fetchUser = (): Promise<void> => {
    if (!token.value && !refreshToken.value) return Promise.resolve()
    loadingUser ??= loadUser().finally(() => { loadingUser = null })
    return loadingUser
  }

  const loadUser = async () => {
    try {
      const response = await $fetch<any>(`${AUTH_BASE}/users/me/`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = response
      try { localStorage.setItem('sf_user', JSON.stringify(response)) } catch { /* private mode */ }
    } catch (error: any) {
      console.error('Kullanıcı bilgileri çekilemedi:', error)
      if (error?.response?.status === 401) {
        user.value = null
        return
      }
      // Offline or server asleep: show the last known profile instead of an empty header
      try {
        const saved = localStorage.getItem('sf_user')
        user.value = saved ? JSON.parse(saved) : null
      } catch {
        user.value = null
      }
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await $fetch<{ access: string; refresh: string }>(
        `${AUTH_BASE}/jwt/create/`,
        {
          method: 'POST',
          body: { username, password },
        }
      )
      token.value = response.access
      refreshToken.value = response.refresh
      await fetchUser()
      return { success: true }
    } catch (error: any) {
      const status = error?.response?.status
      let message = translateApiError(error.data?.detail, 'Giriş yapılamadı. Lütfen tekrar dene.')
      if (status === 401) message = 'Kullanıcı adı veya şifre hatalı.'
      if (status === 429) message = 'Çok fazla deneme yapıldı. Biraz bekleyip tekrar dene.'
      return { success: false, error: message }
    }
  }

  const register = async (username: string, password: string, email: string, first_name: string, last_name: string) => {
    try {
      await $fetch(`${AUTH_BASE}/users/`, {
        method: 'POST',
        body: { username, password, email, first_name, last_name },
      })
      // Sign in right away
      return await login(username, password)
    } catch (error: any) {
      const data = error?.data || {}
      const first = (value: unknown) => (Array.isArray(value) ? value[0] : value)
      const message =
        first(data.username) || first(data.email) || first(data.password) ||
        first(data.first_name) || first(data.last_name) || first(data.non_field_errors) ||
        'Kayıt oluşturulamadı. Lütfen tekrar dene.'
      return { success: false, error: String(message) }
    }
  }

  const logout = () => {
    const refresh = refreshToken.value
    token.value = null
    refreshToken.value = null
    user.value = null
    if (import.meta.client) {
      // Make the refresh token useless on the server too. keepalive lets it finish while we navigate.
      if (refresh) {
        fetch(`${AUTH_BASE}/jwt/logout/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh }),
          keepalive: true,
        }).catch(() => {})
      }
      // The offline copy of this user's data must not outlive the session
      if ('caches' in window) caches.delete('sf-api').catch(() => {})
      localStorage.removeItem('user')
      localStorage.removeItem('sf_user')
      localStorage.removeItem('budgetLimits')
      window.location.href = '/login'
    }
  }

  if ((token.value || refreshToken.value) && !user.value) {
    fetchUser()
  }

  return { token, refreshToken, user, isAuthenticated, login, register, logout, fetchUser, refreshAccessToken }
}
