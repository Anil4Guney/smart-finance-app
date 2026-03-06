export default defineNuxtPlugin(() => {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  router.beforeEach((to, from, next) => {
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
