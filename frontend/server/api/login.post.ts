export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    try {
      const result = await $fetch<{ auth_token: string }>(`http://127.0.0.1:8000/auth/token/login/`, {
        method: "POST",
        body: body,
        }
      )
      if (result) {
        const session = await setUserSession(event, {
          user: {
            auth_token: "SuperSecret :>"
          },
          secure: {
            auth_token: result.auth_token
          }
        })
        return result
      }
    }
    catch(err) {
      return {"error": true, "message": `${err.data.non_field_errors[0]} Your account may not be activated yet.`};
    }
  })
  