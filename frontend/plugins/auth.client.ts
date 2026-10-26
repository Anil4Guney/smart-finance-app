export default defineNuxtPlugin(() => {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  // Pages anyone may open without an account
  const publicPages = ['/privacy']

  router.beforeEach((to, from, next) => {
    if (publicPages.includes(to.path)) return next()

    if (to.path === '/login' || to.path === '/register') {
      if (isAuthenticated.value) {
        return next('/')
      }
      return next()
    }

    if (!isAuthenticated.value) {
      return next('/login')
    }

    next()
  })
})
