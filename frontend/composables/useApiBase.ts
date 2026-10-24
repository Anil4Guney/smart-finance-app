// Backend address in one place. Override with the NUXT_PUBLIC_API_BASE
// environment variable (e.g. on Vercel or in docker-compose).
export const useApiBase = () => {
  const root = String(useRuntimeConfig().public.apiBase).replace(/\/+$/, '')
  return {
    API_BASE: `${root}/api`,
    AUTH_BASE: `${root}/auth`,
  }
}
