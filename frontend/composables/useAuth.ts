export const useAuth = () => {
  const token = useCookie<string | null>('auth_token', {
    default: () => null,
    maxAge: 60 * 60 * 24, // 1 gün
  })

  const user = useState<any>('auth_user', () => null)
  const isAuthenticated = computed(() => !!token.value)


  const { AUTH_BASE } = useApiBase()

  const fetchUser = async () => {
    if (!token.value) return
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
      await fetchUser() 
      return { success: true }
    } catch (error: any) {
      const wrongCredentials = error?.response?.status === 401
      return {
        success: false,
        error: wrongCredentials ? 'Kullanıcı adı veya şifre hatalı.' : (error.data?.detail || 'Giriş yapılamadı. Lütfen tekrar dene.'),
      }
    }
  }

  const register = async (username: string, password: string, email: string, first_name: string, last_name: string) => {
    try {
      // 1. Önce Django'ya (Djoser) Kayıt Ol
      await $fetch(`${AUTH_BASE}/users/`, {
        method: 'POST',
        body: { username, password, email },
      })
      
      // 2. Anında Otomatik Giriş Yap
      const loginResult = await login(username, password)

      // 3. Giriş başarılıysa anında Ad ve Soyadı veritabanına kaydet (Sihir burada!)
      if (loginResult.success && token.value) {
        await $fetch(`${AUTH_BASE}/users/me/`, {
          method: 'PATCH',
          headers: { Authorization: `Bearer ${token.value}` },
          body: { first_name, last_name }
        })
        await fetchUser() 
      }

      return loginResult
    } catch (error: any) {
      // Hatayı net görebilmek için yakalama kodunu geliştirdim
      const errMsg = error.data?.username?.[0] || error.data?.email?.[0] || error.data?.password?.[0] || 'Kayıt oluşturulamadı. Lütfen tekrar dene.'
      return { success: false, error: errMsg }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null 
    if (import.meta.client) {
      // The offline copy of this user's data must not outlive the session
      if ('caches' in window) caches.delete('sf-api').catch(() => {})
      localStorage.removeItem('user')
      localStorage.removeItem('sf_user')
      localStorage.removeItem('budgetLimits') 
      window.location.href = '/login'
    }
  }

  if (token.value && !user.value) {
    fetchUser()
  }

  return { token, user, isAuthenticated, login, register, logout, fetchUser }
}