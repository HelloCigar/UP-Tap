
export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const session = await getUserSession(event)
    if (session.user){
      const result = await $fetch("http://127.0.0.1:8000/api/verify", {
        method: "POST",
        body: body,
        headers: {
          "Authorization": `Bearer ${session.user.auth_token}`
        },
      }
    )

      return result
    }

    return null
  })
  