export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    if (session.secure){
      const result = await $fetch<{ auth_token: string }>("http://127.0.0.1:8000/auth/token/logout/", {
        method: "POST",
        headers: {
          "Authorization": `Token ${session.secure.auth_token}`
        },
      }
    )
      
    await clearUserSession(event)

    return result
    }
})
  