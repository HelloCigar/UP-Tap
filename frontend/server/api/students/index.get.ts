
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const query = await getQuery(event)
    if (session.secure){
      const result = await $fetch("http://127.0.0.1:8000/api/student/all", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
        query: query
      }
    )

      return result
    }

    return {"error": "failed getting student list"}
  })
  