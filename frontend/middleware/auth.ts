export default defineNuxtRouteMiddleware((to, from) => {
  const { loggedIn } = useUserSession()
  
  if(!loggedIn.value) {
    return navigateTo('/login')
  }

  if(to.path === '/login' || to.path === '/signup') {
    if(loggedIn.value) {
      return navigateTo('/dashboard')
    }
  }
})
