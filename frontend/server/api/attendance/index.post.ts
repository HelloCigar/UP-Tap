export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const query = await getQuery(event)
    const body = await readBody(event)
    if (session.secure){
      const result = await $fetch<AttendanceRecord[]>("http://127.0.0.1:8000/api/attendance/all", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${session.secure.auth_token}`
        },
        query: query,
        body: body
      }
    )
      return result
    }
    return sendRedirect(event, '/login')
})