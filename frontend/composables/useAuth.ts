export const useAuth = () => {
  const token = useCookie<string | null>('auth_token', {
    default: () => null,
    maxAge: 60 * 60 * 24, // 1 day
  })

  // YENİ: Kullanıcı bilgilerini tutacağımız global state (hafıza)
  const user = useState<any>('auth_user', () => null)

  const isAuthenticated = computed(() => !!token.value)

  // YENİ: Token ile Backend'den aktif kullanıcının tüm bilgilerini (Ad, Soyad, Email) çeker
  const fetchUser = async () => {
    if (!token.value) return
    try {
      const response = await $fetch<any>('http://127.0.0.1:8000/auth/users/me/', {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })
      user.value = response // Gelen veriyi (first_name, last_name, vb.) hafızaya yaz
    } catch (error) {
      console.error('Kullanıcı bilgileri çekilemedi:', error)
      user.value = null
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await $fetch<{ access: string; refresh: string }>(
        'http://127.0.0.1:8000/auth/jwt/create/',
        {
          method: 'POST',
          body: {
            username,
            password,
          },
        }
      )
      token.value = response.access
      
      // YENİ: Giriş başarılı olunca kullanıcının adını/soyadını hemen çek!
      await fetchUser()
      
      return { success: true }
    } catch (error: any) {
      return { success: false, error: error.data?.detail || 'Login failed' }
    }
  }

  // YENİ: Kayıt olurken Ad (first_name) ve Soyad (last_name) de istiyoruz
  const register = async (username: string, password: string, email: string, first_name: string, last_name: string) => {
    try {
      await $fetch('http://127.0.0.1:8000/auth/users/', {
        method: 'POST',
        body: {
          username,
          password,
          email,
          first_name, // Backend'e adı gönder
          last_name,  // Backend'e soyadı gönder
        },
      })
      // Auto login after registration
      return await login(username, password)
    } catch (error: any) {
      return {
        success: false,
        error: error.data?.username?.[0] || error.data?.password?.[0] || 'Registration failed',
      }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null // Çıkış yapınca kullanıcı verisini de temizle
    navigateTo('/login')
  }

  // Sayfa ilk yüklendiğinde token varsa kullanıcıyı getir (F5 atınca isim kaybolmasın diye)
  if (token.value && !user.value) {
    fetchUser()
  }

  return {
    token,
    user, // Bileşenlere (Header, Profile vb.) user bilgisini açıyoruz
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser
  }
}