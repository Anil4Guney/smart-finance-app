export const useAuth = () => {
  const token = useCookie<string | null>('auth_token', {
    default: () => null,
    maxAge: 60 * 60 * 24, // 1 gün
  })

  const user = useState<any>('auth_user', () => null)
  const isAuthenticated = computed(() => !!token.value)

  // DOĞRU ADRES: /api YOK! Sadece /auth/
  const AUTH_BASE = 'http://127.0.0.1:8000/auth'

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const response = await $fetch<any>(`${AUTH_BASE}/users/me/`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = response
    } catch (error) {
      console.error('Kullanıcı bilgileri çekilemedi:', error)
      user.value = null
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
      return { success: false, error: error.data?.detail || 'Login failed' }
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
      const errMsg = error.data?.username?.[0] || error.data?.email?.[0] || error.data?.password?.[0] || 'Registration failed'
      return { success: false, error: errMsg }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null 
    if (import.meta.client) {
      localStorage.removeItem('user')
      localStorage.removeItem('budgetLimits') 
      window.location.href = '/login'
    }
  }

  if (token.value && !user.value) {
    fetchUser()
  }

  return { token, user, isAuthenticated, login, register, logout, fetchUser }
}