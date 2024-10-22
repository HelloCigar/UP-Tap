
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const body = await readBody(event)
    const query = await getQuery(event)
    if (session.secure){
      const result = await $fetch("http://127.0.0.1:8000/api/student/register", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
        body: body,
        query: query
      }
    )
      return result
    }

    return {"error": "failed to register student"}
  })
  