
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    if (session.secure){
      const result = await $fetch<Teacher>("http://127.0.0.1:8000/auth/users/me/", {
        method: "GET",
        headers: {
          "Authorization": `Token ${session.secure.auth_token}`
        },
      }
    )
      return result
    }

    return {"error": "failed getting the subjects"}
  })
  