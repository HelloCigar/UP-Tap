
export default defineEventHandler(async (event) => {
    const session = await getUserSession(event)
    const id = getRouterParam(event, 'id')
    
    if (!session || !session.secure) {
        return sendRedirect(event, '/login')
    }
    const result = await $fetch(`http://127.0.0.1:8000/api/student/${id}`, {
    method: "GET",
    headers: {
        "Authorization": `Bearer ${session.secure.auth_token}`
    },})
    return result
})
  