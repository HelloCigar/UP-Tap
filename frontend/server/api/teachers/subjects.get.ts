
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    if (session.secure){
      const result = await $fetch("http://127.0.0.1:8000/api/teachers/subjects", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
      }
    )
      return result
    }

    return {"error": "failed getting the subjects"}
  })
  