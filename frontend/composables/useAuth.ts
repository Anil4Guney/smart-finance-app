export const useAuth = () => {
  const token = useCookie<string | null>('auth_token', {
    default: () => null,
    maxAge: 60 * 60 * 24, // 1 day
  })

  const isAuthenticated = computed(() => !!token.value)

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
      return { success: true }
    } catch (error: any) {
      return { success: false, error: error.data?.detail || 'Login failed' }
    }
  }

  const register = async (username: string, password: string, email?: string) => {
    try {
      await $fetch('http://127.0.0.1:8000/auth/users/', {
        method: 'POST',
        body: {
          username,
          password,
          email,
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
    navigateTo('/login')
  }

  return {
    token,
    isAuthenticated,
    login,
    register,
    logout,
  }
}
