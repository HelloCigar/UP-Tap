export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const result = await $fetch<{ auth_token: string }>(`http://127.0.0.1:8000/auth/token/login/`, {
          method: "POST",
          body: body,
        }
    )
    if (result) {
      await setUserSession(event, {
        user: {
          auth_token: "SuperSecret :>"
        },
        secure: {
          auth_token: result.auth_token
        }
      })
      return result
    }

    return null
  })
  