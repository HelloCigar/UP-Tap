export default defineNuxtRouteMiddleware((to, from) => {
  const {ready, loggedIn} = useUserSession()
  const user = useCookie('user')
  if(ready.value) {
    if(!user.value) {
    return navigateTo('/login')
    }
  }
})
