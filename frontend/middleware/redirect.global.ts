export default defineNuxtRouteMiddleware((to, from) => {
  const { loggedIn } = useUserSession()
  if (to.path !== '/login' && to.path !== '/signup' && !loggedIn.value) {
    return navigateTo('/login')
  }
})
