// Silent session renewal for every API call.
//
// The access token only lives 30 minutes. When a request comes back 401 we get a new one with the
// refresh token and repeat the request once. If the refresh token is rejected too, the session is
// over and we go to the login page. If we simply cannot reach the server we keep the session.
//
// This wraps the global $fetch, which useFetch and all pages use. The file name sorts before
// auth.client.ts so the wrapper is in place before anything calls the API.

export default defineNuxtPlugin(() => {
  const original = globalThis.$fetch

  const isAuthEndpoint = (request: unknown) => String(request).includes('/auth/jwt/')

  const authHeader = (headers: unknown): string | null => {
    try {
      return new Headers(headers as HeadersInit).get('Authorization')
    } catch {
      return null
    }
  }

  // Filled in after useAuth() exists (it calls the API once while it is created)
  let renew: (() => Promise<string | null | undefined>) | undefined
  let endSession: (() => void) | undefined
  let currentToken: (() => string | null | undefined) | undefined

  const wrapped = (async (request: any, options: any = {}) => {
    try {
      return await original(request, options)
    } catch (error: any) {
      const unauthorized = error?.response?.status === 401
      if (!unauthorized || !authHeader(options.headers) || isAuthEndpoint(request) || !renew) throw error

      // Another request may have renewed the token while this one was in flight: just use it
      const sent = authHeader(options.headers)
      const latest = currentToken?.()
      const fresh = latest && sent !== `Bearer ${latest}` ? latest : await renew()
      if (fresh === null) {
        endSession?.()
        throw error
      }
      if (!fresh) throw error // offline: keep the session and report the failure

      const headers = new Headers(options.headers)
      headers.set('Authorization', `Bearer ${fresh}`)
      return original(request, { ...options, headers })
    }
  }) as typeof $fetch
  Object.assign(wrapped, original) // keeps $fetch.raw and $fetch.create
  globalThis.$fetch = wrapped

  const { token, refreshAccessToken, logout } = useAuth()
  renew = refreshAccessToken
  endSession = logout
  currentToken = () => token.value
})
