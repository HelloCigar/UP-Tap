
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const body = await readBody(event)
    const { student_id } = body
    if (session.secure){
      const result = await $fetch<{success: boolean}>(`http://127.0.0.1:8000/api/student/${student_id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
      }
    )
      return result
    }

    return sendRedirect(event, '/login')
  })
  